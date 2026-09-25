#!/usr/bin/env python
"""Step accuracy on RMechDB, the paper's own primary metric: does a sampled
chain's emitted state equal the chemist's product (canonical, map-free
SMILES), and how does that split by reaction class, by the number of radical
centres in the reactant, and by what the chain did instead?

Replays the logged moves of `instrumented_rollout.py` on the reactant matrix
(no model needed), reconstructs the emitted state with the repo's own
`chem.product_smiles_from_be`, and compares against the chemist's product
built the same way from `multistep.json`'s moves. A chain that never chose
Stop emits, under the paper's decoder, the last state it was allowed to stop
in -- B_r for a chain that never re-entered the Sector -- and is scored as
such. For a two-radical reactant the *recombination* of the two radical
centres (one COLLIGATION) is also recognised: it is a legitimate alternative
product where the chemist wrote a disproportionation, not a wrong answer.

    .venv/bin/python analyze_accuracy.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict

import numpy as np
import torch
from rdkit import Chem, RDLogger

from fully_explicit_stability import build_batch, fully_explicit_atom_map
from score_reactions import AFM_REPO, HERE, complete_atom_map, to_model_moves

sys.path.insert(0, str(AFM_REPO))
RDLogger.DisableLog("rdApp.*")
import chem  # noqa: E402
from models.afm import scatter_moves  # noqa: E402

KIND_INDEX = {"LONE_TO_BOND": 0, "BOND_TO_LONE": 1, "HOMOLYSIS": 2, "COLLIGATION": 3}


def canonical(mapped_smiles: str) -> str | None:
    if not mapped_smiles:
        return None
    mol = Chem.MolFromSmiles(mapped_smiles, sanitize=False)
    if mol is None:
        return None
    for a in mol.GetAtoms():
        a.SetAtomMapNum(0)
    try:
        Chem.SanitizeMol(mol)
        return Chem.MolToSmiles(mol)
    except Exception:  # noqa: BLE001
        return None


def apply(state: torch.Tensor, moves):
    for k, i, j in moves:
        scatter_moves(state, torch.tensor([k]), torch.tensor([i]), torch.tensor([j]), torch.ones(1, dtype=torch.bool))


def pct(k, n):
    return 100 * k / n if n else float("nan")


def main(log_path):
    targets = json.load(open(HERE / "multistep.json"))
    by_group = defaultdict(Counter)  # (class, reactant odd count) -> counters
    outcome_by_odd = defaultdict(Counter)
    totals = Counter()
    for line in open(log_path):
        rec = json.loads(line)
        t = targets[rec["index"]]
        mapped = fully_explicit_atom_map(t["reactant"])
        _, old_to_new = complete_atom_map(t["reactant"])
        batch, _ = build_batch(mapped)
        mol = batch["reactant_mols"][0]
        src = batch["src"].long()
        size = int(batch["lengths"][0])
        try:
            human = to_model_moves(t["moves"], old_to_new)[0].tolist()
        except KeyError:
            continue
        hs = src.clone()
        apply(hs, human)
        human_smiles = canonical(chem.product_smiles_from_be(mol, hs[0, :size, :size].numpy()))
        if human_smiles is None:
            continue
        reactant_smiles = canonical(chem.product_smiles_from_be(mol, src[0, :size, :size].numpy()))
        diag0 = np.diag(src[0, :size, :size].numpy())
        odd_atoms = [int(k) for k in np.nonzero(diag0 % 2)[0]]
        n_odd = min(len(odd_atoms), 3)
        recomb_smiles = None
        if len(odd_atoms) == 2:
            a, b = sorted(odd_atoms)
            rs = src.clone()
            apply(rs, [(3, a, b)])
            recomb_smiles = canonical(chem.product_smiles_from_be(mol, rs[0, :size, :size].numpy()))
        cls = t["meta"][2]
        key = (cls, n_odd)
        any_hit = False
        for ch in rec["chains"]:
            st = src.clone()
            moves = [(KIND_INDEX[s["move"]], s["i"], s["j"]) for s in ch["steps"] if s["move"] != "STOP"]
            apply(st, moves)
            final_odd = int((np.diag(st[0, :size, :size].numpy()) % 2).sum())
            if ch["stopped"]:
                emitted = canonical(chem.product_smiles_from_be(mol, st[0, :size, :size].numpy()))
            else:
                emitted = reactant_smiles
            hit = emitted == human_smiles
            any_hit |= hit
            if not ch["stopped"]:
                o = "stuck -> fallback (reactant)"
            elif hit:
                o = "= chemist product"
            elif emitted == reactant_smiles:
                o = "stopped at reactant (identity)"
            elif recomb_smiles is not None and emitted == recomb_smiles:
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
        by_group[key]["reactants"] += 1
        by_group[key]["any_hit"] += any_hit
        totals["reactants"] += 1
        totals["any_hit"] += any_hit

    print(f"reactants scored: {totals['reactants']}  chains: {totals['chains']}")
    print(f"chain-level exact match to chemist product: {pct(totals['hit'], totals['chains']):.1f}%   "
          f"reactant-level any-of-3: {pct(totals['any_hit'], totals['reactants']):.1f}%")
    print("\nby (reaction class, radical centres in reactant):")
    for (cls, n_odd), c in sorted(by_group.items(), key=lambda x: (-x[1]["chains"])):
        print(f"  {cls:<14} odd={n_odd}  reactants={c['reactants']:<5} chain match={pct(c['hit'], c['chains']):5.1f}%  any-of-3={pct(c['any_hit'], c['reactants']):5.1f}%")
    print("\nchain outcomes by radical centres in reactant:")
    for n_odd in sorted(outcome_by_odd):
        tot = sum(outcome_by_odd[n_odd].values())
        print(f"  odd={n_odd} (chains={tot})")
        for o, v in outcome_by_odd[n_odd].most_common():
            print(f"     {o:<52} {v:>6} ({pct(v, tot):5.1f}%)")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/instrumented_rmechdb.jsonl")
