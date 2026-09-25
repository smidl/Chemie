#!/usr/bin/env python
"""What *is* the product the model stops at, chemically?

The disputed long steps are prefixes of the recorded cascade: the model
performs the first bond migration and stops. Since the chain may only stop in
the Sector, and a mid-migration state (the pair parked as a lone pair) is not a
molecule, the stopping points are exactly after each *complete* migration. So
the truncation is a real, valence-legal species -- the question is which one.

Two readings, and they call for different fixes:

* **a reactive intermediate** -- charge-separated (a zwitterion, or a carbanion
  next to a leaving group). Then the model is emitting the intermediate of a
  stepwise reading of a step the corpus records as concerted, i.e. it disagrees
  about *granularity*, not about chemistry. The condition that rules such a
  species out as a resting state is not per-atom -- it is a relation between two
  charged centres -- so it is beyond the table by construction, which is the
  non-local validity gap the Conclusion already names.
* **a neutral valence-legal isomer** -- then it is a chemistry error and the fix
  belongs in the stop head or the training marginal.

Reports, per disputed case and in aggregate: formal charges of both products
(from the model's own reconstruction, read back by RDKit), whether either is
charge-separated, and the force-field strain of each.

    python characterise_truncations.py --dispute ../../analysis/results/strata_dispute_afm.json
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from statistics import median

import numpy as np
import torch
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem

HERE = Path(__file__).resolve().parent
HP = HERE.parent / "human_plausibility"
sys.path.insert(0, str(HP))
from score_reactions import AFM_REPO  # noqa: E402

sys.path.insert(0, str(AFM_REPO))
RDLogger.DisableLog("rdApp.*")
import chem  # noqa: E402
from models.afm import scatter_moves  # noqa: E402

KIND_INDEX = {"LONE_TO_BOND": 0, "BOND_TO_LONE": 1, "HOMOLYSIS": 2, "COLLIGATION": 3}


def apply_moves(state, moves):
    for name, i, j in moves:
        scatter_moves(state, torch.tensor([KIND_INDEX[name]]), torch.tensor([i]),
                      torch.tensor([j]), torch.ones(1, dtype=torch.bool))


def describe(mol, matrix):
    """Reconstruct, then read formal charges and strain back through RDKit."""
    smiles = chem.product_smiles_from_be(mol, matrix)
    if not smiles:
        return None
    m = Chem.MolFromSmiles(smiles)
    if m is None:
        return None
    charges = [a.GetFormalCharge() for a in m.GetAtoms()]
    pos = sum(1 for c in charges if c > 0)
    neg = sum(1 for c in charges if c < 0)
    out = {"smiles": smiles, "n_pos": pos, "n_neg": neg, "abs_charge": sum(abs(c) for c in charges),
           "zwitterionic": bool(pos and neg), "n_frags": len(Chem.GetMolFrags(m)),
           "n_heavy": m.GetNumHeavyAtoms(), "radical": sum(a.GetNumRadicalElectrons() for a in m.GetAtoms())}
    mh = Chem.AddHs(m)
    params = AllChem.ETKDGv3()
    params.randomSeed = 0xC0FFEE
    params.useRandomCoords = True
    if AllChem.EmbedMolecule(mh, params) == 0 and AllChem.MMFFHasAllMoleculeParams(mh):
        ff = AllChem.MMFFGetMoleculeForceField(mh, AllChem.MMFFGetMoleculeProperties(mh))
        ff.Minimize(maxIts=2000)
        out["energy_per_heavy"] = ff.CalcEnergy() / max(1, out["n_heavy"])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dispute", default=str(HERE.parent.parent / "analysis" / "results" / "strata_dispute_afm.json"))
    ap.add_argument("--out", default=str(HERE.parent.parent / "analysis" / "results" / "truncation_character.json"))
    args = ap.parse_args()

    cases = json.load(open(args.dispute))["disputed"]
    rows, tally = [], Counter()
    for case in cases:
        mol = chem.mol_from_mapped_smiles(case["reactant"])
        _, be = chem.atom_types_and_be(mol)
        size = be.shape[0]
        src = torch.as_tensor(be, dtype=torch.float32).unsqueeze(0).long()

        rec_state = src.clone()
        apply_moves(rec_state, case["recorded_moves"])
        pref_state = src.clone()
        apply_moves(pref_state, case["preferred_moves"])

        recorded = describe(mol, rec_state[0, :size, :size].numpy())
        preferred = describe(mol, pref_state[0, :size, :size].numpy())
        if recorded is None or preferred is None:
            tally["reconstruction_failed"] += 1
            continue
        prefix = (len(case["preferred_moves"]) < len(case["recorded_moves"]) and
                  case["preferred_moves"] == case["recorded_moves"][:len(case["preferred_moves"])])
        tally["cases"] += 1
        tally["preferred_is_prefix_of_recorded"] += prefix
        tally["preferred_zwitterionic"] += preferred["zwitterionic"]
        tally["recorded_zwitterionic"] += recorded["zwitterionic"]
        tally["preferred_charged_at_all"] += preferred["abs_charge"] > 0
        tally["recorded_charged_at_all"] += recorded["abs_charge"] > 0
        tally["preferred_more_charged"] += preferred["abs_charge"] > recorded["abs_charge"]
        tally["preferred_has_radical"] += preferred["radical"] > 0
        tally["same_smiles"] += preferred["smiles"] == recorded["smiles"]
        rows.append({"stratum": case["stratum"], "n_atoms": case["n_atoms"], "prefix": prefix,
                     "logp_recorded": case["logp_recorded"], "logp_preferred": case["logp_preferred"],
                     "recorded": recorded, "preferred": preferred})

    strains = [(r["preferred"].get("energy_per_heavy"), r["recorded"].get("energy_per_heavy"))
               for r in rows if r["preferred"].get("energy_per_heavy") is not None
               and r["recorded"].get("energy_per_heavy") is not None]
    summary = dict(tally)
    if strains:
        summary["median_strain_preferred"] = round(median(p for p, _ in strains), 2)
        summary["median_strain_recorded"] = round(median(r for _, r in strains), 2)
        summary["preferred_more_strained"] = sum(1 for p, r in strains if p > r)
        summary["n_with_strain"] = len(strains)

    print(json.dumps(summary, indent=1))
    print()
    for r in rows:
        p, q = r["preferred"], r["recorded"]
        print(f"[{r['stratum']}] prefix={r['prefix']}  logp pref {r['logp_preferred']} vs rec {r['logp_recorded']}")
        print(f"   preferred: charge+{p['n_pos']}/-{p['n_neg']} zwitter={p['zwitterionic']} frags={p['n_frags']} {p['smiles'][:90]}")
        print(f"   recorded : charge+{q['n_pos']}/-{q['n_neg']} zwitter={q['zwitterionic']} frags={q['n_frags']} {q['smiles'][:90]}")
    json.dump({"summary": summary, "cases": rows}, open(args.out, "w"), indent=1)
    print("\nwrote", args.out)


if __name__ == "__main__":
    main()
