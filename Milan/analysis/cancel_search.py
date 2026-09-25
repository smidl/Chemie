#!/usr/bin/env python
"""Bounded cancellation: the two things the minimal-decomposition search misses.

`decompose_steps.py` builds its search slots from the bond-order delta, so it only
ever finds decompositions in which no bond is touched twice. Two known
consequences (Milan/plan.md 3c-3d):

  1. The 121 RMechDB rows with NO bond-order change are excluded outright, even
     though the alphabet can express them -- worked by hand for
     "[O-:1][N+:2]=O >> [O:1][N:2]=O" (arrow 1-2), which needs LONE_TO_BOND(1->2)
     at (-2,0,+1) plus HOMOLYSIS(1,2) at (+1,+1,-1), summing to (-1,+1,0).
  2. The "98.8% admit exactly one mechanism" figure counts only minimal
     decompositions, so true ambiguity is understated by an unknown amount.

The decision of 2026-09-15 was not to rewrite the search. This does the bounded
version instead: allow at most ONE cancelling pair (+1 and -1 on the same bond, a
move and its inverse) on top of the minimal slots. That answers both questions
with a bounded, checkable extension rather than an open-ended one.

  --mode express : can the alphabet express the no-bond-change rows at all?
  --mode ambiguity : how much does one cancelling pair raise the count of valid
                     decompositions, on a random sample of ordinary steps?

  .venv/bin/python cancel_search.py --csv FILE --mode express --out_json out.json
"""
import argparse
import csv
import itertools
import json
import random
import sys
from collections import Counter

from rdkit import RDLogger

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from decompose_steps import (  # noqa: E402
    MOVES_MINUS, MOVES_PLUS, components, order_component,
)
from rmechdb_arrows import reduced_matrix  # noqa: E402

RDLogger.DisableLog("rdApp.*")

MAX_COMPONENT = 7


def candidate_pairs(elements):
    """Every unordered atom pair -- a cancelling pair may use a bond that does
    not exist in either endpoint, created and destroyed inside the mechanism."""
    atoms = sorted(elements)
    return list(itertools.combinations(atoms, 2))


def search(r, p, cap, extra_pairs, max_extra=1, exhaustive=False):
    """Valid decompositions allowing up to `max_extra` cancelling pairs."""
    r_diag, r_bonds, r_elem, _ = r
    p_diag, p_bonds, _p_elem, _ = p

    delta = {}
    for key in set(r_bonds) | set(p_bonds):
        d = p_bonds.get(key, 0) - r_bonds.get(key, 0)
        if d:
            delta[key] = d
    required = {n: p_diag[n] - r_diag[n] for n in r_diag}

    base_slots = []
    for (i, j), d in delta.items():
        table = MOVES_PLUS if d > 0 else MOVES_MINUS
        for _ in range(abs(d)):
            base_slots.append([(name, i, j, dii, djj, dij) for name, dii, djj, dij in table])

    found = []
    for n_extra in range(max_extra + 1):
        for extra in itertools.combinations_with_replacement(extra_pairs, n_extra):
            slots = list(base_slots)
            for (i, j) in extra:
                # one +1 and one -1 on the same bond: they cancel on the bond and
                # can still move electrons between the two diagonals
                slots.append([(nm, i, j, a, b, c) for nm, a, b, c in MOVES_PLUS])
                slots.append([(nm, i, j, a, b, c) for nm, a, b, c in MOVES_MINUS])
            if len(slots) > 8:
                continue
            for combo in itertools.product(*slots):
                contrib = Counter()
                for _, i, j, dii, djj, _ in combo:
                    contrib[i] += dii
                    contrib[j] += djj
                if any(contrib.get(n, 0) != required[n] for n in required):
                    continue
                comps = components(list(combo))
                if any(len(c) > MAX_COMPONENT for c in comps):
                    continue
                d_, b_, ok = dict(r_diag), dict(r_bonds), True
                for comp in comps:
                    got = order_component(d_, b_, r_elem, cap, list(combo), comp)
                    if got is None:
                        ok = False
                        break
                    _, d_, b_ = got
                if ok:
                    found.append((n_extra, [m[0] for m in combo]))
        if found and not exhaustive:
            break  # smallest number of cancelling pairs that works
    # exhaustive=True keeps going, so `found` holds BOTH the minimal decompositions
    # and those needing one cancelling pair -- which is what the ambiguity question
    # asks. Stopping early answers "how many pairs are needed", a different thing.
    return found


def load(path):
    out = []
    for rec in csv.reader(open(path)):
        if not rec or ">>" not in rec[0]:
            continue
        smirks = rec[0].strip().rpartition(" ")[0]
        src, _, dst = smirks.partition(">>")
        out.append((src, dst))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--mode", choices=("express", "ambiguity"), required=True)
    ap.add_argument("--sample", type=int, default=400)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max_atoms", type=int, default=28,
                    help="bound on the extra-pair sweep; raise it for small target sets")
    ap.add_argument("--out_json", required=True)
    args = ap.parse_args()
    rng = random.Random(args.seed)

    pairs, cap = [], {}
    for src, dst in load(args.csv):
        r, p = reduced_matrix(src), reduced_matrix(dst)
        if r is None or p is None or set(r[2]) != set(p[2]) or r[3] != p[3]:
            continue
        pairs.append((r, p))
        for m in (r, p):
            diag, bonds, elements, context = m
            for n, sym in elements.items():
                beta = sum(o for (i, j), o in bonds.items() if i == n or j == n) + context[n]
                occ = diag[n] + 2 * beta
                if occ > cap.get(sym, 0):
                    cap[sym] = occ

    def bond_delta_empty(r, p):
        rb, pb = r[1], p[1]
        return all(pb.get(k, 0) == rb.get(k, 0) for k in set(rb) | set(pb))

    if args.mode == "express":
        targets = [(r, p) for r, p in pairs if bond_delta_empty(r, p)]
    else:
        ordinary = [(r, p) for r, p in pairs if not bond_delta_empty(r, p)]
        rng.shuffle(ordinary)
        targets = ordinary[: args.sample]

    res = Counter()
    extra_hist = Counter()
    minimal_counts, extended_counts = [], []
    for r, p in targets:
        ep = candidate_pairs(r[2])
        if len(ep) > args.max_atoms:   # keep the extra-pair sweep bounded
            res["skipped_too_many_atoms"] += 1
            continue
        found = search(r, p, cap, ep, max_extra=1,
                       exhaustive=(args.mode == 'ambiguity'))
        if not found:
            res["not_expressible"] += 1
            continue
        res["expressible"] += 1
        n_extra = min(f[0] for f in found)
        extra_hist[n_extra] += 1
        minimal_counts.append(sum(1 for f in found if f[0] == 0))
        extended_counts.append(len(found))

    out = {
        "csv": args.csv,
        "mode": args.mode,
        "targets": len(targets),
        "result": dict(res),
        "cancelling_pairs_needed": {str(k): v for k, v in sorted(extra_hist.items())},
        "mean_decompositions_minimal": round(sum(minimal_counts) / max(1, len(minimal_counts)), 3),
        "mean_decompositions_with_one_cancelling_pair": round(
            sum(extended_counts) / max(1, len(extended_counts)), 3),
    }
    with open(args.out_json, "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
