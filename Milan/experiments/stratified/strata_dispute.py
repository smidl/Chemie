#!/usr/bin/env python
"""Separate two preferences the margin conflates: which *product*, and which
*route* to it.

`strata_likelihood.py` found a median 0.89-nat margin at six or more moves
between the model's best sampled trajectory and the recorded step's own route.
That margin has two components and they mean opposite things:

* **order** -- the model prefers a different order of the *same* moves, ending
  on the recorded product. Harmless: the product is right, and it is the order
  ambiguity of Limitation (ii).
* **product** -- the model's best trajectory ends somewhere else. That is a
  disagreement about the chemistry.

Splitting them needs the best sampled trajectory *that reaches the recorded
product*, which this computes by keeping every sampled trajectory's endpoint and
its score:

    margin_order   = logp(best trajectory reaching the recorded product)
                     - logp(the recorded route, teacher-forced)
    margin_product = logp(best trajectory overall)
                     - logp(best trajectory reaching the recorded product)

It also dumps the disputed cases -- best trajectory ends elsewhere -- with both
move sequences, so `experiments/draw_arrows/` can render them for a chemist.

    python strata_dispute.py --ckpt <best.ckpt> --files <strata>/test_m6plus.txt \
        --limit 300 --out dispute.json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median

import torch

import compat_flower_cons  # noqa: F401
import hydra
import models  # noqa: F401
from data import read_steps
from models.afm import NUM_MOVES, CollateAFM, _sample_step, scatter_moves

KIND_NAMES = ["LONE_TO_BOND", "BOND_TO_LONE", "HOMOLYSIS", "COLLIGATION"]


def load(ckpt_path, emb_dim, enc_filter_size, config_dir):
    with hydra.initialize_config_dir(config_dir=config_dir, version_base=None):
        cfg = hydra.compose(config_name="default_eval", overrides=[
            "model=afm", f"model.emb_dim={emb_dim}",
            f"model.enc_filter_size={enc_filter_size}", "model.decode=sample",
        ])
    model = hydra.utils.instantiate(cfg.model)
    model.load_state_dict(torch.load(ckpt_path, map_location="cpu", weights_only=False)["state_dict"],
                          strict=True)
    return model.eval(), CollateAFM()


@torch.no_grad()
def recorded_logp(model, batch):
    source = model._source(batch)
    moves, counts = batch["moves"], batch["move_count"]
    n = source.shape[-1]
    state = source.clone()
    total = torch.zeros(1, device=source.device)
    step = torch.zeros(1, device=source.device)
    for position in range(moves.shape[1]):
        lp = model._score(batch["atom_ids"], batch["lengths"], state, source, step)
        mv = moves[:, position]
        if position < int(counts[0]):
            total = total + lp[0, (mv[0, 0] * n + mv[0, 1]) * n + mv[0, 2]]
            scatter_moves(state, mv[:, 0], mv[:, 1], mv[:, 2], torch.ones(1, dtype=torch.bool, device=source.device))
            step = step + 1
    lp = model._score(batch["atom_ids"], batch["lengths"], state, source, step)
    return float(total + lp[0, NUM_MOVES * n * n]), int(counts[0])


@torch.no_grad()
def sample_routes(model, batch, width):
    """width sampled trajectories: endpoint matrix, trajectory score, move list."""
    source = model._source(batch)
    n = source.shape[-1]
    atom_ids = batch["atom_ids"].repeat_interleave(width, 0)
    lengths = batch["lengths"].repeat_interleave(width, 0)
    src = source.repeat_interleave(width, 0)
    state = src.clone()
    score = torch.zeros(width, device=src.device)
    done = torch.zeros(width, dtype=torch.bool, device=src.device)
    step = torch.zeros(width, device=src.device)
    routes = [[] for _ in range(width)]
    for _ in range(model.max_moves):
        lp = model._score(atom_ids, lengths, state, src, step)
        choice, score, _ = _sample_step(lp, score, done, width)
        kind, rest = choice // (n * n), choice % (n * n)
        i, j = rest // n, rest % n
        live = ~done & (choice != NUM_MOVES * n * n)
        for r in range(width):
            if live[r]:
                routes[r].append((int(kind[r]), int(i[r]), int(j[r])))
        scatter_moves(state, kind, i, j, live)
        step = step + live.float()
        done = ~live
        if bool(done.all()):
            break
    return state, score, routes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--limit", type=int, default=300)
    ap.add_argument("--width", type=int, default=10)
    ap.add_argument("--max_atoms_dump", type=int, default=40,
                     help="only dump disputed cases small enough to draw legibly")
    ap.add_argument("--emb_dim", type=int, default=128)
    ap.add_argument("--enc_filter_size", type=int, default=512)
    ap.add_argument("--config_dir", default=str(Path.cwd() / "configs"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    model, collate = load(args.ckpt, args.emb_dim, args.enc_filter_size, args.config_dir)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)

    summary, disputed = {}, []
    for path in args.files:
        name = Path(path).stem
        order_gaps, product_gaps, recorded_reached, best_is_recorded, n_used = [], [], 0, 0, 0
        for step in read_steps(path, limit=args.limit):
            try:
                rec = collate.featurize(step)
            except Exception:  # noqa: BLE001
                continue
            if not rec.get("usable", True):
                continue
            batch = collate.collate([rec])
            batch = {k: (v.to(device) if torch.is_tensor(v) else v) for k, v in batch.items()}
            size = int(batch["lengths"][0])
            target = batch["tgt"][0, :size, :size].long()

            lp_rec, n_moves = recorded_logp(model, batch)
            state, score, routes = sample_routes(model, batch, args.width)
            hits = [k for k in range(args.width)
                    if torch.equal(state[k, :size, :size].long(), target)]
            best = int(score.argmax())
            n_used += 1
            best_is_recorded += best in hits
            if hits:
                recorded_reached += 1
                best_hit = max(hits, key=lambda k: float(score[k]))
                order_gaps.append(float(score[best_hit]) - lp_rec)
                product_gaps.append(float(score[best]) - float(score[best_hit]))
            if best not in hits and size <= args.max_atoms_dump:
                disputed.append({
                    "stratum": name, "reactant": step[0], "product": step[1], "n_atoms": size,
                    "recorded_moves": [[KIND_NAMES[k], i, j] for k, i, j in
                                       batch["moves"][0, :n_moves].cpu().tolist()],
                    "preferred_moves": [[KIND_NAMES[k], i, j] for k, i, j in routes[best]],
                    "logp_recorded": round(lp_rec, 3),
                    "logp_preferred": round(float(score[best]), 3),
                    "reached_recorded_in_beam": bool(hits),
                })

        n = n_used or 1
        summary[name] = {
            "n": n_used,
            "best_trajectory_is_recorded_product": round(best_is_recorded / n, 4),
            "recorded_product_reached_at_all": round(recorded_reached / n, 4),
            "margin_order_median": round(median(order_gaps), 3) if order_gaps else None,
            "margin_order_mean": round(sum(order_gaps) / len(order_gaps), 3) if order_gaps else None,
            "margin_product_median": round(median(product_gaps), 3) if product_gaps else None,
            "margin_product_mean": round(sum(product_gaps) / len(product_gaps), 3) if product_gaps else None,
        }
        print(name, json.dumps(summary[name]), flush=True)

    with open(args.out, "w") as fh:
        json.dump({"summary": summary, "disputed": disputed}, fh, indent=1)
    print("wrote", args.out, "with", len(disputed), "disputed cases")


if __name__ == "__main__":
    main()
