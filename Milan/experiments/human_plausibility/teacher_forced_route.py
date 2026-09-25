#!/usr/bin/env python
"""Teacher-force the chemist's route on the explicit-H input and read, at each
of its states, what the model would do next -- the sampling-free counterpart
of the parity table in problem02-termination.md.

For a two-move propagation step (homolysis then colligation, the RMechDB
norm) this reports p(A_1 | B_r), p(Stop | x_1), p(A_2 | x_1) and p(Stop | x_2),
so "the model treats the first homolysis as the whole step" is a number
rather than an inference from what the sampler happened to do.

    .venv/bin/python teacher_forced_route.py --limit 1000
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

import torch

from fully_explicit_stability import build_batch, fully_explicit_atom_map
from score_reactions import AFM_REPO, HERE, complete_atom_map, load_model, to_model_moves

sys.path.insert(0, str(AFM_REPO))
from models.afm import NUM_MOVES, scatter_moves  # noqa: E402


@torch.no_grad()
def route_probs(model, batch, moves):
    source = model._source(batch)
    atom_ids, lengths = batch["atom_ids"], batch["lengths"]
    n = source.shape[-1]
    state = source.clone()
    step = torch.zeros(1)
    out = []
    for t in range(moves.shape[1] + 1):
        lp = model._score(atom_ids, lengths, state, source, step)[0]
        p_stop = float(lp[-1].exp())
        if t < moves.shape[1]:
            k, i, j = moves[0, t].tolist()
            p_move = float(lp[(k * n + i) * n + j].exp())
            out.append({"p_stop": p_stop, "p_next_chemist_move": p_move, "stop_offered": bool(torch.isfinite(lp[-1]))})
            scatter_moves(state, torch.tensor([k]), torch.tensor([i]), torch.tensor([j]), torch.ones(1, dtype=torch.bool))
            step = step + 1
        else:
            out.append({"p_stop": p_stop, "stop_offered": bool(torch.isfinite(lp[-1]))})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", default=str(HERE / "multistep.json"))
    ap.add_argument("--ckpt", default=str(AFM_REPO / "outputs/runs/afm_nano/checkpoints/best.ckpt"))
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    targets = json.load(open(args.targets))
    if args.limit:
        targets = targets[: args.limit]
    model = load_model(Path(args.ckpt), 128, 512, model_name="afm")

    by_class = defaultdict(list)
    for t in targets:
        if t["n_moves"] != 2:
            continue
        mapped = fully_explicit_atom_map(t["reactant"])
        _, o2n = complete_atom_map(t["reactant"])
        try:
            moves = to_model_moves(t["moves"], o2n)
        except KeyError:
            continue
        batch, _ = build_batch(mapped)
        try:
            probs = route_probs(model, batch, moves)
        except Exception as exc:  # noqa: BLE001
            print("failed:", exc)
            continue
        by_class[t["meta"][2]].append((t["moves"][0][0], t["moves"][1][0], probs))

    def agg(rows, key, t):
        vals = [r[2][t][key] for r in rows if key in r[2][t]]
        return f"mean={mean(vals):.3f} median={median(vals):.4f}" if vals else "n/a"

    print("two-move chemist routes, teacher-forced on the explicit-H input\n")
    for cls, rows in sorted(by_class.items(), key=lambda x: -len(x[1])):
        kinds = defaultdict(int)
        for a, b, _ in rows:
            kinds[f"{a}->{b}"] += 1
        top = ", ".join(f"{k}:{v}" for k, v in sorted(kinds.items(), key=lambda x: -x[1])[:3])
        print(f"[{cls}] n={len(rows)}  routes: {top}")
        print(f"   at B_r : p(Stop) {agg(rows,'p_stop',0)} | p(chemist move 1) {agg(rows,'p_next_chemist_move',0)}")
        print(f"   at x_1 : p(Stop) {agg(rows,'p_stop',1)} | p(chemist move 2) {agg(rows,'p_next_chemist_move',1)}"
              f" | Stop offered at x_1: {100*mean(r[2][1]['stop_offered'] for r in rows):.0f}%")
        print(f"   at x_2 : p(Stop) {agg(rows,'p_stop',2)} | Stop offered at x_2: {100*mean(r[2][2]['stop_offered'] for r in rows):.0f}%")
        route_p = [r[2][0]["p_next_chemist_move"] * r[2][1]["p_next_chemist_move"] * r[2][2]["p_stop"] for r in rows]
        print(f"   whole chemist route probability (move1*move2*stop): mean={mean(route_p):.4f} median={median(route_p):.6f}\n")


if __name__ == "__main__":
    main()
