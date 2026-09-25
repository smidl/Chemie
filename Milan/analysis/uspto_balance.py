#!/usr/bin/env python
"""How much of USPTO-Full is runnable by an atom-conserving decomposition as recorded?

FlowER's template pipeline was applied to 1,100,105 USPTO reactions and produced
mechanistic pathways for 289,024 overall reactions (26.3%).  The ~810k residue is
the only non-circular target for a model-free A->C decomposer -- but a decomposer
over the bond-electron matrix needs a reaction that is BALANCED and ATOM-MAPPED
before it can factor anything, and template application *creates* balance by
adding the byproducts the template implies.  So "unbalanced as recorded" does not
mean "no mechanism exists"; it means "not runnable without a balancing step".

This measures the population that needs no such step, on Lowe's raw grants file:

  parsed             RDKit reads both sides
  mapped             every product heavy atom carries a map number seen in reactants
  balanced_strict    reactants alone conserve the product's heavy-atom multiset
  balanced_agents    reactants + agents conserve it (agents are the middle field,
                     nominally solvents/catalysts, but the corpus treats spectators
                     as participants so they must be counted both ways)
  proton / charge    hydrogen count and total formal charge, on the same two readings

The decisive cross-check is whether the balanced-and-mapped population exceeds
289,024.  If it does not, the template pipeline demonstrably manufactures balance
and any residue work needs a balancer (SynRBL) in front of it.

  python uspto_balance.py --rsmi FILE --workers 32 --out_json out.json
"""
import argparse
import json
from collections import Counter
from multiprocessing import Pool

from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")

_PS = Chem.SmilesParserParams()
_PS.removeHs = False
_PS.sanitize = True


def composition(smiles):
    """(heavy-atom Counter, total H count, total formal charge, mapped-atom set).

    Returns None if RDKit rejects the side.  Hydrogen is counted as explicit
    atoms plus the implicit count RDKit assigns to every heavy atom, so the
    number does not depend on how the record happened to write them.
    """
    if smiles == "":
        return Counter(), 0, 0, set()
    mol = Chem.MolFromSmiles(smiles, _PS)
    if mol is None:
        return None
    heavy, hydrogens, charge, mapped = Counter(), 0, 0, set()
    for atom in mol.GetAtoms():
        sym = atom.GetSymbol()
        charge += atom.GetFormalCharge()
        if sym == "H":
            hydrogens += 1
            continue
        heavy[sym] += 1
        hydrogens += atom.GetTotalNumHs()
        n = atom.GetAtomMapNum()
        if n:
            mapped.add(n)
    return heavy, hydrogens, charge, mapped


def classify(line):
    """Flags for one .rsmi row.  Returns a tuple of counter keys to increment."""
    fields = line.rstrip("\n").split("\t")
    rxn = fields[0]
    year = fields[3] if len(fields) > 3 else ""
    parts = rxn.split(">")
    if len(parts) != 3:
        return ("malformed",), year
    src, agents, dst = parts

    r = composition(src)
    a = composition(agents)
    p = composition(dst)
    if r is None or a is None or p is None:
        return ("unparsed",), year

    r_heavy, r_h, r_q, r_map = r
    a_heavy, a_h, a_q, a_map = a
    p_heavy, p_h, p_q, p_map = p

    if not p_heavy:
        return ("empty_product",), year

    flags = ["parsed"]

    # Mapped: every product heavy atom's map number is present on the reactant
    # side.  An unmapped product atom has nowhere to come from, so the BE-matrix
    # delta is undefined for it.
    mapped = bool(p_map) and p_map <= (r_map | a_map)
    if mapped:
        flags.append("mapped")

    strict = r_heavy == p_heavy
    with_agents = (r_heavy + a_heavy) == p_heavy
    if strict:
        flags.append("balanced_strict")
        if r_h == p_h:
            flags.append("proton_strict")
        if r_q == p_q:
            flags.append("charge_strict")
    if with_agents:
        flags.append("balanced_agents")
        if r_h + a_h == p_h:
            flags.append("proton_agents")
        if r_q + a_q == p_q:
            flags.append("charge_agents")

    # The population runnable today: balanced under either reading AND mapped.
    if mapped and (strict or with_agents):
        flags.append("RUNNABLE")
        if strict:
            flags.append("RUNNABLE_strict")
    return tuple(flags), year


def scan_chunk(job):
    path, offset, n_lines, skip_header = job
    counts, years = Counter(), Counter()
    with open(path, errors="replace") as fh:
        fh.seek(offset)
        if skip_header:
            fh.readline()
        for _ in range(n_lines):
            line = fh.readline()
            if not line:
                break
            counts["rows"] += 1
            flags, year = classify(line)
            for flag in flags:
                counts[flag] += 1
            if "RUNNABLE" in flags and year:
                years[year] += 1
    return counts, years


def plan_chunks(path, workers):
    marks, pos, lines = [0], 0, 0
    with open(path, "rb") as fh:
        for buf in iter(lambda: fh.read(1 << 22), b""):
            start = 0
            while True:
                nl = buf.find(b"\n", start)
                if nl < 0:
                    break
                lines += 1
                marks.append(pos + nl + 1)
                start = nl + 1
            pos += len(buf)
    step = max(1, (lines + workers - 1) // workers)
    return lines, [(marks[s], min(step, lines - s)) for s in range(0, lines, step)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rsmi", required=True)
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--out_json", required=True)
    ap.add_argument("--corpus_reactions", type=int, default=289024,
                    help="overall reactions the FlowER corpus covers, for the cross-check")
    args = ap.parse_args()

    total, chunks = plan_chunks(args.rsmi, args.workers)
    # The first chunk spends one of its lines on the header, so it takes one
    # fewer row; without this it reads one row into the next chunk's range and
    # that row is counted twice.
    jobs = [(args.rsmi, off, n - 1 if i == 0 else n, i == 0)
            for i, (off, n) in enumerate(chunks)]
    counts, years = Counter(), Counter()
    with Pool(args.workers) as pool:
        for c, y in pool.imap_unordered(scan_chunk, jobs):
            counts.update(c)
            years.update(y)

    rows = counts["rows"]
    out = {
        "file_lines": total,
        "rows_scanned": rows,
        "counts": dict(counts),
        "pct_of_rows": {k: round(100.0 * v / max(1, rows), 2) for k, v in counts.items()},
        "runnable_years": dict(sorted(years.items())),
        "cross_check": {
            "flower_corpus_overall_reactions": args.corpus_reactions,
            "runnable_as_recorded": counts["RUNNABLE"],
            "runnable_exceeds_corpus": counts["RUNNABLE"] > args.corpus_reactions,
        },
    }
    with open(args.out_json, "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
