#!/usr/bin/env python
"""How much of each stratum is resonance bookkeeping rather than chemistry?

Aromatic rings are Kekule-resolved before the matrix is built, so a step may
move bond orders around a delocalised system -- a charge pushed to another
position of an arenium ion, a Kekule shuffle -- and change the bond-electron
matrix while leaving the *molecule* unchanged. The corpus counts 18.5% of steps
as identity, but that is matrix identity; molecule identity is a weaker and
larger condition.

This matters for reading the stratified evaluation, because the metric compares
canonical, atom-map-free SMILES. On a step whose product is the same molecule
as its reactant, a model with a copy prior is right by doing nothing, while a
model that must construct the product by moves has to find its way back. And on
a step whose product is one arbitrary resonance form, a model that emits a
different form of the same species is marked wrong.

Reports per stratum: steps whose product equals the reactant as a molecule,
steps whose matrices differ but whose molecules do not, and the share of
multi-move steps among them.

  python resonance_share.py --files <strata>/test_m6plus.txt ... --out resonance.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from multiprocessing import Pool

from rdkit import Chem, RDLogger

AFM_REPO = os.environ.get("AFM_REPO", os.path.expanduser("~/ArrowFlowMatching"))
sys.path.insert(0, AFM_REPO)
import chem  # noqa: E402

RDLogger.DisableLog("rdApp.*")


def canonical(smiles: str):
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        return None
    for a in mol.GetAtoms():
        a.SetAtomMapNum(0)
    return Chem.MolToSmiles(mol)


def analyse(line: str):
    head = line.strip().split("|")[0]
    if ">>" not in head:
        return None
    src, _, dst = head.partition(">>")
    out = Counter()
    out["steps"] += 1
    cr, cp = canonical(src), canonical(dst)
    if cr is None or cp is None:
        out["unparsed"] += 1
        return out
    # matrix identity, the corpus's own notion
    try:
        _, br = chem.atom_types_and_be(chem.mol_from_mapped_smiles(src))
        _, bp = chem.atom_types_and_be(chem.mol_from_mapped_smiles(dst))
        matrix_same = (br == bp).all()
    except Exception:  # noqa: BLE001
        matrix_same = None
    if cr == cp:
        out["molecule_identity"] += 1
        if matrix_same is False:
            out["molecule_same_matrix_differs"] += 1  # resonance / Kekule bookkeeping
    if matrix_same:
        out["matrix_identity"] += 1
    return out


def run(job):
    path, start, end = job
    stats = Counter()
    with open(path) as fh:
        fh.seek(start)
        if start:
            fh.readline()
        while fh.tell() < end:
            line = fh.readline()
            if not line:
                break
            a = analyse(line)
            if a:
                stats.update(a)
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out = {}
    for path in args.files:
        size = os.path.getsize(path)
        step = max(1, size // args.workers)
        jobs = [(path, k, min(k + step, size)) for k in range(0, size, step)]
        stats = Counter()
        with Pool(args.workers) as pool:
            for s in pool.imap_unordered(run, jobs):
                stats.update(s)
        n = stats["steps"] or 1
        out[os.path.basename(path)] = {
            "steps": stats["steps"],
            "molecule_identity_pct": round(100 * stats["molecule_identity"] / n, 2),
            "matrix_identity_pct": round(100 * stats["matrix_identity"] / n, 2),
            "resonance_only_pct": round(100 * stats["molecule_same_matrix_differs"] / n, 2),
            "counts": dict(stats),
        }
        print(os.path.basename(path), json.dumps(out[os.path.basename(path)]), flush=True)
    json.dump(out, open(args.out, "w"), indent=1)
    print("wrote", args.out)


if __name__ == "__main__":
    main()
