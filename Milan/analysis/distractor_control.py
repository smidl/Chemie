#!/usr/bin/env python
"""Negative control: does the alphabet REJECT wrong products?

The 99.73% coverage of §3e (17,623 of 17,671 curated steps decomposed) is only
evidence for the architectural claim -- that a move-based construction cannot emit
a product with no mechanism, where ArrowFinder's generate-then-filter fails on
31% of its own balance-filtered predictions -- if admitting a decomposition is
DISCRIMINATING. If the alphabet accepts nearly any balanced rearrangement, the
coverage number says nothing and the argument collapses.

Distractor construction. Group steps by the (map number -> element) signature of
their reactant side. Within a group every step describes a different reaction over
an identical labelled atom set, so pairing step i's reactant with step j's product
(i != j) yields a pair that is:

  * balanced          -- same labelled atoms on both sides, by construction
  * chemically valid  -- the product is a real curated molecule, unmodified
  * almost always wrong -- it is a different reaction's outcome

which is exactly the shape of the balance-filtered wrong predictions ArrowFinder
reports 68.86% on. Identical-product pairs are dropped (some groups contain
genuine duplicates); so are pairs whose product happens to equal the true one.

Reported separately from failures: distractors whose delta exceeds the search
budget. Those are "not decomposed within budget", not evidence of rejection, and
lumping them in would flatter the result.

  .venv/bin/python distractor_control.py --csv a.csv b.csv --out_json out.json
"""
import argparse
import csv
import json
import random
import sys
from collections import Counter, defaultdict

from rdkit import RDLogger

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from rmechdb_arrows import decompose, reduced_matrix  # noqa: E402
from decompose_steps import VALENCE  # noqa: E402

RDLogger.DisableLog("rdApp.*")


def load(paths):
    """Accepts both layouts we hold.

    PMechDB/RMechDB CSV : '"SMIRKS arrowcodes",meta,...'  -- arrows after a space
    FlowER corpus .txt  : 'reactant>>product|label'       -- no arrows, pipe label

    Sniffing on the pipe rather than the extension, because a corpus sample can be
    written anywhere. Getting this wrong silently yields zero usable steps.
    """
    out = []
    for path in paths:
        for rec in csv.reader(open(path)):
            if not rec or ">>" not in rec[0]:
                continue
            field = rec[0].strip()
            if "|" in field and " " not in field.rpartition("|")[0]:
                smirks = field.rpartition("|")[0]      # corpus line
            else:
                smirks = field.rpartition(" ")[0]      # mechdb line
            if ">>" not in smirks:
                continue
            src, _, dst = smirks.partition(">>")
            out.append((src, dst))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", nargs="+", required=True)
    ap.add_argument("--per_step", type=int, default=3, help="distractors per step")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out_json", required=True)
    args = ap.parse_args()
    rng = random.Random(args.seed)

    steps = load(args.csv)
    built = []
    cap = defaultdict(int)
    for src, dst in steps:
        r, p = reduced_matrix(src), reduced_matrix(dst)
        if r is None or p is None or set(r[2]) != set(p[2]) or r[3] != p[3]:
            continue
        built.append((r, p, dst))
        for m in (r, p):
            diag, bonds, elements, context = m
            for n, sym in elements.items():
                beta = sum(o for (i, j), o in bonds.items() if i == n or j == n) + context[n]
                occ = diag[n] + 2 * beta
                if occ > cap[sym]:
                    cap[sym] = occ
    cap = dict(cap)

    # Group by the labelled atom set of the reactant: same map numbers, same
    # elements. Within a group any product is a syntactically legal counterfactual.
    groups = defaultdict(list)
    for idx, (r, _p, _dst) in enumerate(built):
        sig = tuple(sorted(r[2].items()))
        groups[sig].append(idx)

    true_v, dist_v = Counter(), Counter()
    n_pairs, group_sizes = 0, Counter()
    for sig, members in groups.items():
        group_sizes[min(len(members), 10)] += 1
    for r, p, _dst in built:
        v, _ = decompose(r, p, cap)
        true_v[v] += 1

    for sig, members in groups.items():
        if len(members) < 2:
            continue
        for idx in members:
            r, _p, true_dst = built[idx]
            others = [k for k in members if k != idx and built[k][2] != true_dst]
            if not others:
                continue
            rng.shuffle(others)
            for k in others[: args.per_step]:
                other_p = built[k][1]
                if set(r[2]) != set(other_p[2]):
                    continue
                v, _ = decompose(r, other_p, cap)
                dist_v[v] += 1
                n_pairs += 1

    def rate(counter):
        dec = counter.get("decomposed", 0)
        # Budget exclusions are not rejections; report them apart.
        budget = counter.get("too_large", 0)
        nochange = counter.get("no_bond_change", 0)
        judged = dec + counter.get("no_decomposition", 0)
        return {
            "counts": dict(counter),
            "decomposed": dec,
            "rejected": counter.get("no_decomposition", 0),
            "over_budget_not_judged": budget,
            "identical_no_bond_change": nochange,
            "judged": judged,
            "decomposed_pct_of_judged": round(100.0 * dec / max(1, judged), 2),
        }

    out = {
        "inputs": args.csv,
        "steps_usable": len(built),
        "groups": len(groups),
        "group_size_hist": {str(k): v for k, v in sorted(group_sizes.items())},
        "distractor_pairs": n_pairs,
        "true": rate(true_v),
        "distractor": rate(dist_v),
    }
    t, d = out["true"]["decomposed_pct_of_judged"], out["distractor"]["decomposed_pct_of_judged"]
    out["discrimination_gap_pp"] = round(t - d, 2)
    with open(args.out_json, "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
