#!/usr/bin/env python
"""Are AFM's predicted intermediates chemically sane, or merely valence-legal?

The paper's own flagged limitation (`plan.md`'s P3.7, echoed in
`afm-decomposition-credibility-test`): AFM's mask guarantees every intermediate
along a mechanism is a *representable* molecule (right valence, right electron
count) -- but "valence-admissible is not chemically plausible". A real answer
needs DFT (the existing, not-yet-launched `specialty_11` NEB line). A *cheap*
proxy that doesn't need a checkpoint or GPU-hours at all: can each intermediate
even be embedded in 3D and locally energy-minimized with a standard force
field? A structure that fails at that stage (bad valence geometry, absurd
strain) is a bad DFT starting point regardless of what the mask says; one that
passes is a reasonable one to hand to real numerics.

This needs no trained model -- it walks the *chemist's own* move sequence
(``targets.json``, already verified admissible) and checks the molecules along
that one specific, human-endorsed path. Reused, not reimplemented:

* ``score_reactions.py``'s ``complete_atom_map`` / ``to_model_moves`` (the same
  atom-map completion and move-translation already validated there).
* ``models.afm.scatter_moves`` -- the model's own state-transition function.
* ``chem.product_smiles_from_be`` -- the model's own BE-matrix -> SMILES
  reconstruction, already used everywhere else in this repo to read out a
  candidate.
* RDKit's own ETKDG embedding + MMFF/UFF minimization -- standard cheminformatics,
  not written here.

Run (from this directory, no checkpoint needed)::

    .venv/bin/python intermediate_stability.py --limit 200
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem

# Importing this first runs its sys.path setup (ArrowFlowMatching/, analysis/),
# which the plain `import chem` / `models.afm` right after depend on.
from score_reactions import HERE, complete_atom_map, to_model_moves

import chem
from models.afm import scatter_moves

RDLogger.DisableLog("rdApp.*")


def stability_metrics(smiles: str) -> dict:
    """Embed in 3D and locally minimize with a standard force field.

    Returns whether RDKit could even parse/embed the structure, whether the
    force-field minimization converged, and the minimized energy per heavy atom
    (a rough strain proxy -- not a DFT-quality number, just a cheap ranking
    signal for "is this a reasonable optimizer/DFT starting point").
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return {"parses": False}
    n_heavy = mol.GetNumHeavyAtoms()
    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = 0xC0FFEE
    params.useRandomCoords = True
    if AllChem.EmbedMolecule(mol, params) != 0:
        return {"parses": True, "n_heavy": n_heavy, "embeds": False}
    energy, converged = None, None
    try:
        if AllChem.MMFFHasAllMoleculeParams(mol):
            props = AllChem.MMFFGetMoleculeProperties(mol)
            ff = AllChem.MMFFGetMoleculeForceField(mol, props)
        elif AllChem.UFFHasAllMoleculeParams(mol):
            ff = AllChem.UFFGetMoleculeForceField(mol)
        else:
            ff = None
        if ff is not None:
            converged = ff.Minimize(maxIts=500) == 0
            energy = ff.CalcEnergy()
    except Exception:  # noqa: BLE001 -- force-field failures are part of the measurement
        pass
    return {
        "parses": True, "n_heavy": n_heavy, "embeds": True,
        "ff_available": energy is not None, "converged": converged,
        "energy_per_heavy_atom": energy / n_heavy if energy and n_heavy else energy,
    }


def walk_intermediates(reactant_smiles: str, moves: list[list]) -> list[str] | None:
    """Reactant SMILES + chemist move sequence -> SMILES after every move.

    Excludes the reactant itself (not a prediction); includes the final product.
    """
    mapped_smiles, old_to_new = complete_atom_map(reactant_smiles)
    if mapped_smiles is None:
        return None
    mol = chem.mol_from_mapped_smiles(mapped_smiles)
    atom_index, be = chem.atom_types_and_be(mol)
    state = torch.as_tensor(be, dtype=torch.long).unsqueeze(0)
    move_tensor = to_model_moves(moves, old_to_new)

    smiles_by_step = []
    for t in range(move_tensor.shape[1]):
        kind, i, j = move_tensor[0, t]
        scatter_moves(state, kind.view(1), i.view(1), j.view(1), torch.ones(1, dtype=torch.bool))
        smiles = chem.product_smiles_from_be(mol, state[0].numpy())
        smiles_by_step.append(smiles)
    return smiles_by_step


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", default=str(HERE / "targets.json"))
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", default=str(HERE / "results" / "intermediate_stability.jsonl"))
    args = ap.parse_args()

    targets = json.load(open(args.targets))
    if args.limit:
        targets = targets[: args.limit]

    n_mid, n_final = 0, 0
    mid_embed_ok, mid_conv_ok = 0, 0
    final_embed_ok, final_conv_ok = 0, 0

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as out_fh:
        for idx, rec in enumerate(targets):
            try:
                smiles_by_step = walk_intermediates(rec["reactant"], rec["moves"])
            except Exception as exc:  # noqa: BLE001
                print(f"[{idx}] failed: {exc}")
                continue
            if smiles_by_step is None or any(not s for s in smiles_by_step):
                continue  # reconstruction itself failed somewhere on the path

            per_step = []
            for pos, smiles in enumerate(smiles_by_step):
                is_final = pos == len(smiles_by_step) - 1
                m = stability_metrics(smiles)
                m.update(smiles=smiles, position=pos, is_final=is_final)
                per_step.append(m)
                if is_final:
                    n_final += 1
                    final_embed_ok += m.get("embeds", False)
                    final_conv_ok += bool(m.get("converged"))
                else:
                    n_mid += 1
                    mid_embed_ok += m.get("embeds", False)
                    mid_conv_ok += bool(m.get("converged"))

            out_fh.write(json.dumps({"index": idx, "reactant": rec["reactant"], "steps": per_step}) + "\n")
            if (idx + 1) % 200 == 0:
                print(f"{idx + 1}/{len(targets)} processed")

    def pct(k, n):
        return 100 * k / n if n else float("nan")

    print(f"\nMid-mechanism intermediates: n={n_mid}  embed ok={pct(mid_embed_ok, n_mid):.1f}%  "
          f"FF-converged={pct(mid_conv_ok, n_mid):.1f}%")
    print(f"Final products:              n={n_final}  embed ok={pct(final_embed_ok, n_final):.1f}%  "
          f"FF-converged={pct(final_conv_ok, n_final):.1f}%")
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
