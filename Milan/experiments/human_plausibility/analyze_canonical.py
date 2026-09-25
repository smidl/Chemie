#!/usr/bin/env python
"""Rank of the chemist's route among the model's own sampled mechanisms, split
by the length of the chemist's route (one move vs two or more), for one or
more score files produced by `score_reactions.py` on `targets_canonical.json`.

Per group: reactions; those where the model drew >= 2 distinct mechanisms and,
among them, the share where the chemist's route is the model's best (rank 1)
and its worst; the share of reactions where the chemist's route scores below
every mechanism the model drew (never sampled); median trajectory
log-probability of the chemist's route.

    .venv/bin/python analyze_canonical.py results/scores_canonical_released.jsonl results/scores_canonical_ft_mixed.jsonl
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from statistics import median

from analyze import distinct_sorted, human_rank


def pct(k, n):
    return 100 * k / n if n else float("nan")


def main(paths):
    for path in paths:
        groups = defaultdict(list)
        for line in open(path):
            r = json.loads(line)
            n_moves = r["human_length"] - 1
            groups["all"].append(r)
            groups["1 move"].append(r) if n_moves == 1 else groups["2+ moves"].append(r)
            groups[f"class {r['meta'][2]}"].append(r)
        print(f"\n### {path}")
        print(f"{'group':<22}{'reactions':>10}{'>=2 distinct':>13}{'rank 1 (of those)':>19}{'rank last':>11}{'below all sampled':>19}{'median logp(human)':>20}")
        for g in ["all", "1 move", "2+ moves"] + sorted(k for k in groups if k.startswith("class")):
            rows = groups[g]
            multi = []; first = last = below = 0
            for r in rows:
                d = distinct_sorted(r["sampled_logps"])
                rk = human_rank(r["human_logp"], d)  # analyze.py's tolerance: 3 decimals, ties count up
                if rk > len(d):
                    below += 1  # strictly below every mechanism the model drew: never sampled
                if len(d) >= 2:
                    multi.append(r)
                    first += rk == 1
                    last += rk >= len(d)
            print(f"{g:<22}{len(rows):>10}{len(multi):>13}{pct(first, len(multi)):>18.1f}%{pct(last, len(multi)):>10.1f}%{pct(below, len(rows)):>18.1f}%{median(r['human_logp'] for r in rows):>20.2f}")


if __name__ == "__main__":
    main(sys.argv[1:] or ["results/scores_canonical_released.jsonl"])
