#!/usr/bin/env python
"""Does matching FlowER's own input convention -- not a code patch, not a
retrain -- close the reconstruction gap?

``problem01-validity.md`` traced the ~14-22% mid-mechanism / ~47-51% final
reconstruction rates (``afm_sampled_stability.py``) to Remark 4's dropped
``n_i^H`` term (equation (1)): RMechDB reactants are fed in with most
hydrogens implicit, so ``beta_i`` -- computed everywhere in the code as a
plain row sum -- silently undercounts every atom carrying an implicit
hydrogen. Two fixes were considered: patch ``stop_mask``/``in_sector`` to add
``n_i^H`` back (a code change), or retrain. Checking the training corpus
found ``n_i^H`` is 0 for every training step already: FlowER's own data has
*every* hydrogen mapped as its own explicit atom (exactly what Remark 4 says),
which is why the row-sum shortcut was safe there and only breaks on inputs
that don't share that convention. That makes retraining a no-op, and points
at a third fix that touches neither code nor weights: make new data conform
to the convention the checkpoint already expects.

This script does that and nothing else. ``fully_explicit_atom_map`` runs
``Chem.AddHs`` on the RMechDB reactant and gives every atom -- hydrogens
included -- its own contiguous map number, so ``n_i^H`` is 0 by construction,
the same as in training. Everything downstream -- model loading, the
self-sampled rollout, the embed/converge proxy -- is the *unmodified*
``models/afm.py``/``afm_nano`` checkpoint this repo already ships; no line of
model code changes and no retraining happens. Compare the printed rates
against ``afm_sampled_stability.py``'s (same targets, RMechDB's own partial
mapping, implicit hydrogens) to see how much of the gap the input convention
alone explains.

Run (from this directory)::

    .venv/bin/python fully_explicit_stability.py --limit 200 --num_chains 3
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch
from rdkit import Chem, RDLogger

from intermediate_stability import stability_metrics
from score_reactions import AFM_REPO, HERE, load_model

sys.path.insert(0, str(AFM_REPO))
RDLogger.DisableLog("rdApp.*")

import chem  # noqa: E402
from models.afm import NUM_MOVES, _sample_step, scatter_moves  # noqa: E402

_PS = Chem.SmilesParserParams()
_PS.removeHs = False
_PS.sanitize = True


def fully_explicit_atom_map(reactant_smiles: str) -> str | None:
    """RMechDB reactant (reacting atoms mapped, hydrogens implicit) -> every
    atom, hydrogens included, its own contiguous map number -- FlowER's own
    convention (Remark 4), under which ``n_i^H`` is 0 for every atom and
    ``beta_i`` (a plain row sum everywhere in the code) is exactly right.

    Spectator atoms and hydrogens don't change identity across the step, so
    any fixed 1..N numbering of *this* molecule is self-consistent; nothing
    needs matching against a product or an old RMechDB map number, unlike
    ``score_reactions.complete_atom_map``.
    """
    mol = Chem.MolFromSmiles(reactant_smiles, _PS)
    if mol is None:
        return None
    mol = Chem.AddHs(mol)
    for atom in mol.GetAtoms():
        atom.SetAtomMapNum(atom.GetIdx() + 1)
    return Chem.MolToSmiles(mol, canonical=False)


def build_batch(mapped_smiles: str):
    mol = chem.mol_from_mapped_smiles(mapped_smiles)
    atom_index, be = chem.atom_types_and_be(mol)
    n_h = chem.atom_n_hydrogens(mol) if hasattr(chem, "atom_n_hydrogens") else None
    n = len(atom_index)
    batch = {
        "src": torch.as_tensor(be, dtype=torch.float32).unsqueeze(0),
        "lengths": torch.tensor([n]),
        "atom_ids": torch.as_tensor(atom_index, dtype=torch.long).unsqueeze(0),
        "reactant_mols": [mol],
    }
    return batch, n_h


@torch.no_grad()
def sampled_intermediates(model, atom_ids, lengths, source, reactant_mol, width: int) -> list[list[str]]:
    """Unmodified rollout loop (mirrors ``ArrowFlowMatching._rollout``, sample
    decode only): no ``n_h`` argument anywhere, because this checkout's
    ``_score``/``stop_mask`` take none -- the whole point of this script is
    that the *unpatched* code, given data in the convention it was trained on,
    needs none.
    """
    assert model.hparams.decode == "sample", "beam decode reorders slots; not handled here"
    rows = width
    atom_ids = atom_ids.repeat_interleave(width, dim=0)
    lengths = lengths.repeat_interleave(width, dim=0)
    source = source.repeat_interleave(width, dim=0)
    n = source.shape[-1]

    state = source.clone()
    score = torch.zeros(rows)
    done = torch.zeros(rows, dtype=torch.bool)
    step = torch.zeros(rows)
    chains: list[list[str]] = [[] for _ in range(rows)]
    for _ in range(model.max_moves):
        log_probs = model._score(atom_ids, lengths, state, source, step)
        choice, score, _ = _sample_step(log_probs, score, done, width)
        kind, rest = choice // (n * n), choice % (n * n)
        live = ~done & (choice != NUM_MOVES * n * n)
        scatter_moves(state, kind, rest // n, rest % n, live)
        step = step + live.float()
        done = ~live
        for row in range(rows):
            if live[row]:
                size = int(lengths[row].item())
                chains[row].append(chem.product_smiles_from_be(reactant_mol, state[row, :size, :size].numpy()))
        if bool(done.all()):
            break
    return chains


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", default=str(HERE / "multistep.json"),
                     help="Only the `reactant` field is used -- AFM generates its own path.")
    ap.add_argument("--ckpt", default=str(AFM_REPO / "outputs/runs/afm_nano/checkpoints/best.ckpt"))
    ap.add_argument("--emb_dim", type=int, default=128)
    ap.add_argument("--enc_filter_size", type=int, default=512)
    ap.add_argument("--num_chains", type=int, default=3)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", default=str(HERE / "results" / "fully_explicit_stability.jsonl"))
    args = ap.parse_args()

    targets = json.load(open(args.targets))
    if args.limit:
        targets = targets[: args.limit]

    model = load_model(Path(args.ckpt), args.emb_dim, args.enc_filter_size, model_name="afm")

    n_mid, n_final = 0, 0
    mid_recon, mid_embed, mid_conv = 0, 0, 0
    final_recon, final_embed, final_conv = 0, 0, 0
    n_h_nonzero, n_excluded = 0, 0

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as out_fh:
        for idx, rec in enumerate(targets):
            mapped_smiles = fully_explicit_atom_map(rec["reactant"])
            if mapped_smiles is None:
                n_excluded += 1
                continue
            batch, n_h = build_batch(mapped_smiles)
            if n_h is not None:
                n_h_nonzero += int((n_h != 0).sum())
            source = model._source(batch)
            try:
                chains = sampled_intermediates(
                    model, batch["atom_ids"], batch["lengths"], source,
                    batch["reactant_mols"][0], args.num_chains,
                )
            except Exception as exc:  # noqa: BLE001
                n_excluded += 1
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

    print(f"Excluded (parse/rollout failure): {n_excluded}")
    print(f"n_h nonzero atoms across all processed reactants (expect 0): {n_h_nonzero}")
    print(f"Mid-mechanism intermediates    n={n_mid:<6} reconstructs={pct(mid_recon, n_mid):5.1f}%  "
          f"embeds={pct(mid_embed, n_mid):5.1f}%  FF-converges={pct(mid_conv, n_mid):5.1f}%")
    print(f"Final products                 n={n_final:<6} reconstructs={pct(final_recon, n_final):5.1f}%  "
          f"embeds={pct(final_embed, n_final):5.1f}%  FF-converges={pct(final_conv, n_final):5.1f}%")
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
