#!/usr/bin/env python
"""Teacher-force the chemist's routes of the held-out fine-tune split under a
given checkpoint (released or fine-tuned) and read the two transition
probabilities that were ~0 before fine-tuning: p(chemist's first move | B_r)
and, after that move, p(Stop) vs p(chemist's second move).

The split's reactant strings are `fully_explicit_atom_map(original)`, whose
map numbers are the parse indices of the original RMechDB SMILES, so the
chemist's moves translate with `complete_atom_map`'s `old_to_new` exactly as
in `teacher_forced_route.py`; the manifest links each test line back to its
source entry.

    .venv/bin/python teacher_forced_test.py --ckpt ../../ArrowFlowMatching/outputs/runs/afm_nano_ft_mixed/checkpoints/best.ckpt
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from statistics import mean, median

from fully_explicit_stability import build_batch
from score_reactions import AFM_REPO, HERE, complete_atom_map, load_model, to_model_moves
from teacher_forced_route import route_probs

FT = HERE.parent / "finetune" / "data" / "rmechdb_ft"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", default=str(AFM_REPO / "outputs/runs/afm_nano/checkpoints/best.ckpt"))
    ap.add_argument("--split", default="test")
    args = ap.parse_args()
    manifest = json.load(open(FT / "manifest.json"))["splits"][args.split]["lines"]
    lines = [l.strip().split("|")[0].split(">>") for l in open(FT / f"{args.split}.txt") if ">>" in l]
    sources = {s: json.load(open(HERE / s)) for s in ("targets.json", "multistep.json")}
    model = load_model(Path(args.ckpt), 128, 512, model_name="afm")

    by_class = defaultdict(list)
    for row in manifest:
        if row["n_moves"] != 2:
            continue
        entry = sources[row["source"]][row["index"]]
        reactant_mapped = lines[row["seq"]][0]
        _, o2n = complete_atom_map(entry["reactant"])
        try:
            moves = to_model_moves(entry["moves"], o2n)
        except KeyError:
            continue
        batch, _ = build_batch(reactant_mapped)
        probs = route_probs(model, batch, moves)
        by_class[row["meta"][2]].append(probs)

    def agg(rows, key, t):
        vals = [r[t][key] for r in rows if key in r[t]]
        return f"mean={mean(vals):.3f} median={median(vals):.3f}" if vals else "n/a"

    print(f"checkpoint: {args.ckpt}\ntwo-move chemist routes of the {args.split} split, teacher-forced\n")
    for cls, rows in sorted(by_class.items(), key=lambda x: -len(x[1])):
        route_p = [r[0]["p_next_chemist_move"] * r[1]["p_next_chemist_move"] * r[2]["p_stop"] for r in rows]
        print(f"[{cls}] n={len(rows)}")
        print(f"   at B_r : p(chemist move 1) {agg(rows,'p_next_chemist_move',0)} | p(Stop) {agg(rows,'p_stop',0)}")
        print(f"   at x_1 : p(chemist move 2) {agg(rows,'p_next_chemist_move',1)} | p(Stop) {agg(rows,'p_stop',1)}")
        print(f"   at x_2 : p(Stop) {agg(rows,'p_stop',2)}")
        print(f"   whole route: mean={mean(route_p):.3f} median={median(route_p):.3f}\n")


if __name__ == "__main__":
    main()
