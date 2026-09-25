#!/usr/bin/env python
"""Splits the mid-mechanism reconstruction gap by reactant/step properties.

Both fixes tried so far (the 4-axis mask, fully-explicit-hydrogen
preprocessing) leave mid-mechanism reconstruction well below final-product
reconstruction -- this does not slice the sample, it just re-confirms the
gap exists. This script joins each self-sampled step (from
``fully_explicit_stability.jsonl`` and, for comparison, the RMechDB-native
``afm_sampled_stability.jsonl``) back to ``multistep.json``'s reactant/
meta/moves fields and RDKit-derived size features, then reports
reconstruction rate broken down by:

* reactant size (heavy atoms; total atoms post-AddHs)
* reaction class / stage (``meta``: Propagation/Termination/Initiation x
  abstraction/addition/retroaddition/resonance/homolyze/recombine)
* whether the *human* route contains a radical move (HOMOLYSIS/COLLIGATION)
  -- a proxy for "this reactant's chemistry is the kind the separately
  documented ``_radical_moves()`` bug underserves in training", not a claim
  about what the model actually sampled
* position within the self-sampled chain (early vs late -- error
  accumulation) and self-sampled chain length
* whether the *same* reactant's mid-steps succeed in both preprocessing
  variants (an OOD-difficulty signal, if failure correlates across variants,
  vs a preprocessing-artifact signal, if it doesn't)

Run (from this directory)::

    .venv/bin/python analyze_mid_gap.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")

HERE = Path(__file__).resolve().parent
_PS = Chem.SmilesParserParams()
_PS.removeHs = False
_PS.sanitize = True

_RADICAL_MOVE_NAMES = {"HOMOLYSIS", "COLLIGATION"}


def load_targets():
    return json.load(open(HERE / "multistep.json"))


def reactant_sizes(smiles: str):
    mol = Chem.MolFromSmiles(smiles, _PS)
    if mol is None:
        return None, None
    heavy = mol.GetNumHeavyAtoms()
    total = Chem.AddHs(mol).GetNumAtoms()
    return heavy, total


def size_bucket(n, edges):
    for lo, hi, label in edges:
        if lo <= n < hi:
            return label
    return f">={edges[-1][1]}"


SIZE_EDGES = [(0, 8, "<8"), (8, 12, "8-11"), (12, 16, "12-15"), (16, 24, "16-23"), (24, 10**9, "24+")]
POS_EDGES = [(0, 1, "pos 0"), (1, 2, "pos 1"), (2, 3, "pos 2"), (3, 10**9, "pos 3+")]
LEN_EDGES = [(0, 2, "len<2"), (2, 3, "len 2"), (3, 5, "len 3-4"), (5, 10**9, "len 5+")]


def flatten(results_path: Path, targets: list[dict]):
    """One row per self-sampled mid-mechanism step (final position excluded)."""
    rows = []
    with open(results_path) as fh:
        for line in fh:
            rec = json.loads(line)
            idx = rec["index"]
            meta = targets[idx].get("meta", [None, None, None])
            moves = targets[idx].get("moves", [])
            n_moves_human = targets[idx].get("n_moves")
            heavy, total = reactant_sizes(rec["reactant"])
            radical_route = any(m[0] in _RADICAL_MOVE_NAMES for m in moves)
            for chain in rec["chains"]:
                chain_len = len(chain)
                for pos, step in enumerate(chain):
                    if pos == chain_len - 1:
                        continue  # final position -- not part of the mid-mechanism gap
                    rows.append({
                        "index": idx,
                        "pos": pos,
                        "chain_len": chain_len,
                        "reconstructs": bool(step.get("reconstructs")),
                        "heavy": heavy,
                        "total": total,
                        "stage": meta[1] if len(meta) > 1 else None,
                        "reaction_class": meta[2] if len(meta) > 2 else None,
                        "radical_route": radical_route,
                        "n_moves_human": n_moves_human,
                    })
    return rows


def pct(k, n):
    return 100 * k / n if n else float("nan")


def breakdown(rows, key, label):
    print(f"\n-- by {label} --")
    buckets = defaultdict(lambda: [0, 0])
    for r in rows:
        buckets[key(r)][1] += 1
        buckets[key(r)][0] += r["reconstructs"]
    for k in sorted(buckets, key=lambda x: (x is None, str(x))):
        ok, n = buckets[k]
        print(f"  {str(k):<12} n={n:<6} reconstructs={pct(ok, n):5.1f}%")


def main():
    targets = load_targets()
    explicit_path = HERE / "results" / "fully_explicit_stability.jsonl"
    native_path = HERE / "results" / "afm_sampled_stability.jsonl"

    print("=" * 70)
    print("Fully-explicit-H preprocessing run")
    print("=" * 70)
    rows_explicit = flatten(explicit_path, targets)
    print(f"total mid-mechanism steps: {len(rows_explicit)}")
    breakdown(rows_explicit, lambda r: size_bucket(r["total"], SIZE_EDGES), "total atom count (post-AddHs)")
    breakdown(rows_explicit, lambda r: size_bucket(r["heavy"], SIZE_EDGES), "heavy atom count")
    breakdown(rows_explicit, lambda r: r["reaction_class"], "reaction class (human route)")
    breakdown(rows_explicit, lambda r: r["stage"], "stage (human route)")
    breakdown(rows_explicit, lambda r: r["radical_route"], "human route contains HOMOLYSIS/COLLIGATION")
    breakdown(rows_explicit, lambda r: size_bucket(r["pos"], POS_EDGES), "position in self-sampled chain")
    breakdown(rows_explicit, lambda r: size_bucket(r["chain_len"], LEN_EDGES), "self-sampled chain length")
    breakdown(rows_explicit, lambda r: r["n_moves_human"], "human route move count (n_moves)")
    breakdown(rows_explicit, lambda r: "hit max_moves=12 budget" if r["chain_len"] == 12 else "stopped on its own",
              "did this step's OWN chain ever find a valid stop")

    if native_path.exists():
        print("\n" + "=" * 70)
        print("RMechDB-native mapping run (for cross-variant correlation)")
        print("=" * 70)
        rows_native = flatten(native_path, targets)
        print(f"total mid-mechanism steps: {len(rows_native)}")
        breakdown(rows_native, lambda r: size_bucket(r["total"], SIZE_EDGES), "total atom count (post-AddHs, recomputed)")

        # Per-reactant success rate in each variant, to check whether the same
        # reactants are hard in both (OOD-difficulty) or not (preprocessing
        # artifact / sampling noise).
        def per_reactant_rate(rows):
            agg = defaultdict(lambda: [0, 0])
            for r in rows:
                agg[r["index"]][1] += 1
                agg[r["index"]][0] += r["reconstructs"]
            return {idx: (ok / n if n else None) for idx, (ok, n) in agg.items()}

        rate_explicit = per_reactant_rate(rows_explicit)
        rate_native = per_reactant_rate(rows_native)
        common = sorted(set(rate_explicit) & set(rate_native))
        print(f"\nreactants with mid-mechanism steps in both variants: {len(common)}")
        both_ok = sum(1 for i in common if rate_explicit[i] == 1.0 and rate_native[i] == 1.0)
        both_bad = sum(1 for i in common if rate_explicit[i] == 0.0 and rate_native[i] == 0.0)
        only_explicit_ok = sum(1 for i in common if rate_explicit[i] == 1.0 and rate_native[i] < 1.0)
        only_native_ok = sum(1 for i in common if rate_native[i] == 1.0 and rate_explicit[i] < 1.0)
        print(f"  all-steps-reconstruct in BOTH variants: {both_ok} ({pct(both_ok, len(common)):.1f}%)")
        print(f"  zero-steps-reconstruct in BOTH variants: {both_bad} ({pct(both_bad, len(common)):.1f}%)")
        print(f"  all-ok in explicit-H only:               {only_explicit_ok} ({pct(only_explicit_ok, len(common)):.1f}%)")
        print(f"  all-ok in native-mapping only:            {only_native_ok} ({pct(only_native_ok, len(common)):.1f}%)")
        try:
            import numpy as np
            a = np.array([rate_explicit[i] for i in common])
            b = np.array([rate_native[i] for i in common])
            if a.std() > 0 and b.std() > 0:
                corr = float(np.corrcoef(a, b)[0, 1])
                print(f"  per-reactant reconstruction-rate correlation across variants: r={corr:.3f}")
        except ImportError:
            pass


if __name__ == "__main__":
    main()
