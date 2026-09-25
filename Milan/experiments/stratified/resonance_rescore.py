#!/usr/bin/env python
"""Score a stratum twice: exactly as the paper does, and again up to resonance.

The metric compares the emitted product with the record as a canonical,
atom-map-free string. Aromatic rings are Kekule-resolved before the matrix is
built, so a delocalised ion -- an arenium cation, a Meisenheimer carbanion --
has several matrix representations that RDKit writes as different strings while
a chemist reads them as one species. Characterising the disputed long steps
found exactly that: of twelve, seven gave an identical string and four more were
resonance structures of one ion.

That is a property of the metric, not of a model, so it is measured here for
every model on the same steps and reported next to the strict number rather
than instead of it. Resonance structures are enumerated only when the strict
comparison fails, and only by RDKit's own supplier.

    python resonance_rescore.py --model afm --name afm_nano --ckpt <best.ckpt> \\
        --files <strata>/test_m6plus.txt --limit 2000 --out rescore.json
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import torch
from rdkit import Chem, RDLogger
from rdkit.Chem import rdchem

import compat_flower_cons  # noqa: F401
import hydra
import models  # noqa: F401
from data import read_steps

RDLogger.DisableLog("rdApp.*")
FLAGS = rdchem.ResonanceFlags.ALLOW_CHARGE_SEPARATION | rdchem.ResonanceFlags.KEKULE_ALL


def canonical(smiles: str):
    """Canonical, atom-map-free -- the string the evaluation compares."""
    if not smiles:
        return None
    mol = Chem.MolFromSmiles(smiles, sanitize=False)
    if mol is None:
        return None
    for atom in mol.GetAtoms():
        atom.SetAtomMapNum(0)
    try:
        Chem.SanitizeMol(mol)
    except Exception:  # noqa: BLE001
        return None
    return Chem.MolToSmiles(mol)


def resonance_keys(smiles: str, cap: int = 32):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return set()
    keys = {Chem.MolToSmiles(mol)}
    try:
        for structure in rdchem.ResonanceMolSupplier(mol, FLAGS, maxStructs=cap):
            if structure is None:
                continue
            written = Chem.MolToSmiles(structure)
            reread = Chem.MolFromSmiles(written)
            keys.add(Chem.MolToSmiles(reread) if reread is not None else written)
    except Exception:  # noqa: BLE001
        pass
    return {k for k in keys if k}


def same_species(a: str, b: str, cache: dict):
    if a == b:
        return True
    for key in (a, b):
        if key not in cache:
            cache[key] = resonance_keys(key)
    return bool(cache[a] & cache[b])


def load(model_group, ckpt, emb_dim, filt, config_dir):
    with hydra.initialize_config_dir(config_dir=config_dir, version_base=None):
        overrides = [f"model={model_group}", f"model.emb_dim={emb_dim}",
                     f"model.enc_filter_size={filt}", "model.decode=sample",
                     "model.ranking=frequency"]
        cfg = hydra.compose(config_name="default_eval", overrides=overrides)
    model = hydra.utils.instantiate(cfg.model)
    model.load_state_dict(torch.load(ckpt, map_location="cpu", weights_only=False)["state_dict"],
                          strict=True)
    collate = hydra.utils.instantiate(cfg.model.collate_fn)
    return model.eval(), collate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, help="hydra model group: afm | flower_discrete | flower")
    ap.add_argument("--name", required=True)
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--limit", type=int, default=2000)
    ap.add_argument("--samples", type=int, default=10)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--max_atoms", type=int, default=120,
                     help="skip larger reactants, identically for every model")
    ap.add_argument("--emb_dim", type=int, default=128)
    ap.add_argument("--enc_filter_size", type=int, default=512)
    ap.add_argument("--config_dir", default=str(Path.cwd() / "configs"))
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    model, collate = load(args.model, args.ckpt, args.emb_dim, args.enc_filter_size, args.config_dir)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(device)

    out = {}
    for path in args.files:
        name = Path(path).stem
        steps = read_steps(path, limit=args.limit)
        # Models differ in where memory pressure bites, so dropping on failure
        # would score each on its own, easier subset. Size is capped up front
        # instead, identically for every model, and the per-step outcome is
        # written out so the populations can be intersected rather than trusted.
        if args.max_atoms:
            kept = []
            for step in steps:
                mol = Chem.MolFromSmiles(step[0], sanitize=False)
                if mol is not None and mol.GetNumAtoms() <= args.max_atoms:
                    kept.append(step)
            steps = kept
        cache, tally, per_step_rows = {}, Counter(), []
        def run(chunk):
            """Candidates for a chunk; on memory pressure, split rather than drop.

            Dropping a failed batch would silently remove the largest molecules,
            and the models differ in where that bites -- which would bias the
            comparison this script exists to make. Steps are only abandoned
            singly, and counted when they are.
            """
            try:
                batch = collate(chunk)
                batch = {k: (v.to(device) if torch.is_tensor(v) else v) for k, v in batch.items()}
                with torch.no_grad():
                    return list(zip(chunk, model.mapped_candidates(batch, args.samples)))
            except torch.OutOfMemoryError:
                torch.cuda.empty_cache()
                if len(chunk) == 1:
                    tally["dropped_steps_oom"] += 1
                    return []
                half = len(chunk) // 2
                return run(chunk[:half]) + run(chunk[half:])
            except Exception as exc:  # noqa: BLE001
                if len(chunk) == 1:
                    tally["dropped_steps_error"] += 1
                    print("step failed:", exc, flush=True)
                    return []
                half = len(chunk) // 2
                return run(chunk[:half]) + run(chunk[half:])

        for start in range(0, len(steps), args.batch):
            for step, per_step in run(steps[start:start + args.batch]):
                truth = canonical(step[1])
                if truth is None:
                    continue
                counts = Counter()
                for smiles, _ in per_step:
                    key = canonical(smiles)
                    if key:
                        counts[key] += 1
                if not counts:
                    tally["no_candidate"] += 1
                    tally["scored"] += 1
                    continue
                ranked = [k for k, _ in counts.most_common()]
                strict = ranked[0] == truth
                resonant = same_species(ranked[0], truth, cache)
                tally["scored"] += 1
                tally["top1_strict"] += strict
                tally["top1_resonance"] += resonant
                tally["topk_strict"] += truth in ranked
                tally["topk_resonance"] += any(same_species(k, truth, cache) for k in ranked)
                per_step_rows.append({"reactant": step[0], "strict": bool(strict),
                                      "resonance": bool(resonant)})
        n = tally["scored"] or 1
        out[name] = {
            "n": tally["scored"],
            "top1_strict": round(tally["top1_strict"] / n, 4),
            "top1_up_to_resonance": round(tally["top1_resonance"] / n, 4),
            "topk_strict": round(tally["topk_strict"] / n, 4),
            "topk_up_to_resonance": round(tally["topk_resonance"] / n, 4),
            "recovered_by_resonance": round((tally["top1_resonance"] - tally["top1_strict"]) / n, 4),
            "counts": dict(tally),
            "per_step": per_step_rows,
        }
        print(args.name, name, json.dumps(out[name]), flush=True)
    json.dump({args.name: out}, open(args.out, "w"), indent=1)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
