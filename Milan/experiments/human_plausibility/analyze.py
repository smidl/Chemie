#!/usr/bin/env python
"""How does the chemist's mechanism rank among AFM's own distinct candidates?

Per reaction, ``score_reactions.py`` already has both numbers: the teacher-forced
log-probability of the chemist's own move sequence, and ~200 samples of the
model's own trajectory log-probabilities for the same reactant. Many of those
200 samples are the *same* mechanism drawn more than once (the model is often
close to deterministic for a small molecule), so the first step is to collapse
them to distinct mechanisms by score. The human's mechanism is then given a
*rank* among those distinct scores (1 = the model's single best; last = its
single worst; ties go to the human).

Reported broken down by how many distinct mechanisms the model actually
produced (1, 2, 3, ... draws), because "human ranked 1st out of 1" is a
different, uninformative statement from "1st out of 6" -- collapsing them into
one percentile number (the previous version of this script) hid exactly that
distinction.

Caveat carried into every number below: 200 samples only find a *lower bound*
on how many distinct mechanisms the model can produce -- a rare alternative may
simply not have been drawn. Reactions therefore never move to a *smaller*
n_unique than their true value, only possibly a larger true one collapsed here
into a smaller observed bucket.
"""
import argparse
import json
import statistics
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
_ROUND = 3  # collapse float noise between the two independent scoring paths


def distinct_sorted(sampled: list[float]) -> list[float]:
    """Sampled log-probs -> distinct mechanism scores, best (highest) first."""
    return sorted({round(s, _ROUND) for s in sampled}, reverse=True)


def human_rank(human_logp: float, distinct: list[float]) -> int:
    """1-based rank of the human's score among the model's distinct candidates.

    A tie (the human's score matches one of the model's own, which is common
    when the model's top draw literally is the human's mechanism) counts as
    reaching that rank, not being pushed below it.
    """
    h = round(human_logp, _ROUND)
    return 1 + sum(1 for v in distinct if v > h)


def bucket_key(n: int) -> str:
    if n <= 5:
        return str(n)
    if n <= 10:
        return "6-10"
    return "11+"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scores", default=str(HERE / "results" / "scores.jsonl"))
    ap.add_argument("--out", default=str(HERE / "results" / "summary.json"))
    args = ap.parse_args()

    rows = []
    n_inf = 0
    with open(args.scores) as fh:
        for line in fh:
            r = json.loads(line)
            if r["human_logp"] == float("-inf"):
                n_inf += 1
                continue
            distinct = distinct_sorted(r["sampled_logps"])
            r["n_unique"] = len(distinct)
            r["human_rank"] = human_rank(r["human_logp"], distinct)
            rows.append(r)

    print(f"Loaded {len(rows)} scored reactions ({n_inf} with -inf human score, excluded above)\n")

    groups: dict[str, list[dict]] = {}
    for r in rows:
        groups.setdefault(bucket_key(r["n_unique"]), []).append(r)

    order = [str(n) for n in range(1, 6)] + ["6-10", "11+"]
    print(f"{'n_unique':>10}  {'n_reactions':>11}  {'rank=1 (top)':>13}  "
          f"{'rank=last (bottom)':>19}  {'median rank/n_unique':>21}")
    table = []
    for key in order:
        g = groups.get(key, [])
        if not g:
            continue
        n = len(g)
        top = sum(r["human_rank"] == 1 for r in g)
        bottom = sum(r["human_rank"] == r["n_unique"] for r in g)
        normalized = [
            (r["human_rank"] - 1) / (r["n_unique"] - 1) if r["n_unique"] > 1 else 0.0 for r in g
        ]
        med_norm = statistics.median(normalized)
        print(f"{key:>10}  {n:>11}  {100 * top / n:>12.1f}%  {100 * bottom / n:>18.1f}%  "
              f"{med_norm:>21.2f}")
        table.append({
            "n_unique": key, "n_reactions": n,
            "pct_rank_1_top": round(100 * top / n, 1),
            "pct_rank_last_bottom": round(100 * bottom / n, 1),
            "median_normalized_rank": round(med_norm, 3),
            "rank_counts": dict(sorted(Counter(r["human_rank"] for r in g).items())),
        })
    print(
        "\n(n_unique=1: the model only ever drew one mechanism, so the human "
        "trivially 'ranks 1st' -- not a discriminating test. "
        "median rank/n_unique: 0.0 = always the model's best, 1.0 = always its "
        "worst, 0.5 = the middle of whatever it could draw.)"
    )

    discriminating = [r for r in rows if r["n_unique"] > 1]
    print(f"\nAcross all {len(discriminating)} reactions with >1 distinct mechanism:")
    print(f"  human ranked 1st (the model's best):  "
          f"{100 * sum(r['human_rank'] == 1 for r in discriminating) / len(discriminating):.1f}%")
    print(f"  human ranked last (the model's worst): "
          f"{100 * sum(r['human_rank'] == r['n_unique'] for r in discriminating) / len(discriminating):.1f}%")

    out = {
        "n_total": len(rows),
        "n_human_zero_probability": n_inf,
        "by_n_unique": table,
        "per_reaction": [
            {"index": r["index"], "n_unique": r["n_unique"], "human_rank": r["human_rank"],
             "human_logp": r["human_logp"]}
            for r in rows
        ],
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
