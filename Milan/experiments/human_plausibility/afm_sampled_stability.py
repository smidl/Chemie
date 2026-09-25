#!/usr/bin/env python
"""Is AFM's *trained model*, not just its alphabet, producing stable intermediates?

``intermediate_stability.py`` never touched ``afm_nano``'s weights at all -- it
applied `models.afm.scatter_moves` (pure state transition) along an admissible
move sequence found by the alphabet's own combinatorial search
(`analysis/decompose_steps.py`, no trained network), and reconstructed SMILES
(pure chemistry). That tested the alphabet's structural guarantee, not the
trained model's actual behaviour, and made the comparison against
``flower_discrete_stability.py`` (which *does* run trained weights, self-
sampled) not quite apples to apples.

This closes that gap: run ``afm_nano``'s own trained rollout (the same one
``mapped_candidates``/the alphabet-composition check use), reconstruct SMILES
at every self-generated step, and apply the identical embed/converge proxy.
Since the move mask is a structural property of the alphabet, applying to
*any* admissible sequence -- self-sampled or otherwise -- these numbers are
expected to land the same as the teacher-forced ones. That expectation is
exactly what should be checked, not asserted.

Run (from this directory)::

    .venv/bin/python afm_sampled_stability.py --limit 200 --num_chains 3
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch

from intermediate_stability import stability_metrics
from score_reactions import AFM_REPO, HERE, build_batch, complete_atom_map, load_model, sampled_intermediates


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", default=str(HERE / "multistep.json"),
                     help="Only the `reactant` field is used -- AFM generates its own path.")
    ap.add_argument("--ckpt", default=str(AFM_REPO / "outputs/runs/afm_nano/checkpoints/best.ckpt"))
    ap.add_argument("--emb_dim", type=int, default=128)
    ap.add_argument("--enc_filter_size", type=int, default=512)
    ap.add_argument("--num_chains", type=int, default=3)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", default=str(HERE / "results" / "afm_sampled_stability.jsonl"))
    args = ap.parse_args()

    targets = json.load(open(args.targets))
    if args.limit:
        targets = targets[: args.limit]

    model = load_model(Path(args.ckpt), args.emb_dim, args.enc_filter_size, model_name="afm")

    n_mid, n_final = 0, 0
    mid_recon, mid_embed, mid_conv = 0, 0, 0
    final_recon, final_embed, final_conv = 0, 0, 0

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as out_fh:
        for idx, rec in enumerate(targets):
            mapped_smiles, _ = complete_atom_map(rec["reactant"])
            if mapped_smiles is None:
                continue
            batch, _ = build_batch(mapped_smiles)
            source = model._source(batch)
            try:
                chains = sampled_intermediates(
                    model, batch["atom_ids"], batch["lengths"], source, batch["n_h"],
                    batch["reactant_mols"][0], args.num_chains,
                )
            except Exception as exc:  # noqa: BLE001
                print(f"[{idx}] failed: {exc}")
                continue

            per_chain = []
            for chain in chains:
                if not chain:
                    continue  # chain stopped immediately (0 moves) -- nothing to check
                per_step = []
                for pos, smiles in enumerate(chain):
                    which = "final" if pos == len(chain) - 1 else "mid"
                    if which == "mid":
                        n_mid += 1
                    else:
                        n_final += 1
                    if not smiles:
                        per_step.append({"position": pos, "reconstructs": False})
                        continue
                    if which == "mid":
                        mid_recon += 1
                    else:
                        final_recon += 1
                    m = stability_metrics(smiles)
                    m.update(smiles=smiles, position=pos, reconstructs=True)
                    per_step.append(m)
                    if which == "mid":
                        mid_embed += bool(m.get("embeds"))
                        mid_conv += bool(m.get("converged"))
                    else:
                        final_embed += bool(m.get("embeds"))
                        final_conv += bool(m.get("converged"))
                per_chain.append(per_step)

            out_fh.write(json.dumps({"index": idx, "reactant": rec["reactant"], "chains": per_chain}) + "\n")
            if (idx + 1) % 200 == 0:
                print(f"{idx + 1}/{len(targets)} processed")

    def pct(k, n):
        return 100 * k / n if n else float("nan")

    print(f"Mid-mechanism intermediates    n={n_mid:<6} reconstructs={pct(mid_recon, n_mid):5.1f}%  "
          f"embeds={pct(mid_embed, n_mid):5.1f}%  FF-converges={pct(mid_conv, n_mid):5.1f}%")
    print(f"Final products                 n={n_final:<6} reconstructs={pct(final_recon, n_final):5.1f}%  "
          f"embeds={pct(final_embed, n_final):5.1f}%  FF-converges={pct(final_conv, n_final):5.1f}%")
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
