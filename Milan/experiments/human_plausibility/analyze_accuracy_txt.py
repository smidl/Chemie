#!/usr/bin/env python
"""Step accuracy against a FlowER-format txt whose product *is* the chemist's
product (the fine-tune splits of `experiments/finetune`), from an
`instrumented_rollout.py --flower_txt <same file>` log.

Same scoring as `analyze_accuracy.py`: replay the logged moves on the
reactant matrix, reconstruct the emitted state with the repo's own
`chem.product_smiles_from_be`, compare canonical map-free SMILES with the
product column; a never-stopped chain emits `B_r` (the decoder's fallback).
Recognises the recombination alternative for two-radical reactants and the
"homolysis, then Stop" triradical emission. Class labels come from the split
manifest when given.

    .venv/bin/python analyze_accuracy_txt.py results/instrumented_test_released.jsonl \
        ../finetune/data/rmechdb_ft/test.txt --manifest ../finetune/data/rmechdb_ft/manifest.json --split test
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict

import numpy as np
import torch

from analyze_accuracy import KIND_INDEX, apply, canonical, pct
from fully_explicit_stability import build_batch
from score_reactions import AFM_REPO

sys.path.insert(0, str(AFM_REPO))
import chem  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("log")
    ap.add_argument("txt")
    ap.add_argument("--manifest", default=None)
    ap.add_argument("--split", default="test")
    args = ap.parse_args()

    pairs = [l.strip().split("|")[0].split(">>") for l in open(args.txt) if ">>" in l]
    labels = {}
    if args.manifest:
        for row in json.load(open(args.manifest))["splits"][args.split]["lines"]:
            labels[row["seq"]] = (row["meta"][2] if row["meta"] else None, row["n_moves"])

    by_group = defaultdict(Counter)
    outcome_by_odd = defaultdict(Counter)
    totals = Counter()
    for line in open(args.log):
        rec = json.loads(line)
        reactant, product = pairs[rec["index"]]
        batch, _ = build_batch(reactant)
        mol = batch["reactant_mols"][0]
        src = batch["src"].long()
        size = int(batch["lengths"][0])
        # Write the chemist's product through the same writer as the emitted states
        # (`product_smiles_from_be`, implicit hydrogens), not from the mapped string
        # with every hydrogen explicit -- RDKit canonicalises those two forms of one
        # molecule to different strings.
        pbe = chem.atom_types_and_be(chem.mol_from_mapped_smiles(product))[1]
        human = canonical(chem.product_smiles_from_be(mol, pbe))
        reactant_c = canonical(chem.product_smiles_from_be(mol, src[0, :size, :size].numpy()))
        diag0 = np.diag(src[0, :size, :size].numpy())
        odd_atoms = [int(k) for k in np.nonzero(diag0 % 2)[0]]
        n_odd = min(len(odd_atoms), 3)
        recomb = None
        if len(odd_atoms) == 2:
            a, b = sorted(odd_atoms)
            rs = src.clone()
            apply(rs, [(3, a, b)])
            recomb = canonical(chem.product_smiles_from_be(mol, rs[0, :size, :size].numpy()))
        cls, n_moves = labels.get(rec["index"], (None, None))
        key = (cls, n_odd)
        any_hit = False
        for ch in rec["chains"]:
            st = src.clone()
            apply(st, [(KIND_INDEX[s["move"]], s["i"], s["j"]) for s in ch["steps"] if s["move"] != "STOP"])
            final_odd = int((np.diag(st[0, :size, :size].numpy()) % 2).sum())
            emitted = canonical(chem.product_smiles_from_be(mol, st[0, :size, :size].numpy())) if ch["stopped"] else reactant_c
            hit = emitted == human
            any_hit |= hit
            if not ch["stopped"]:
                o = "stuck -> fallback (reactant)"
            elif hit:
                o = "= chemist product"
            elif emitted == reactant_c:
                o = "stopped at reactant (identity)"
            elif recomb is not None and emitted == recomb:
                o = "= recombination of the two radicals"
            elif final_odd >= len(odd_atoms) + 2:
                o = "stopped with 2 fresh radicals (homolysis, then Stop)"
            else:
                o = "stopped, other product"
            by_group[key]["chains"] += 1
            by_group[key]["hit"] += hit
            outcome_by_odd[n_odd][o] += 1
            totals["chains"] += 1
            totals["hit"] += hit
            totals["stuck"] += (not ch["stopped"])
        by_group[key]["reactants"] += 1
        by_group[key]["any_hit"] += any_hit
        totals["reactants"] += 1
        totals["any_hit"] += any_hit

    print(f"log: {args.log}")
    print(f"reactants={totals['reactants']} chains={totals['chains']}  stuck={pct(totals['stuck'], totals['chains']):.1f}%  "
          f"chain exact match={pct(totals['hit'], totals['chains']):.1f}%  any-of-3={pct(totals['any_hit'], totals['reactants']):.1f}%")
    print("by (class, radical centres):")
    for (cls, n_odd), c in sorted(by_group.items(), key=lambda x: -x[1]["chains"]):
        print(f"  {str(cls):<14} odd={n_odd} reactants={c['reactants']:<4} chain match={pct(c['hit'], c['chains']):5.1f}%  any-of-3={pct(c['any_hit'], c['reactants']):5.1f}%")
    print("outcomes by radical centres:")
    for n_odd in sorted(outcome_by_odd):
        tot = sum(outcome_by_odd[n_odd].values())
        print(f"  odd={n_odd} (chains={tot}): " + "; ".join(f"{o} {pct(v, tot):.0f}%" for o, v in outcome_by_odd[n_odd].most_common()))


if __name__ == "__main__":
    main()
