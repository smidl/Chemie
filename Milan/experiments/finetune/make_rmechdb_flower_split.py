#!/usr/bin/env python
"""RMechDB chemist steps -> FlowER-format dataset for fine-tuning AFM.

Writes ``train.txt / val.txt / test.txt`` in the released data format
(``reactant>>product|seq_idx``, every atom -- hydrogens included -- mapped,
see ``data.py::_parse_line`` and Remark "the dataset makes every hydrogen its
own atom") from the two alphabet-expressible RMechDB target files of the
human-plausibility experiment (``targets.json``: single-move steps,
``multistep.json``: multi-move steps). The reactant is put in FlowER's
convention by ``fully_explicit_atom_map``; the product is *constructed* by
applying the chemist's own moves to that matrix (``scatter_moves``) and
written back with the repo's own ``product_mapped_smiles_from_be``, so the
pair is exactly the step the chemist drew, in the model's own numbering.

Split: grouped by the canonical, map-free reactant SMILES and assigned
80/10/10 by a seeded shuffle of the groups, so a reactant with several
recorded products (RMechDB branches) never straddles train and test. The
held-out ``test.txt`` is the only split the human-comparison may be scored
on after fine-tuning. ``manifest.json`` records, per written line, its
source file, index and RMechDB meta.

    .venv/bin/python make_rmechdb_flower_split.py --out data/rmechdb_ft
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import torch
from rdkit import Chem, RDLogger

HERE = Path(__file__).resolve().parent
HP = HERE.parent / "human_plausibility"
sys.path.insert(0, str(HP))
from fully_explicit_stability import build_batch, fully_explicit_atom_map  # noqa: E402
from score_reactions import AFM_REPO, complete_atom_map, to_model_moves  # noqa: E402

sys.path.insert(0, str(AFM_REPO))
RDLogger.DisableLog("rdApp.*")
import chem  # noqa: E402
from models.afm import scatter_moves  # noqa: E402


def canonical(smiles: str) -> str | None:
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    for a in mol.GetAtoms():
        a.SetAtomMapNum(0)
    return Chem.MolToSmiles(mol)


def convert(entry: dict, source: str, index: int):
    mapped = fully_explicit_atom_map(entry["reactant"])
    _, old_to_new = complete_atom_map(entry["reactant"])
    if mapped is None:
        return None, "reactant unparsable"
    try:
        moves = to_model_moves(entry["moves"], old_to_new)[0]
    except KeyError:
        return None, "chemist move names an atom not in the parse"
    batch, _ = build_batch(mapped)
    mol = batch["reactant_mols"][0]
    size = int(batch["lengths"][0])
    state = batch["src"].long().clone()
    for k, i, j in moves.tolist():
        scatter_moves(state, torch.tensor([k]), torch.tensor([i]), torch.tensor([j]), torch.ones(1, dtype=torch.bool))
    product = chem.product_mapped_smiles_from_be(mol, state[0, :size, :size].numpy())
    if not product:
        return None, "product does not reconstruct"
    # round trip: the product must re-featurise to the matrix that produced it
    try:
        pm = chem.mol_from_mapped_smiles(product)
        _, be = chem.atom_types_and_be(pm)
    except Exception:  # noqa: BLE001
        return None, "product does not re-parse"
    if be.shape[0] != size or (be.astype(int) != state[0, :size, :size].numpy()).any():
        return None, "product round-trip mismatch"
    return {
        "reactant": mapped, "product": product,
        "group": canonical(entry["reactant"]),
        "pair": (canonical(entry["reactant"]), canonical(product)),
        "source": source, "index": index, "meta": entry.get("meta"), "n_moves": len(entry["moves"]),
    }, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE / "data" / "rmechdb_ft"))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--frac", type=float, nargs=3, default=(0.8, 0.1, 0.1))
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    # Deduplication rule, changed 2026-09-21. Previously: keep the FIRST entry
    # for a (reactant, product) pair, iterating targets.json before
    # multistep.json. That silently preferred whichever drawing came first, and
    # since RMechDB annotates the same transformation twice at different
    # mechanistic granularity in 207 rows -- one chemist drawing a single arrow
    # where another draws the whole concerted flow -- it systematically kept the
    # SHORTER explanation, which is the failure mode the fine-tune exists to
    # repair.
    #
    # Now: among the entries for one pair, keep the one with the most moves,
    # preferring a chemist-MATCHED decomposition (targets.json, whose moves
    # expand to the curated arrows) over an arbitrary admissible one
    # (multistep.json, "whichever the search returned first"). Rank is
    # (is_chemist_matched, n_moves), maximised; insertion order breaks ties, so
    # the result is deterministic.
    rows, dropped, best = [], Counter(), {}
    _seen_moves = defaultdict(list)
    for source in ("targets.json", "multistep.json"):
        for index, entry in enumerate(json.load(open(HP / source))):
            row, why = convert(entry, source, index)
            if row is None:
                dropped[why] += 1
                continue
            _seen_moves[row["pair"]].append(row["n_moves"])
            rank = (row["source"] == "targets.json", row["n_moves"])
            prev = best.get(row["pair"])
            if prev is None:
                best[row["pair"]] = (rank, row)
                continue
            dropped["duplicate (reactant, product)"] += 1
            if rank > prev[0]:
                best[row["pair"]] = (rank, row)
                dropped["duplicate resolved in favour of the LONGER drawing"] += 1
    rows = [r for _, r in best.values()]
    # diagnostic: how often did a pair actually offer drawings of different length?
    spread = Counter()
    for key, moves in _seen_moves.items():
        if len(set(moves)) > 1:
            spread["pairs offering different move counts"] += 1
            spread[f"  min {min(moves)} -> kept {best[key][1]['n_moves']} (max {max(moves)})"] += 1
    dropped.update(spread)

    groups = defaultdict(list)
    for r in rows:
        groups[r["group"]].append(r)
    keys = sorted(groups)
    random.Random(args.seed).shuffle(keys)
    n = len(keys)
    cut1 = int(args.frac[0] * n)
    cut2 = cut1 + int(args.frac[1] * n)
    assign = {}
    for pos, k in enumerate(keys):
        assign[k] = "train" if pos < cut1 else "val" if pos < cut2 else "test"

    manifest = {"seed": args.seed, "dropped": dict(dropped), "splits": {}}
    for split in ("train", "val", "test"):
        lines = [r for r in rows if assign[r["group"]] == split]
        with open(out / f"{split}.txt", "w") as fh:
            for seq, r in enumerate(lines):
                fh.write(f"{r['reactant']}>>{r['product']}|{seq}\n")
        manifest["splits"][split] = {
            "n": len(lines),
            "n_reactant_groups": len({r["group"] for r in lines}),
            "n_moves": dict(Counter(r["n_moves"] for r in lines)),
            "classes": dict(Counter(r["meta"][2] if r["meta"] else None for r in lines)),
            "stages": dict(Counter(r["meta"][1] if r["meta"] else None for r in lines)),
            "lines": [{"seq": seq, "source": r["source"], "index": r["index"], "meta": r["meta"], "n_moves": r["n_moves"]}
                      for seq, r in enumerate(lines)],
        }
    json.dump(manifest, open(out / "manifest.json", "w"), indent=1)
    print(f"kept {len(rows)} steps in {len(groups)} reactant groups; dropped: {dict(dropped)}")
    for split, s in manifest["splits"].items():
        print(f"  {split:<5} n={s['n']:<5} groups={s['n_reactant_groups']:<5} n_moves={s['n_moves']}  classes={s['classes']}")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
