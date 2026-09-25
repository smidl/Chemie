#!/usr/bin/env python
"""The paper's own extension, measured: rank candidates by the *exact* product
likelihood instead of by one trajectory's score.

The Conclusion names it -- "summing the trajectory likelihood over the
admissible orders of one multiset of moves would give the exact product
likelihood rather than the lower bound, and might close the remaining gap". The
stratified evaluation says where to spend it: at six or more moves the recorded
product is in the beam 99.3% of the time and ranked first only 79%, and the
disputed cases are prefixes of the recorded cascade, which a sum of one
trajectory's negative log terms structurally prefers.

Exact, not sampled. The state after a set of moves does not depend on their
order (increments add), so the sum over admissible orders is a dynamic program
over subsets:

    f(empty) = 1
    f(S)     = sum_{a in S} f(S \\ {a}) * p(a | x_{S \\ {a}})
    P(product) = f(M) * p(Stop | x_M)

Inadmissible orders drop out for free: the move mask gives p(a | x) = 0 when a
prefix would leave the representable set, so only orders the chain could
actually take contribute. Identical moves in one multiset would be counted once
per distinguishable index-order, so the total is divided by the product of the
multiplicity factorials.

Cost is 2^m masked forward passes per candidate, batched -- a few hundred per
step at m <= 10, no retraining.

    python strata_exact_likelihood.py --ckpt <best.ckpt> --files <strata>/test_m6plus.txt \
        --limit 200 --out exact.json
"""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path
from statistics import median

import torch

import compat_flower_cons  # noqa: F401
import hydra
import models  # noqa: F401
from data import read_steps
from models.afm import NUM_MOVES, CollateAFM, _sample_step, scatter_moves

NEG_INF = float("-inf")


def load(ckpt, emb_dim, filt, config_dir):
    with hydra.initialize_config_dir(config_dir=config_dir, version_base=None):
        cfg = hydra.compose(config_name="default_eval", overrides=[
            "model=afm", f"model.emb_dim={emb_dim}",
            f"model.enc_filter_size={filt}", "model.decode=sample"])
    model = hydra.utils.instantiate(cfg.model)
    model.load_state_dict(torch.load(ckpt, map_location="cpu", weights_only=False)["state_dict"],
                          strict=True)
    return model.eval(), CollateAFM()


@torch.no_grad()
def sample_routes(model, batch, width):
    """width sampled trajectories: endpoint, trajectory score, move list."""
    source = model._source(batch)
    n = source.shape[-1]
    atom_ids = batch["atom_ids"].repeat_interleave(width, 0)
    lengths = batch["lengths"].repeat_interleave(width, 0)
    src = source.repeat_interleave(width, 0)
    state, score = src.clone(), torch.zeros(width, device=src.device)
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


@torch.no_grad()
def exact_logp(model, batch, moves, chunk=64):
    """log P(product) summed over every admissible order of this move multiset."""
    m = len(moves)
    source = model._source(batch)
    n = source.shape[-1]
    stop_index = NUM_MOVES * n * n
    if m == 0:
        lp = model._score(batch["atom_ids"], batch["lengths"], source, source,
                          torch.zeros(1, device=source.device))
        return float(lp[0, stop_index])

    total = 1 << m
    # Held on the host: 2^m matrices of N^2 is 1.7 GB of device memory at the
    # corpus's largest molecules, and only one chunk is needed at a time.
    host = source.detach().cpu()
    states = torch.empty((total, n, n), dtype=host.dtype)
    for mask in range(total):
        st = host.clone()
        for b in range(m):
            if mask >> b & 1:
                k, i, j = moves[b]
                scatter_moves(st, torch.tensor([k]), torch.tensor([i]),
                              torch.tensor([j]), torch.ones(1, dtype=torch.bool))
        states[mask] = st[0]
    popcount = torch.tensor([bin(mask).count("1") for mask in range(total)], dtype=torch.float)
    # the roll-out cost is O(rows * N^2); keep that product bounded
    chunk = max(1, min(chunk, 2_000_000 // max(1, n * n)))

    logits = []
    for start in range(0, total, chunk):
        stop = min(start + chunk, total)
        rows = stop - start
        logits.append(model._score(
            batch["atom_ids"].expand(rows, -1), batch["lengths"].expand(rows),
            states[start:stop].to(source.device), source.expand(rows, -1, -1),
            popcount[start:stop].to(source.device)).cpu())
    logits = torch.cat(logits)

    f = [NEG_INF] * total
    f[0] = 0.0
    for mask in range(total):
        if f[mask] == NEG_INF:
            continue
        for b in range(m):
            if mask >> b & 1:
                continue
            k, i, j = moves[b]
            value = f[mask] + float(logits[mask, (k * n + i) * n + j])
            if value == NEG_INF or value != value:
                continue
            nxt = mask | (1 << b)
            f[nxt] = value if f[nxt] == NEG_INF else float(
                torch.logaddexp(torch.tensor(f[nxt]), torch.tensor(value)))
    full = total - 1
    if f[full] == NEG_INF:
        return None
    # identical moves: each trajectory corresponds to mult! index-orders
    correction = sum(math.log(math.factorial(c)) for c in Counter(moves).values())
    return f[full] + float(logits[full, stop_index]) - correction


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--limit", type=int, default=200)
    ap.add_argument("--width", type=int, default=20)
    ap.add_argument("--max_m", type=int, default=8)
    ap.add_argument("--top_candidates", type=int, default=5)
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
        n_used = skipped = 0
        top1_traj = top1_freq = top1_exact = 0
        flips, gains, fell_back = 0, [], 0
        for step in read_steps(path, limit=args.limit):
            try:
                rec = collate.featurize(step)
            except Exception:  # noqa: BLE001
                continue
            if not rec.get("usable", True) or len(rec["moves"]) > args.max_m:
                skipped += 1
                continue
            batch = collate.collate([rec])
            batch = {k: (v.to(device) if torch.is_tensor(v) else v) for k, v in batch.items()}
            size = int(batch["lengths"][0])
            target = batch["tgt"][0, :size, :size].long()

            state, score, routes = sample_routes(model, batch, args.width)
            # distinct products, each with its best-scoring route and draw count
            best = {}
            for r in range(args.width):
                key = state[r, :size, :size].long().cpu().numpy().tobytes()
                entry = best.get(key)
                if entry is None or float(score[r]) > entry[0]:
                    best[key] = (float(score[r]), routes[r], r)
                best[key] = (best[key][0], best[key][1], best[key][2])
            counts = Counter(state[r, :size, :size].long().cpu().numpy().tobytes()
                             for r in range(args.width))
            target_key = target.cpu().numpy().tobytes()
            if target_key not in best:
                continue  # recorded product never sampled: ranking cannot fix it
            n_used += 1

            ranked = sorted(best.items(), key=lambda kv: -kv[1][0])[:args.top_candidates]
            top1_traj += ranked[0][0] == target_key
            top1_freq += max(counts, key=lambda k: counts[k]) == target_key

            scored = []
            for key, (traj_score, route, _) in ranked:
                # One hard candidate must not sink the run: fall back to the
                # trajectory score for it and count how often that happened, so
                # the result says how much of it is actually exact.
                try:
                    exact = exact_logp(model, batch, [tuple(mv) for mv in route])
                except torch.OutOfMemoryError:
                    torch.cuda.empty_cache()
                    exact = None
                if exact is None:
                    fell_back += 1
                scored.append((exact if exact is not None else traj_score, key))
            scored.sort(key=lambda kv: -kv[0])
            top1_exact += scored[0][1] == target_key
            if ranked[0][0] != target_key and scored[0][1] == target_key:
                flips += 1
            exact_by_key = {k: v for v, k in scored}
            if target_key in exact_by_key:
                gains.append(exact_by_key[target_key] - best[target_key][0])

        n = n_used or 1
        out[name] = {
            "n_scored": n_used, "n_skipped_long_or_unusable": skipped,
            "top1_by_trajectory_score": round(top1_traj / n, 4),
            "top1_by_frequency": round(top1_freq / n, 4),
            "top1_by_exact_likelihood": round(top1_exact / n, 4),
            "flipped_to_recorded": flips,
            "candidates_without_exact_score": fell_back,
            "exact_minus_trajectory_median": round(median(gains), 3) if gains else None,
        }
        print(name, json.dumps(out[name]), flush=True)
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=1)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
