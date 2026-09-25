#!/usr/bin/env python
"""Is entrywise random interpolation itself prone to invalid states -- even
when guided by the true product, not a model's guess?

``flower_discrete_stability.py`` found DiscreteFlowER's *self-generated*
intermediates fail to reconstruct to any valid molecule >50% of the time.
That is confounded: is the cause the model's own imperfect predictions (it
guesses the wrong endpoint, and resampling toward a wrong target produces
nonsense), or is it the *representation* -- resampling a random subset of
matrix entries toward any endpoint, even the correct one -- that is inherently
prone to this, independent of model quality? Only the second reading supports
the paper's argument that AFM's move-alphabet construction is doing something
representationally better, not just "our model happened to train better."

This isolates it: no model, no checkpoint. Take the reactant and the *true*
product bond-electron matrix for a reaction (computed by applying the
alphabet's own admissible move sequence -- ``multistep.json``, same as
``intermediate_stability.py`` -- to the reactant; a mechanical calculation, not
a model prediction), and run DiscreteFlowER's own forward noising schedule
(``DiscreteFlowER.training_loss``'s ``flip = symmetrize(rand < t)``, walked
progressively the way its inference loop does: ``h / (1 - i*h)`` at each step,
see ``mapped_candidates``) with the *true* product standing in for the
model's guessed endpoint at every step. Reconstruct and stability-check each
intermediate exactly as before.

Run (from this directory, no checkpoint needed)::

    .venv/bin/python entrywise_interpolation_stability.py --limit 200
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import torch

from intermediate_stability import stability_metrics
from score_reactions import HERE, complete_atom_map, to_model_moves

import chem
from models.afm import scatter_moves
from models.flower_discrete import _symmetrize


def true_product_matrix(reactant_smiles: str, moves: list[list]) -> tuple[object, "torch.Tensor"] | None:
    """Reactant SMILES + an admissible move sequence -> (reactant_mol, product BE matrix).

    Purely mechanical -- applies each move with `scatter_moves`, the same
    state-transition function the model itself uses, no network involved.
    """
    mapped_smiles, old_to_new = complete_atom_map(reactant_smiles)
    if mapped_smiles is None:
        return None
    mol = chem.mol_from_mapped_smiles(mapped_smiles)
    atom_index, be = chem.atom_types_and_be(mol)
    state = torch.as_tensor(be, dtype=torch.long).unsqueeze(0)
    move_tensor = to_model_moves(moves, old_to_new)
    for t in range(move_tensor.shape[1]):
        kind, i, j = move_tensor[0, t]
        scatter_moves(state, kind.view(1), i.view(1), j.view(1), torch.ones(1, dtype=torch.bool))
    return mol, state[0]


@torch.no_grad()
def interpolation_chain(source: "torch.Tensor", target: "torch.Tensor", flow_steps: int) -> "torch.Tensor":
    """One stochastic reveal path from `source` to `target`, DiscreteFlowER's own
    schedule (``h / (1 - i*h)`` per step), returning the state after every step.
    """
    n = source.shape[-1]
    h = 1.0 / flow_steps
    x = source.clone().unsqueeze(0)
    tgt = target.unsqueeze(0)
    states = []
    for i in range(flow_steps - 1):
        flip = _symmetrize(torch.rand(1, n, n) < h / (1.0 - i * h))
        x = torch.where(flip, tgt, x)
        states.append(x[0].clone())
    states.append(target.clone())  # by construction, t=1 reveals everything
    return states


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", default=str(HERE / "multistep.json"))
    ap.add_argument("--flow_steps", type=int, default=10, help="Matches flower_discrete_nano's own hyperparameter.")
    ap.add_argument("--num_chains", type=int, default=3)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", default=str(HERE / "results" / "entrywise_interpolation_stability.jsonl"))
    args = ap.parse_args()

    targets = json.load(open(args.targets))
    if args.limit:
        targets = targets[: args.limit]

    tiers = {"mid": Counter(), "final": Counter()}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as out_fh:
        for idx, rec in enumerate(targets):
            got = true_product_matrix(rec["reactant"], rec["moves"])
            if got is None:
                continue
            mol, target = got
            try:
                source = chem.atom_types_and_be(mol)[1]
                source = torch.as_tensor(source, dtype=torch.long)
            except Exception as exc:  # noqa: BLE001
                print(f"[{idx}] failed: {exc}")
                continue

            per_chain = []
            for _ in range(args.num_chains):
                states = interpolation_chain(source, target, args.flow_steps)
                per_step = []
                for pos, state in enumerate(states):
                    which = "final" if pos == len(states) - 1 else "mid"
                    tiers[which]["n"] += 1
                    smiles = chem.product_smiles_from_be(mol, state.numpy())
                    if not smiles:
                        per_step.append({"position": pos, "reconstructs": False})
                        continue
                    tiers[which]["reconstructs"] += 1
                    m = stability_metrics(smiles)
                    m.update(smiles=smiles, position=pos, reconstructs=True)
                    per_step.append(m)
                    tiers[which]["embeds"] += bool(m.get("embeds"))
                    tiers[which]["converges"] += bool(m.get("converged"))
                per_chain.append(per_step)

            out_fh.write(json.dumps({"index": idx, "reactant": rec["reactant"], "chains": per_chain}) + "\n")
            if (idx + 1) % 200 == 0:
                print(f"{idx + 1}/{len(targets)} processed")

    def pct(k, n):
        return 100 * k / n if n else float("nan")

    for label, key in (("Mid-mechanism intermediates", "mid"), ("Final products", "final")):
        c = tiers[key]
        n = c["n"]
        print(f"{label:<30} n={n:<6} reconstructs={pct(c['reconstructs'], n):5.1f}%  "
              f"embeds={pct(c['embeds'], n):5.1f}%  FF-converges={pct(c['converges'], n):5.1f}%")
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
