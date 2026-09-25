#!/usr/bin/env python
"""How concerted are the corpus's elementary steps? Model-free, no search.

The pre-check for a constructed OOD axis the paper's own theory predicts.
Two results of afm.pdf meet on one quantity, the number of matrix positions a
step couples:

* Theorem 1 / App. "the path is exact in mean and not surely": the entrywise
  bridge's electron count has variance ``kappa(1-kappa) * sum_e w_e^2 Delta_e^2``
  -- linear in the number of changed positions. A six-position step gives
  sigma ~ 2.4 electrons at kappa = 1/2, so an entrywise model is trained almost
  only on states that are not molecules. AFM's states are on the sheet by
  construction, whatever the step.
* App. "What one move does to a capacity, and the jam": a pericyclic step is
  *jammed as arrows* -- every single first arrow puts a fifth pair on some
  atom -- and the alphabet dissolves it by splitting each migration into
  BOND_TO_LONE then LONE_TO_BOND. 5.06% of test steps admit no ordering of
  arrows through Tab, 0% admit no ordering of moves.

So the prediction is not "AFM is better" but "the AFM-minus-entrywise gap grows
with sum w^2 Delta^2, and is largest on the jammed cyclic steps". Before any
GPU is spent, this script asks whether the corpus contains that chemistry at a
depth the model could have learned -- the check that distinguishes this axis
from the radical one, where the required continuation occurs twice in 200,000
steps (`problem02-termination.md`).

Everything here is read off Delta = B_p - B_r, exactly, with no enumeration:

* **moves** ``m = sum_{i<j} |Delta_ij|``. Every move of the alphabet changes
  exactly one off-diagonal entry by one, so this is the minimal move count
  (the count of a decomposition that touches no bond twice).
* **arrows** ``m/2`` where the step is a pure chain/cycle of migrations.
* **var_coef** ``sum_e w_e^2 Delta_e^2`` with w = 1 on the diagonal and 2 off
  it -- the entrywise path variance at kappa(1-kappa) = 1, the theory's own
  x-axis.
* **walk structure** (App. "Decomposition, cutting a step into arrows"): the
  changed bonds form a graph on atoms; its connected components are the walks.
  A component whose atoms carry no diagonal change and all have degree two is
  a **cycle** -- "a walk that closes into a cycle has no ends, so it neither
  donates nor accepts, and that is the pericyclic case". Alternation (break,
  form, break, ...) is the local condition that the two changed bonds at every
  degree-two atom have opposite sign.

  python concertedness.py --files DIR/train.txt DIR/test.txt --every 10 \
      --workers 32 --out_json out.json --out_tsv strata.tsv.gz
"""
from __future__ import annotations

import argparse
import gzip
import json
import os
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool

import numpy as np
from rdkit import RDLogger

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# The model's own featurisation, not decompose_steps' reduced one: the latter's
# VALENCE table has no Pd, so it silently drops every organometallic step --
# which is where the corpus's odd-parity chemistry lives.
AFM_REPO = os.environ.get("AFM_REPO", os.path.expanduser("~/ArrowFlowMatching"))
sys.path.insert(0, AFM_REPO)
import chem  # noqa: E402

RDLogger.DisableLog("rdApp.*")


def _be(smiles: str):
    mol = chem.mol_from_mapped_smiles(smiles)
    atom_index, matrix = chem.atom_types_and_be(mol)
    return [chem.ELEM_LIST[k] for k in atom_index], matrix.astype(int)


def analyse(line: str):
    head = line.strip().split("|")[0]
    if ">>" not in head:
        return None
    src, _, dst = head.partition(">>")
    try:
        r_elem, r_mat = _be(src)
        p_elem, p_mat = _be(dst)
    except Exception:  # noqa: BLE001
        return {"verdict": "unparsed"}
    if r_elem != p_elem:
        return {"verdict": "atom_set_differs"}

    delta = p_mat - r_mat
    n = delta.shape[0]
    ddiag = {i: int(delta[i, i]) for i in range(n) if delta[i, i]}
    dbond = {(i, j): int(delta[i, j]) for i in range(n) for j in range(i + 1, n) if delta[i, j]}
    r_elem = {i: r_elem[i] for i in range(n)}
    if not ddiag and not dbond:
        return {"verdict": "identity"}

    m = sum(abs(d) for d in dbond.values())
    var_coef = sum(d * d for d in ddiag.values()) + 4 * sum(d * d for d in dbond.values())
    n_changed = len(ddiag) + len(dbond)
    odd_atoms = sum(1 for d in ddiag.values() if abs(d) % 2)

    adj = defaultdict(list)
    for (i, j), d in dbond.items():
        adj[i].append((j, (i, j)))
        adj[j].append((i, (i, j)))

    seen, comps = set(), []
    for start in adj:
        if start in seen:
            continue
        stack, nodes, edges = [start], set(), set()
        seen.add(start)
        while stack:
            u = stack.pop()
            nodes.add(u)
            for v, e in adj[u]:
                edges.add(e)
                if v not in seen:
                    seen.add(v)
                    stack.append(v)
        ends = sum(1 for n in nodes if n in ddiag)
        degrees = {n: len(adj[n]) for n in nodes}
        # every interior atom of a walk passes a pair on: its two changed bonds
        # must read break, form (opposite signs).
        alternating = all(
            dbond[adj[n][0][1]] * dbond[adj[n][1][1]] < 0
            for n, deg in degrees.items() if deg == 2
        )
        cycle = ends == 0 and all(deg == 2 for deg in degrees.values()) and len(edges) == len(nodes)
        comps.append({
            "atoms": len(nodes), "bonds": len(edges), "ends": ends,
            "cycle": cycle, "alternating": alternating,
            "elements": "".join(sorted(r_elem[n] for n in nodes)) if cycle else "",
        })

    cycles = [c for c in comps if c["cycle"]]
    lone_only = sum(1 for n in ddiag if n not in adj)  # diagonal change touching no changed bond
    return {
        "verdict": "ok", "m": m, "var_coef": var_coef, "n_changed": n_changed,
        "odd_atoms": odd_atoms, "n_components": len(comps),
        "n_cycles": len(cycles),
        "max_cycle_bonds": max((c["bonds"] for c in cycles), default=0),
        "cycle_alternating": all(c["alternating"] for c in cycles) if cycles else None,
        "cycle_elements": cycles[0]["elements"] if cycles else "",
        "all_alternating": all(c["alternating"] for c in comps),
        "lone_only_atoms": lone_only,
        "max_component_bonds": max((c["bonds"] for c in comps), default=0),
    }


def _bucket(v, edges):
    for hi in edges:
        if v <= hi:
            return str(hi)
    return f">{edges[-1]}"


#: strata written as split files, ready for ``eval.py data.eval_split=...``.
#: `cyclic` is the jam class of App. "What one move does to a capacity"; the
#: move-count strata are the theory's x-axis binned.
def stratum_of(a):
    out = []
    if a["n_cycles"]:
        out.append("cyclic")
    m = a["m"]
    out.append("m1" if m <= 1 else "m2" if m == 2 else "m3to5" if m <= 5 else "m6plus")
    return out


def run_chunk(job):
    path, start, end, every, offset, keep = job
    stats = Counter()
    hist = defaultdict(Counter)
    rows = defaultdict(list)
    with open(path) as fh:
        fh.seek(start)
        if start:
            fh.readline()
        idx = -1
        while fh.tell() < end:
            line = fh.readline()
            if not line:
                break
            idx += 1
            if (idx + offset) % every:
                continue
            a = analyse(line)
            if a is None:
                continue
            stats[a["verdict"]] += 1
            if a["verdict"] != "ok":
                continue
            stats["non_identity"] += 1
            hist["moves"][min(a["m"], 12)] += 1
            hist["var_coef"][_bucket(a["var_coef"], [4, 8, 16, 24, 40, 64])] += 1
            hist["components"][min(a["n_components"], 4)] += 1
            if a["odd_atoms"]:
                stats["odd_parity"] += 1
            if a["n_cycles"]:
                stats["has_cycle"] += 1
                hist["cycle_bonds"][a["max_cycle_bonds"]] += 1
                hist["cycle_elements"][a["cycle_elements"][:12]] += 1
                if a["cycle_alternating"]:
                    stats["cycle_alternating"] += 1
                if a["m"] >= 6:
                    stats["cycle_6plus_moves"] += 1
            if a["m"] >= 3:
                stats["moves_3plus"] += 1
            if a["m"] >= 6:
                stats["moves_6plus"] += 1
            if not a["all_alternating"]:
                stats["non_alternating_walk"] += 1
            if keep:
                for s in stratum_of(a):
                    rows[s].append(line)
    return stats, hist, rows


def chunks(path, workers, every, offset, keep):
    size = os.path.getsize(path)
    step = max(1, size // workers)
    return [(path, k, min(k + step, size), every, offset, keep) for k in range(0, size, step)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--every", type=int, default=1, help="take every Nth line")
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--out_json", required=True)
    ap.add_argument("--out_dir", default=None,
                     help="write each stratum's steps to <out_dir>/<split>_<stratum>.txt")
    args = ap.parse_args()

    if args.out_dir:
        os.makedirs(args.out_dir, exist_ok=True)
    out = {}
    for path in args.files:
        name = os.path.basename(path)
        split = name.rsplit(".", 1)[0]
        jobs = chunks(path, args.workers, args.every, args.offset, bool(args.out_dir))
        stats, hist, rows = Counter(), defaultdict(Counter), defaultdict(list)
        with Pool(args.workers) as pool:
            for s, h, r in pool.imap_unordered(run_chunk, jobs):
                stats.update(s)
                for k, c in h.items():
                    hist[k].update(c)
                for k, v in r.items():
                    rows[k].extend(v)
        n = stats["non_identity"] or 1
        out[name] = {
            "counts": dict(stats),
            "pct_of_non_identity": {
                k: round(100 * stats[k] / n, 3) for k in
                ("odd_parity", "has_cycle", "cycle_alternating", "cycle_6plus_moves",
                 "moves_3plus", "moves_6plus", "non_alternating_walk")
            },
            "hist": {k: {str(a): b for a, b in sorted(c.items(), key=lambda kv: str(kv[0]))}
                     for k, c in hist.items()},
        }
        print(json.dumps({name: out[name]}, indent=1)[:4000])
        if args.out_dir:
            out[name]["strata_files"] = {}
            for stratum, lines in sorted(rows.items()):
                target = os.path.join(args.out_dir, f"{split}_{stratum}.txt")
                with open(target, "w") as fh:
                    fh.writelines(lines)
                out[name]["strata_files"][stratum] = len(lines)
            print("strata:", out[name]["strata_files"])
    with open(args.out_json, "w") as fh:
        json.dump(out, fh, indent=1)
    print("wrote", args.out_json)


if __name__ == "__main__":
    main()
