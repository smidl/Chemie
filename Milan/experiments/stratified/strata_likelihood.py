#!/usr/bin/env python
"""Rank-free: how probable is the *recorded* product under the model?

The stratified evaluation says AFM's top-1 deficit on long steps is a ranking
effect -- the recorded product is in its candidate list at top-3 (0.962 against
0.976 for the entrywise model) but not at top-1 (0.778 against 0.870). A ranking
rule cannot be blamed or cleared by a metric that is itself a ranking. This one
is not: it teacher-forces the recorded step's own move sequence (the order the
training pipeline computes for it) and reads the trajectory log-probability
directly, then compares it with the model's own best sampled trajectory.

Per stratum it reports

* ``p_decision``: the geometric-mean probability per decision of the recorded
  route, ``exp(logp / (moves + 1))`` -- comparable across strata, where the raw
  log-probability is not, since a longer route sums more negative terms.
* ``best_is_recorded``: the fraction of steps whose highest-scoring sampled
  trajectory ends on the recorded product matrix. Matrices are compared
  entry-wise, so no canonicalisation or SMILES round-trip enters.
* ``margin``: the model's best sampled trajectory score minus the recorded
  route's. Positive means the model prefers a different route; a small positive
  margin is a near-tie a ranking rule can lose, a large one is a real preference.

Run inside the AFM checkout::

    python strata_likelihood.py --ckpt <best.ckpt> --files <strata>/test_m6plus.txt \
        --limit 1000 --out strata_likelihood.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from statistics import median

import torch

import compat_flower_cons  # noqa: F401  aliases the pre-rename checkpoint module
import hydra
import models  # noqa: F401  registers the model classes
from data import read_steps
from models.afm import NUM_MOVES, CollateAFM, scatter_moves
from models.flower import _SAMPLE_BUDGET


def load(ckpt_path, emb_dim, enc_filter_size, config_dir):
    with hydra.initialize_config_dir(config_dir=config_dir, version_base=None):
        cfg = hydra.compose(config_name="default_eval", overrides=[
            "model=afm", f"model.emb_dim={emb_dim}",
            f"model.enc_filter_size={enc_filter_size}", "model.decode=sample",
        ])
    model = hydra.utils.instantiate(cfg.model)
    state = torch.load(ckpt_path, map_location="cpu", weights_only=False)["state_dict"]
    model.load_state_dict(state, strict=True)
    model.eval()
    return model, CollateAFM()


@torch.no_grad()
def recorded_route_logp(model, batch):
    """Teacher-forced trajectory log-probability of the recorded move sequence."""
    source = model._source(batch)
    moves, counts = batch["moves"], batch["move_count"]
    b, n, _ = source.shape
    state = source.clone()
    total = torch.zeros(b, device=source.device)
    step = torch.zeros(b, device=source.device)
    for position in range(moves.shape[1]):
        log_probs = model._score(batch["atom_ids"], batch["lengths"], state, source, step)
        mv = moves[:, position]
        index = (mv[:, 0] * n + mv[:, 1]) * n + mv[:, 2]
        live = position < counts
        total = total + torch.where(live, log_probs.gather(1, index[:, None]).squeeze(1),
                                    torch.zeros_like(total))
        scatter_moves(state, mv[:, 0], mv[:, 1], mv[:, 2], live)
        step = step + live.float()
    log_probs = model._score(batch["atom_ids"], batch["lengths"], state, source, step)
    return total + log_probs[:, NUM_MOVES * n * n], counts


@torch.no_grad()
def best_sampled(model, batch, width):
    """Highest-scoring sampled trajectory per step: its score, and whether its
    endpoint is the recorded product matrix (compared entry-wise).

    A roll-out holds ``rows * width`` states and their O(N^2) attention at once,
    so rows are processed in groups small enough to bound that product -- the
    same budget rule ``mapped_candidates`` applies internally, which calling
    ``_rollout`` directly would otherwise skip.
    """
    source = model._source(batch)
    b, n, _ = source.shape
    group = max(1, _SAMPLE_BUDGET // (width * n * n))
    scores, hits = [], []
    target, lengths = batch["tgt"], batch["lengths"]
    for start in range(0, b, group):
        stop = min(start + group, b)
        state, score, _ = model._rollout(
            batch["atom_ids"][start:stop], lengths[start:stop], source[start:stop], width
        )
        rows = stop - start
        score = score.view(rows, width)
        state = state.view(rows, width, *state.shape[-2:])
        best = score.argmax(dim=1)
        index = torch.arange(rows, device=score.device)
        endpoint = state[index, best]
        scores.append(score[index, best].cpu())
        for k in range(rows):
            size = int(lengths[start + k])
            hits.append(torch.equal(endpoint[k, :size, :size].long(),
                                    target[start + k, :size, :size].long().to(endpoint.device)))
    return torch.cat(scores), torch.tensor(hits)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--limit", type=int, default=1000)
    ap.add_argument("--width", type=int, default=10)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--emb_dim", type=int, default=128)
    ap.add_argument("--enc_filter_size", type=int, default=512)
    ap.add_argument("--config_dir", default=str(Path.cwd() / "configs"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    model, collate = load(args.ckpt, args.emb_dim, args.enc_filter_size, args.config_dir)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)

    out = {}
    for path in args.files:
        name = Path(path).stem
        steps = read_steps(path, limit=args.limit)
        records = []
        unusable = 0
        for step in steps:
            try:
                rec = collate.featurize(step)
            except Exception:  # noqa: BLE001
                unusable += 1
                continue
            # A step whose move multiset admits no order carries no route to
            # teacher-force; counted, not silently dropped.
            if not rec.get("usable", True):
                unusable += 1
                continue
            records.append(rec)

        per_decision, margins, hits, n_moves = [], [], 0, []
        for start in range(0, len(records), args.batch):
            chunk = records[start:start + args.batch]
            batch = collate.collate(chunk)
            batch = {k: (v.to(device) if torch.is_tensor(v) else v) for k, v in batch.items()}
            logp, counts = recorded_route_logp(model, batch)
            best, hit = best_sampled(model, batch, args.width)
            decisions = (counts + 1).float()
            per_decision.extend(torch.exp(logp / decisions).cpu().tolist())
            margins.extend((best - logp.cpu()).tolist())
            n_moves.extend(counts.cpu().tolist())
            hits += int(hit.sum())

        n = len(per_decision) or 1
        out[name] = {
            "n_scored": len(per_decision), "n_unusable": unusable,
            "mean_moves": round(sum(n_moves) / n, 2),
            "p_decision_mean": round(sum(per_decision) / n, 4),
            "p_decision_median": round(median(per_decision), 4) if per_decision else None,
            "best_is_recorded": round(hits / n, 4),
            "margin_mean": round(sum(margins) / n, 3),
            "margin_median": round(median(margins), 3) if margins else None,
            "margin_under_1nat": round(sum(1 for m in margins if m < 1.0) / n, 4),
        }
        print(name, json.dumps(out[name]))
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
