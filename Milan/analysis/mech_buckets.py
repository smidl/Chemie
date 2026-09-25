#!/usr/bin/env python
"""Is the arrow alphabet in scope for the radical chemistry of RMechDB?

The FlowER corpus carries PMechDB/RMechDB-derived steps under four bucket labels
in place of a numeric sequence index: PM/PC (polar, manual/combinatorial) and
RS/RC (radical).  RS+RC total 5,088 steps, matching RMechDB's ~5,300 -- so the
radical database is effectively on disk already, balanced and atom-mapped,
without the gated download.  What the conversion drops is the curly-arrow
annotation, so this measures scope and ambiguity, not arrow recovery.

The question.  AFM's alphabet has four moves.  The two pair moves (LONE->BOND,
BOND->LONE) change a diagonal entry by +-2; the two single-electron moves
(HOMOLYSIS, COLLIGATION) change two diagonals by +-1 each against a bond of -+1,
and are, per the paper, "needed whenever a step changes a diagonal entry by an
odd amount, which pair moves cannot do".  So the parity of the diagonal change is
a direct, cheap test of whether a step needs the fish-hook half of the alphabet --
which is exactly the half OrbChain/ArrowFinder (polar only) does not have.

Bond-electron matrix, Dugundji-Ugi, over the atom-map space:

    B_ij  = bond order between i and j          (i != j)
    B_ii  = V(element) - formal_charge(i) - sum_j B_ij     (unshared electrons)

Every hydrogen is its own mapped atom in this corpus, so no implicit-H term is
needed.  Total electrons = sum of all entries (diagonals once, bonds twice), and
a well-formed elementary step conserves it exactly; that is checked, not assumed.

Reports, per bucket: parse rate, electron/atom conservation, how many steps carry
an odd diagonal change (need single-electron moves), how many touch a radical
centre at all, and the distribution of the move count implied by the delta.

  python mech_buckets.py --data_dir DIR --dataset flower_new_dataset \
      --workers 32 --out_json out.json --out_dir buckets/
"""
import argparse
import json
import os
from collections import Counter
from multiprocessing import Pool

from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")

_PS = Chem.SmilesParserParams()
_PS.removeHs = False
_PS.sanitize = True

#: Valence electrons per element, for the B_ii formula.  Covers the corpus;
#: an unlisted element makes the step unparsable rather than silently wrong.
VALENCE = {
    "H": 1, "Li": 1, "Na": 1, "K": 1, "Rb": 1, "Cs": 1, "Cu": 1, "Ag": 1,
    "Be": 2, "Mg": 2, "Ca": 2, "Sr": 2, "Ba": 2, "Zn": 2, "Cd": 2, "Hg": 2,
    "B": 3, "Al": 3, "Ga": 3, "In": 3, "Tl": 3,
    "C": 4, "Si": 4, "Ge": 4, "Sn": 4, "Pb": 4, "Ti": 4, "Zr": 4,
    "N": 5, "P": 5, "As": 5, "Sb": 5, "Bi": 5, "V": 5,
    "O": 6, "S": 6, "Se": 6, "Te": 6, "Cr": 6, "Mo": 6, "W": 6,
    "F": 7, "Cl": 7, "Br": 7, "I": 7, "Mn": 7, "Re": 7,
    "He": 2, "Ne": 8, "Ar": 8, "Kr": 8, "Xe": 8,
}

BUCKETS = ("PM", "PC", "RS", "RC")


def be_matrix(smiles):
    """(diagonal dict, bond dict, element dict) over map numbers, or None."""
    mol = Chem.MolFromSmiles(smiles, _PS)
    if mol is None:
        return None
    try:
        Chem.Kekulize(mol, clearAromaticFlags=True)
    except Exception:
        return None

    bonds, elements, charges = {}, {}, {}
    for atom in mol.GetAtoms():
        n = atom.GetAtomMapNum()
        if not n:
            return None  # an unmapped atom has no column in the shared space
        sym = atom.GetSymbol()
        if sym not in VALENCE:
            return None
        elements[n] = sym
        charges[n] = atom.GetFormalCharge()
    for bond in mol.GetBonds():
        a, b = bond.GetBeginAtom().GetAtomMapNum(), bond.GetEndAtom().GetAtomMapNum()
        order = bond.GetBondTypeAsDouble()
        if order != int(order):
            return None  # unkekulised aromatic bond: not an integer matrix
        bonds[(a, b) if a < b else (b, a)] = int(order)

    diag = {}
    for n, sym in elements.items():
        rowsum = sum(o for (i, j), o in bonds.items() if i == n or j == n)
        diag[n] = VALENCE[sym] - charges[n] - rowsum
    return diag, bonds, elements


def total_electrons(diag, bonds):
    """Sum of the whole symmetric matrix: diagonals once, each bond twice."""
    return sum(diag.values()) + 2 * sum(bonds.values())


def analyse(line):
    """Flags and measurements for one corpus step."""
    rxn, _, label = line.strip().rpartition("|")
    if ">>" not in rxn:
        return {"flag": "malformed"}
    src, dst = rxn.split(">>")
    if src == dst:
        return {"flag": "identity"}

    r = be_matrix(src)
    p = be_matrix(dst)
    if r is None or p is None:
        return {"flag": "unparsed"}
    r_diag, r_bonds, r_elem = r
    p_diag, p_bonds, p_elem = p

    if set(r_elem) != set(p_elem):
        return {"flag": "atom_set_differs"}

    out = {"flag": "ok"}
    out["electrons_conserved"] = (
        total_electrons(r_diag, r_bonds) == total_electrons(p_diag, p_bonds)
    )

    # Diagonal changes.  Parity decides whether the pair moves suffice.
    odd_diag = 0
    for n in r_diag:
        d = p_diag[n] - r_diag[n]
        if d % 2:
            odd_diag += 1
    out["odd_diagonal_atoms"] = odd_diag
    out["needs_single_electron_moves"] = odd_diag > 0

    # A radical centre is an atom with an odd number of unshared electrons.
    out["radical_reactant"] = sum(1 for v in r_diag.values() if v % 2)
    out["radical_product"] = sum(1 for v in p_diag.values() if v % 2)

    # Move count implied by the delta.  A pair move shifts one diagonal by 2 and
    # one bond by 1; a single-electron move shifts two diagonals by 1 and one bond
    # by 1.  Either way one move accounts for exactly one unit of bond change, so
    # the total absolute bond change is a lower bound on the number of moves.
    bond_change = 0
    for key in set(r_bonds) | set(p_bonds):
        bond_change += abs(p_bonds.get(key, 0) - r_bonds.get(key, 0))
    out["moves_lower_bound"] = bond_change
    out["n_atoms"] = len(r_elem)
    return out


def scan_chunk(job):
    path, offset, n_lines, wanted = job
    stats = {b: Counter() for b in BUCKETS}
    moves = {b: Counter() for b in BUCKETS}
    kept = {b: [] for b in BUCKETS}
    with open(path) as fh:
        fh.seek(offset)
        for _ in range(n_lines):
            line = fh.readline()
            if not line:
                break
            label = line.strip().rpartition("|")[2]
            bucket = label.rstrip("0123456789")
            if bucket not in BUCKETS:
                continue
            if wanted:
                kept[bucket].append(line)
            s = stats[bucket]
            s["steps"] += 1
            a = analyse(line)
            s[a["flag"]] += 1
            if a["flag"] != "ok":
                continue
            s["electrons_conserved"] += int(a["electrons_conserved"])
            s["needs_single_electron_moves"] += int(a["needs_single_electron_moves"])
            s["has_radical_reactant"] += int(a["radical_reactant"] > 0)
            s["has_radical_product"] += int(a["radical_product"] > 0)
            s["atoms_total"] += a["n_atoms"]
            moves[bucket][a["moves_lower_bound"]] += 1
    return stats, moves, kept


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
    ap.add_argument("--data_dir", required=True)
    ap.add_argument("--dataset", default="flower_new_dataset")
    ap.add_argument("--splits", default="train,test")
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--out_json", required=True)
    ap.add_argument("--out_dir", default=None,
                    help="if given, write each bucket's steps to <out_dir>/<split>_<bucket>.txt")
    args = ap.parse_args()

    result = {}
    for split in args.splits.split(","):
        path = f"{args.data_dir}/{args.dataset}/{split}.txt"
        _, chunks = plan_chunks(path, args.workers)
        jobs = [(path, off, n, args.out_dir is not None) for off, n in chunks]
        stats = {b: Counter() for b in BUCKETS}
        moves = {b: Counter() for b in BUCKETS}
        kept = {b: [] for b in BUCKETS}
        with Pool(args.workers) as pool:
            for s, m, k in pool.imap_unordered(scan_chunk, jobs):
                for b in BUCKETS:
                    stats[b].update(s[b])
                    moves[b].update(m[b])
                    kept[b].extend(k[b])

        if args.out_dir:
            os.makedirs(args.out_dir, exist_ok=True)
            for b in BUCKETS:
                if kept[b]:
                    with open(f"{args.out_dir}/{split}_{b}.txt", "w") as fh:
                        fh.writelines(kept[b])

        result[split] = {}
        for b in BUCKETS:
            s, m = stats[b], moves[b]
            ok = s.get("ok", 0)
            result[split][b] = {
                "steps": s.get("steps", 0),
                "ok": ok,
                "identity": s.get("identity", 0),
                "unparsed": s.get("unparsed", 0),
                "atom_set_differs": s.get("atom_set_differs", 0),
                "electrons_conserved": s.get("electrons_conserved", 0),
                "electrons_conserved_pct": round(100.0 * s.get("electrons_conserved", 0) / max(1, ok), 2),
                "needs_single_electron_moves": s.get("needs_single_electron_moves", 0),
                "needs_single_electron_moves_pct": round(100.0 * s.get("needs_single_electron_moves", 0) / max(1, ok), 2),
                "has_radical_reactant_pct": round(100.0 * s.get("has_radical_reactant", 0) / max(1, ok), 2),
                "has_radical_product_pct": round(100.0 * s.get("has_radical_product", 0) / max(1, ok), 2),
                "mean_atoms": round(s.get("atoms_total", 0) / max(1, ok), 1),
                "moves_lower_bound_hist": {str(k): m[k] for k in sorted(m)},
                "mean_moves_lower_bound": round(
                    sum(k * v for k, v in m.items()) / max(1, sum(m.values())), 2
                ),
            }

    with open(args.out_json, "w") as fh:
        json.dump(result, fh, indent=2)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
