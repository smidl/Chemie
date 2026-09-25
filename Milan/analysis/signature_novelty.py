#!/usr/bin/env python
"""How much elementary-step-type novelty does FlowER's released split contain?

The mechanistic corpus is built by applying a finite set of expert-curated
templates to USPTO reactions, then split at random. Exact-step leakage is low
(4%, measured by compare_datasets.py), but that says nothing about whether a
test step's *mechanism type* was seen in training. If every type is covered,
then no model evaluated on this split is ever asked to extrapolate, and the
reported accuracies cannot separate a model that learned chemistry from one
that learned the template table.

This measures that. A step's TYPE is the change it makes to the bond-electron
matrix, stripped of everything the atom map holds fixed:

  core   multiset of {(elemA, elemB, order_before, order_after)} over bonds whose
         order changed, elements sorted within the pair, together with the
         multiset of {(elem, q_before, q_after)} over atoms whose formal charge
         changed. This is the data-side image of a curly-arrow multiset.

  1-hop  the same, but each participating atom is labelled by its element, its
         reactant-side formal charge, and the sorted elements of its reactant-side
         neighbours. Closer to an actual mechanistic template.

core over-reports coverage (too coarse) and 1-hop under-reports it (too fine);
run both and the truth is bracketed.

Identity steps (product == reactant, ~18.5% of the corpus, the pathway
terminator) have an empty signature and are counted separately rather than
pooled into a single giant class.

Outputs a JSON summary and a per-test-step TSV so that model predictions can
later be re-scored per novelty bin by joining on line index.

  python signature_novelty.py --data_dir DIR --dataset flower_new_dataset \
      --workers 32 --out_json out.json --out_tsv test_bins.tsv
"""
import argparse
import hashlib
import json
from collections import Counter
from multiprocessing import Pool

from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")

_PS = Chem.SmilesParserParams()
_PS.removeHs = False
_PS.sanitize = True

# Train-frequency bins for a test step's type. The first is the one that matters.
BIN_EDGES = [0, 1, 10, 100, 1000, 10000]
BIN_NAMES = ["unseen", "1-9", "10-99", "100-999", "1k-9999", ">=10k"]


def digest(text):
    return int.from_bytes(hashlib.blake2b(text.encode(), digest_size=8).digest(), "big")


def parse_side(smiles):
    """Map number -> (atom, mol) for one side of a step, Kekule-resolved."""
    mol = Chem.MolFromSmiles(smiles, _PS)
    if mol is None:
        return None, None
    try:
        Chem.Kekulize(mol, clearAromaticFlags=True)
    except Exception:
        return None, None
    by_map = {}
    for atom in mol.GetAtoms():
        n = atom.GetAtomMapNum()
        if n:
            by_map[n] = atom
    return mol, by_map


def bonds_by_map(mol, by_map):
    """{(lo_map, hi_map): order} over bonds whose two ends are both mapped."""
    out = {}
    for bond in mol.GetBonds():
        a, b = bond.GetBeginAtom().GetAtomMapNum(), bond.GetEndAtom().GetAtomMapNum()
        if a and b:
            out[(a, b) if a < b else (b, a)] = bond.GetBondTypeAsDouble()
    return out


def atom_label(atom, hop):
    if hop == 0:
        return f"{atom.GetSymbol()}{atom.GetFormalCharge():+d}"
    env = "".join(sorted(nb.GetSymbol() for nb in atom.GetNeighbors()))
    return f"{atom.GetSymbol()}{atom.GetFormalCharge():+d}[{env}]"


def signature(line, hop):
    """Canonical string for the step's type, or None if unparsable.

    Returns ("IDENT", 0) for an identity step, else (sig_string, n_changes).
    """
    rxn = line.strip().split("|")[0]
    if ">>" not in rxn:
        return None
    src, dst = rxn.split(">>")
    if src == dst:
        return "IDENT", 0

    rmol, rmap = parse_side(src)
    pmol, pmap = parse_side(dst)
    if rmol is None or pmol is None:
        return None

    rb, pb = bonds_by_map(rmol, rmap), bonds_by_map(pmol, pmap)

    bond_terms = []
    for key in set(rb) | set(pb):
        before, after = rb.get(key, 0.0), pb.get(key, 0.0)
        if before == after:
            continue
        i, j = key
        if i not in rmap or j not in rmap:
            continue
        ends = sorted([atom_label(rmap[i], hop), atom_label(rmap[j], hop)])
        bond_terms.append(f"{ends[0]}~{ends[1]}:{before:g}>{after:g}")

    charge_terms = []
    for n, atom in rmap.items():
        other = pmap.get(n)
        if other is None:
            continue
        q0, q1 = atom.GetFormalCharge(), other.GetFormalCharge()
        if q0 != q1:
            charge_terms.append(f"{atom_label(atom, hop)}:q{q0:+d}>{q1:+d}")

    n_changes = len(bond_terms) + len(charge_terms)
    if n_changes == 0:
        # Same bonds and charges but a different string: not an identity step in
        # the file's sense, but no BE change this signature can see.
        return "NOCHANGE", 0
    return "|".join(sorted(bond_terms) + sorted(charge_terms)), n_changes


def scan_chunk(job):
    """Count signatures over a byte slice of a file.

    The slice is given as (byte offset of a line start, line index there, how many
    lines to take) so each worker reads only its own share -- seeking by line would
    make every worker stream the whole 3 GB file.
    """
    path, offset, first_line, n_lines, keep = job
    core, hop1 = Counter(), Counter()
    rows = []
    with open(path) as fh:
        fh.seek(offset)
        for k in range(n_lines):
            line = fh.readline()
            if not line:
                break
            idx = first_line + k
            sc = signature(line, 0)
            sh = signature(line, 1)
            if sc is None or sh is None:
                core["__UNPARSED__"] += 1
                if keep:
                    rows.append((idx, -1, -1, -1))
                continue
            core[digest(sc[0])] += 1
            hop1[digest(sh[0])] += 1
            if keep:
                rows.append((idx, sc[1], digest(sc[0]), digest(sh[0])))
    return core, hop1, rows


def plan_chunks(path, workers):
    """One sequential pass: total lines, and a (byte offset, line index) per chunk."""
    marks, pos, lines = [(0, 0)], 0, 0
    with open(path, "rb") as fh:
        for buf in iter(lambda: fh.read(1 << 22), b""):
            start = 0
            while True:
                nl = buf.find(b"\n", start)
                if nl < 0:
                    break
                lines += 1
                marks.append((pos + nl + 1, lines))
                start = nl + 1
            pos += len(buf)
    step = max(1, (lines + workers - 1) // workers)
    chunks = []
    for s in range(0, lines, step):
        offset, first = marks[s]
        chunks.append((offset, first, min(step, lines - s)))
    return lines, chunks


def scan(path, workers, keep=False):
    total, chunks = plan_chunks(path, workers)
    jobs = [(path, off, first, n, keep) for off, first, n in chunks]
    core, hop1, rows = Counter(), Counter(), []
    with Pool(workers) as pool:
        for c, h, r in pool.imap_unordered(scan_chunk, jobs):
            core.update(c)
            hop1.update(h)
            rows.extend(r)
    rows.sort()
    return total, core, hop1, rows


def bin_index(count):
    if count <= 0:
        return 0
    for k in range(len(BIN_EDGES) - 1, 0, -1):
        if count >= BIN_EDGES[k]:
            return k
    return 1


def summarise(train_counts, test_counts, label):
    """Coverage of test steps by train types, at one granularity."""
    ident = digest("IDENT")
    train_real = {k: v for k, v in train_counts.items() if isinstance(k, int) and k != ident}
    test_real = {k: v for k, v in test_counts.items() if isinstance(k, int) and k != ident}

    n_test = sum(test_real.values())
    unseen_types = [k for k in test_real if k not in train_real]
    unseen_steps = sum(test_real[k] for k in unseen_types)

    bins = Counter()
    for k, v in test_real.items():
        bins[bin_index(train_real.get(k, 0))] += v

    ordered = sorted(train_real.values(), reverse=True)
    n_train = max(1, sum(ordered))
    top = {
        f"top{n}_types_cover_pct_of_train": round(100.0 * sum(ordered[:n]) / n_train, 2)
        for n in (10, 50, 100, 500)
    }
    return {
        "granularity": label,
        "train_distinct_types": len(train_real),
        "test_distinct_types": len(test_real),
        "test_steps_nonidentity": n_test,
        "test_types_unseen_in_train": len(unseen_types),
        "test_steps_with_unseen_type": unseen_steps,
        "test_steps_with_unseen_type_pct": round(100.0 * unseen_steps / max(1, n_test), 4),
        "test_steps_by_train_frequency_bin": {
            BIN_NAMES[i]: bins.get(i, 0) for i in range(len(BIN_NAMES))
        },
        "test_steps_by_train_frequency_bin_pct": {
            BIN_NAMES[i]: round(100.0 * bins.get(i, 0) / max(1, n_test), 3)
            for i in range(len(BIN_NAMES))
        },
        **top,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data_dir", required=True)
    ap.add_argument("--dataset", default="flower_new_dataset")
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--out_json", required=True)
    ap.add_argument("--out_tsv", default=None)
    args = ap.parse_args()

    base = f"{args.data_dir}/{args.dataset}"
    ident = digest("IDENT")

    n_tr, tr_core, tr_hop, _ = scan(f"{base}/train.txt", args.workers)
    n_te, te_core, te_hop, rows = scan(f"{base}/test.txt", args.workers, keep=True)

    out = {
        "dataset": args.dataset,
        "train_steps": n_tr,
        "test_steps": n_te,
        "train_identity_steps": tr_core.get(ident, 0),
        "test_identity_steps": te_core.get(ident, 0),
        "unparsed_train": tr_core.get("__UNPARSED__", 0),
        "unparsed_test": te_core.get("__UNPARSED__", 0),
        "core": summarise(tr_core, te_core, "core"),
        "one_hop": summarise(tr_hop, te_hop, "1-hop"),
    }
    with open(args.out_json, "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps(out, indent=2))

    if args.out_tsv:
        tr_core_real = {k: v for k, v in tr_core.items() if isinstance(k, int)}
        tr_hop_real = {k: v for k, v in tr_hop.items() if isinstance(k, int)}
        with open(args.out_tsv, "w") as fh:
            fh.write("line\tn_changes\ttrain_count_core\ttrain_count_1hop\n")
            for idx, nch, dc, dh in rows:
                if nch < 0:
                    fh.write(f"{idx}\t-1\t-1\t-1\n")
                else:
                    fh.write(
                        f"{idx}\t{nch}\t{tr_core_real.get(dc, 0)}\t{tr_hop_real.get(dh, 0)}\n"
                    )


if __name__ == "__main__":
    main()
