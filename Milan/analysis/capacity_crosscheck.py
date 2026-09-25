#!/usr/bin/env python
"""Does AFM's capacity table, built on its own corpus, cover other chemistry?

The guarantee's one empirical assumption. afm.pdf enumerates the per-atom capacity
table T against the FlowER corpus and grades validity with the same checker
("Appendix E.3 ... the largest c_i any atom of each element attains over the test
split"). On chemistry outside that corpus the table can be too tight: the mask
then forbids the correct stop state, validity still reports 1.0000 because every
visited state is representable, and accuracy on those steps silently goes to zero.
That failure is invisible to every metric the paper reports.

This measures it. Build the table from one corpus, then scan another and count
atoms whose occupancy Z_ii + 2*beta_i exceeds it. Four corpora are available:
the FlowER training split (what the paper used), and PMechDB / RMechDB, which
are curated from the literature and were never seen when the table was built.

  python capacity_crosscheck.py --table FILE --against name=FILE ... --out_json out.json
"""
import argparse
import csv
import json
from collections import Counter, defaultdict
from multiprocessing import Pool

from rdkit import RDLogger

import sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from decompose_steps import be_matrix, occupancies  # noqa: E402
from rmechdb_arrows import reduced_matrix  # noqa: E402

RDLogger.DisableLog("rdApp.*")


def sides_corpus(path, limit=None):
    """FlowER-format lines: 'reactant>>product|label'. Fully mapped."""
    out = []
    with open(path) as fh:
        for i, line in enumerate(fh):
            if limit and i >= limit:
                break
            rxn = line.strip().rpartition("|")[0]
            if ">>" in rxn:
                out.append(tuple(rxn.split(">>")))
    return out, "corpus"


def sides_mechdb(path, limit=None):
    """PMechDB/RMechDB CSV: only the reacting atoms are mapped."""
    out = []
    for i, rec in enumerate(csv.reader(open(path))):
        if limit and i >= limit:
            break
        if not rec or ">>" not in rec[0]:
            continue
        smirks = rec[0].strip().rpartition(" ")[0]
        src, _, dst = smirks.partition(">>")
        out.append((src, dst))
    return out, "mechdb"


def occ_chunk(job):
    pairs, kind = job
    caps, hist = defaultdict(int), Counter()
    for src, dst in pairs:
        for side in (src, dst):
            m = be_matrix(side) if kind == "corpus" else reduced_matrix(side)
            if m is None:
                continue
            if kind == "corpus":
                diag, bonds, elements = m
                items = occupancies(diag, bonds, elements)
            else:
                diag, bonds, elements, context = m
                items = []
                for n, sym in elements.items():
                    beta = sum(o for (i, j), o in bonds.items() if i == n or j == n) + context[n]
                    items.append((sym, diag[n] + 2 * beta))
            for sym, occ in items:
                hist[(sym, occ)] += 1
                if occ > caps[sym]:
                    caps[sym] = occ
    return dict(caps), hist


def scan(path, loader, workers, limit=None):
    pairs, kind = loader(path, limit)
    step = max(1, (len(pairs) + workers - 1) // workers)
    jobs = [(pairs[i:i + step], kind) for i in range(0, len(pairs), step)]
    caps, hist = defaultdict(int), Counter()
    with Pool(workers) as pool:
        for c, h in pool.imap_unordered(occ_chunk, jobs):
            hist.update(h)
            for sym, occ in c.items():
                if occ > caps[sym]:
                    caps[sym] = occ
    return dict(caps), hist, len(pairs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", help="corpus the table is built from (FlowER format)")
    ap.add_argument("--table_json", help="load a table dumped by an earlier run instead")
    ap.add_argument("--table_limit", type=int, default=None)
    ap.add_argument("--against", nargs="*", default=[], help="name=path, CSV (mechdb) or .txt (corpus)")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--out_json", required=True)
    args = ap.parse_args()

    # The table can be built here (needs the 3 GB corpus, so RCI) or loaded from
    # an earlier run's dump, which is what lets the corpus side and the licensed
    # PMechDB/RMechDB side run on different machines.
    if args.table_json:
        prev = json.load(open(args.table_json))
        table, n_table, src = prev["table"], prev.get("table_steps"), prev.get("table_source")
    else:
        table, _, n_table = scan(args.table, sides_corpus, args.workers, args.table_limit)
        src = args.table
    out = {"table_source": src, "table_steps": n_table,
           "table": dict(sorted(table.items())), "against": {}}

    for spec in args.against:
        name, _, path = spec.partition("=")
        loader = sides_mechdb if path.endswith(".csv") else sides_corpus
        caps, hist, n = scan(path, loader, args.workers)

        # Every (element, occupancy) the other corpus shows that the table forbids.
        over = Counter()
        unknown = Counter()
        for (sym, occ), count in hist.items():
            if sym not in table:
                unknown[sym] += count
            elif occ > table[sym]:
                over[(sym, occ, table[sym])] += count
        total_atoms = sum(hist.values())
        out["against"][name] = {
            "path": path,
            "steps": n,
            "atom_observations": total_atoms,
            "their_max_occupancy": dict(sorted(caps.items())),
            "elements_absent_from_table": dict(unknown),
            "atoms_over_table": {f"{s} occ={o} > cap={c}": v for (s, o, c), v in over.most_common(40)},
            "atoms_over_table_total": sum(over.values()),
            "atoms_over_table_pct": round(100.0 * sum(over.values()) / max(1, total_atoms), 4),
            "elements_exceeding": sorted({s for (s, _o, _c) in over}),
        }

    with open(args.out_json, "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2)[:4000])


if __name__ == "__main__":
    main()
