#!/usr/bin/env python
"""Does AFM's valence mask actually matter, or would any model's intermediates
look this stable anyway?

`intermediate_stability.py` found AFM's alphabet-admissible intermediates
(walking the chemist's own verified move sequence) are, by a cheap RDKit
embed/force-field proxy, statistically indistinguishable from its final
products (~100% embed, ~98% FF-converge, both mid-mechanism and final). That
is consistent with the mask mattering -- but also consistent with "cheap
force-field checks pass on almost anything small enough to be a plausible
molecule regardless of how it was built." This is the control that tells the
two apart.

``DiscreteFlowER`` (``models/flower_discrete.py``) is the natural baseline:
same body, same bond-electron-matrix representation, same paper, but its
per-step intermediates carry **no admissibility guarantee at all** -- each
Euler step just resamples a random subset of matrix entries to the model's
predicted endpoint value, with nothing masking off a chemically nonsensical
partial state. If its intermediates score just as well as AFM's, the earlier
result says more about the cheap proxy's ceiling than about AFM's mask. If
they score worse, that is direct evidence the mask is doing real work, not
merely papering over what a force field would have accepted anyway.

Since DiscreteFlowER has no move alphabet, there is no chemist-verified path to
walk it through (unlike ``intermediate_stability.py``); instead each reactant's
own self-generated Euler chain is used -- the model's *own* mechanism, the only
kind of path it can produce at all.

Run (from this directory)::

    .venv/bin/python flower_discrete_stability.py --limit 200 --num_chains 3
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import torch

from fully_explicit_stability import build_batch, fully_explicit_atom_map
from instrumented_rollout import flower_reactants
from intermediate_stability import stability_metrics
from score_reactions import AFM_REPO, HERE, load_model

import chem
from models.flower_discrete import _perturb, _symmetrize


@torch.no_grad()
def self_generated_intermediates(model, batch, num_chains: int) -> list[list[str]]:
    """One reactant -> ``num_chains`` independent Euler chains, each a list of
    reconstructed SMILES, one per flow step (last entry = final product).

    A close copy of ``DiscreteFlowER.mapped_candidates``'s own loop -- same
    ``_integer_matrices``, ``encoder``, ``_endpoint``/``_perturb``, resample-
    probability schedule -- except every step's state is reconstructed to
    SMILES here (``mapped_candidates`` only keeps the last one), and chains run
    one at a time rather than batched, since this needs each step, not just the
    endpoint score.
    """
    source, node_mask, pair_mask, off_mask = model._integer_matrices(batch)
    b, n, _ = source.shape
    assert b == 1
    reactant_mol = batch["reactant_mols"][0]
    h = 1.0 / model.flow_steps

    chains = []
    for _ in range(num_chains):
        x = source.clone()
        atom_emb = model.encoder.embed_atoms(batch["atom_ids"])
        steps = []
        for i in range(model.flow_steps - 1):
            t = torch.full((b,), i * h)
            bond_logits, lone_logits = model.encoder(
                batch["atom_ids"], batch["lengths"], x, source, t, atom_emb=atom_emb
            )
            endpoint = model._endpoint(_perturb(bond_logits), _perturb(lone_logits))
            flip = _symmetrize(torch.rand(b, n, n) < h / (1.0 - i * h))
            x = torch.where(flip, endpoint, x)
            steps.append(chem.product_smiles_from_be(reactant_mol, x[0].numpy()))
        t = torch.full((b,), 1.0 - h)
        bond_logits, lone_logits = model.encoder(
            batch["atom_ids"], batch["lengths"], x, source, t, atom_emb=atom_emb
        )
        x = model._endpoint(bond_logits, lone_logits)
        steps.append(chem.product_smiles_from_be(reactant_mol, x[0].numpy()))
        chains.append(steps)
    return chains


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", default=str(HERE / "multistep.json"),
                     help="Only the `reactant` field is used -- DiscreteFlowER generates its own path.")
    ap.add_argument("--ckpt", default=str(AFM_REPO / "outputs/runs/flower_discrete_nano/checkpoints/best.ckpt"))
    ap.add_argument("--emb_dim", type=int, default=128)
    ap.add_argument("--enc_filter_size", type=int, default=512)
    ap.add_argument("--num_chains", type=int, default=3)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--flower_txt", default=None,
                     help="If given, run on FlowER's own (already fully mapped) reactants instead of RMechDB.")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.flower_txt:
        targets = [{"reactant": r} for r in flower_reactants(Path(args.flower_txt), args.limit)]
        preprocess = lambda s: s  # noqa: E731 -- every atom mapped already, hydrogens included
        out_path = Path(args.out) if args.out else HERE / "results" / "flower_discrete_stability_flower.jsonl"
    else:
        targets = json.load(open(args.targets))
        if args.limit:
            targets = targets[: args.limit]
        # Same input convention as the AFM runs it is compared against.
        preprocess = fully_explicit_atom_map
        out_path = Path(args.out) if args.out else HERE / "results" / "flower_discrete_stability.jsonl"
    args.out = str(out_path)

    model = load_model(Path(args.ckpt), args.emb_dim, args.enc_filter_size, model_name="flower_discrete")

    # Unlike `intermediate_stability.py` (AFM's mask makes reconstruction failure
    # impossible by construction, so a chain-level skip on any failure cost
    # ~1.4% of reactions), a step here can fail to reconstruct to *any* molecule
    # at all -- and that is exactly the outcome this ablation exists to measure,
    # not noise to discard. Every step of every chain is counted, in three tiers:
    # reconstructs at all -> embeds in 3D -> force-field converges.
    tiers = {"mid": Counter(), "final": Counter()}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as out_fh:
        for idx, rec in enumerate(targets):
            mapped_smiles = preprocess(rec["reactant"])
            if mapped_smiles is None:
                continue
            batch, _ = build_batch(mapped_smiles)
            try:
                chains = self_generated_intermediates(model, batch, args.num_chains)
            except Exception as exc:  # noqa: BLE001
                print(f"[{idx}] failed: {exc}")
                continue

            per_chain = []
            for chain in chains:
                per_step = []
                for pos, smiles in enumerate(chain):
                    which = "final" if pos == len(chain) - 1 else "mid"
                    tiers[which]["n"] += 1
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
