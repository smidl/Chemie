#!/usr/bin/env python
"""Does the arrow alphabet admit a decomposition for a given A -> C?

The number this sits against: ArrowFinder (miller2025_arrowfinder, JACS 2025)
recovers a mechanism for 1331/1337 = 99.55% of curated endpoint pairs, but for
only 1968/2858 = 68.86% of its own ensemble's balance-filtered predictions,
because -- the authors' own explanation -- "the predicted products do not always
have a simple or plausible arrow-pushing mechanism available".  That is a
property of generate-then-filter.  A construction whose every state is reached by
applying admissible moves cannot fail that way.  This measures the construction
side of that comparison directly.

Method, model-free throughout (afm.pdf section 5; no trained network anywhere):

  1. Build the Dugundji-Ugi matrix for both endpoints over the atom-map space.
  2. Split the bond-order delta into unit changes, one slot per unit.
  3. Each slot is realised by one of three moves of the four-symbol alphabet
     (LONE_TO_BOND either direction, or COLLIGATION, for a +1 unit; BOND_TO_LONE
     either direction, or HOMOLYSIS, for -1).  Enumerate the product of slots and
     keep the assignments whose per-atom diagonal contributions match the
     required change exactly.
  4. For each such move multiset, search for an ordering admissible at every
     prefix, permuting only within connected components of the move graph.

Two departures from `retrosyntesis/script/decomposition_check.py`, which this is
adapted from.  That script rejects an odd non-bonding electron count as an input
bug, correct for its closed-shell corpus and fatal here -- radical chemistry is
the point.  And it hardcodes an octet cap over six elements; instead the per-element
capacity is measured from the corpus endpoints in a first pass, which is what the
paper does too ("the table is built against the same valency checker the
experiments score with").

  python decompose_steps.py --files buckets/train_RS.txt ... --out_json out.json
"""
import argparse
import itertools
import json
from collections import Counter, defaultdict
from multiprocessing import Pool

from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")

_PS = Chem.SmilesParserParams()
_PS.removeHs = False
_PS.sanitize = True

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

#: (dii, djj, dij) per move, for an ordered pair (i, j).  Every increment sums to
#: zero over the full symmetric matrix -- dii + djj + 2*dij = 0 -- which is what
#: makes electron conservation an identity rather than a constraint to enforce.
MOVES_PLUS = [  # realise +1 of bond order
    ("LONE_TO_BOND_i", -2, 0, +1),
    ("LONE_TO_BOND_j", 0, -2, +1),
    ("COLLIGATION", -1, -1, +1),
]
MOVES_MINUS = [  # realise -1 of bond order
    ("BOND_TO_LONE_j", 0, +2, -1),
    ("BOND_TO_LONE_i", +2, 0, -1),
    ("HOMOLYSIS", +1, +1, -1),
]

MAX_UNITS = 10       # 3**10 = 59049 assignments; larger steps are reported, not searched
MAX_COMPONENT = 7    # 7! = 5040 orderings per connected component


def be_matrix(smiles):
    """(diag, bonds, elements) over map numbers, or None if not representable."""
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
            return None
        sym = atom.GetSymbol()
        if sym not in VALENCE:
            return None
        elements[n], charges[n] = sym, atom.GetFormalCharge()
    for bond in mol.GetBonds():
        a, b = bond.GetBeginAtom().GetAtomMapNum(), bond.GetEndAtom().GetAtomMapNum()
        order = bond.GetBondTypeAsDouble()
        if order != int(order):
            return None
        bonds[(a, b) if a < b else (b, a)] = int(order)
    diag = {}
    for n, sym in elements.items():
        beta = sum(o for (i, j), o in bonds.items() if i == n or j == n)
        diag[n] = VALENCE[sym] - charges[n] - beta
    return diag, bonds, elements


def occupancies(diag, bonds, elements):
    """Z_ii + 2*beta_i per atom, keyed by element -- the quantity the table caps."""
    out = []
    for n, sym in elements.items():
        beta = sum(o for (i, j), o in bonds.items() if i == n or j == n)
        out.append((sym, diag[n] + 2 * beta))
    return out


def admissible(diag, bonds, elements, cap):
    for order in bonds.values():
        if order < 0 or order > 3:
            return False
    beta = defaultdict(int)
    for (i, j), o in bonds.items():
        beta[i] += o
        beta[j] += o
    for n, z in diag.items():
        if z < 0:
            return False
        if z + 2 * beta[n] > cap.get(elements[n], 8):
            return False
    return True


def order_component(diag, bonds, elements, cap, moves, indices):
    """First admissible permutation of one component's moves, or None."""
    for perm in itertools.permutations(indices):
        d, b = dict(diag), dict(bonds)
        ok = True
        for idx in perm:
            _, i, j, dii, djj, dij = moves[idx]
            d[i] += dii
            d[j] += djj
            key = (min(i, j), max(i, j))
            b[key] = b.get(key, 0) + dij
            if b[key] == 0:
                del b[key]
            if not admissible(d, b, elements, cap):
                ok = False
                break
        if ok:
            return list(perm), d, b
    return None


def components(moves):
    parent = list(range(len(moves)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    seen = {}
    for k, (_, i, j, *_rest) in enumerate(moves):
        for atom in (i, j):
            if atom in seen:
                a, b = find(seen[atom]), find(k)
                if a != b:
                    parent[a] = b
            seen[atom] = k
    groups = defaultdict(list)
    for k in range(len(moves)):
        groups[find(k)].append(k)
    return list(groups.values())


def has_admissible_order(diag, bonds, elements, cap, moves):
    comps = components(moves)
    if any(len(c) > MAX_COMPONENT for c in comps):
        return None  # not searched
    d, b = dict(diag), dict(bonds)
    for comp in comps:
        got = order_component(d, b, elements, cap, moves, comp)
        if got is None:
            return False
        _, d, b = got
    return True


def analyse(line, cap):
    rxn = line.strip().rpartition("|")[0]
    if ">>" not in rxn:
        return {"verdict": "malformed"}
    src, dst = rxn.split(">>")
    if src == dst:
        return {"verdict": "identity"}
    r, p = be_matrix(src), be_matrix(dst)
    if r is None or p is None:
        return {"verdict": "unparsed"}
    r_diag, r_bonds, r_elem = r
    p_diag, p_bonds, p_elem = p
    if set(r_elem) != set(p_elem):
        return {"verdict": "atom_set_differs"}

    delta = {}
    for key in set(r_bonds) | set(p_bonds):
        d = p_bonds.get(key, 0) - r_bonds.get(key, 0)
        if d:
            delta[key] = d
    if not delta:
        return {"verdict": "no_bond_change"}

    slots = []
    for (i, j), d in delta.items():
        table = MOVES_PLUS if d > 0 else MOVES_MINUS
        for _ in range(abs(d)):
            slots.append([(name, i, j, dii, djj, dij) for name, dii, djj, dij in table])
    if len(slots) > MAX_UNITS:
        return {"verdict": "too_large", "units": len(slots)}

    required = {n: p_diag[n] - r_diag[n] for n in r_diag}
    n_budget_ok, n_ordered, unsearched = 0, 0, 0
    first_moves = ()
    for combo in itertools.product(*slots):
        contrib = Counter()
        for _, i, j, dii, djj, _ in combo:
            contrib[i] += dii
            contrib[j] += djj
        if any(contrib.get(n, 0) != required[n] for n in required):
            continue
        n_budget_ok += 1
        got = has_admissible_order(r_diag, r_bonds, r_elem, cap, list(combo))
        if got is None:
            unsearched += 1
        elif got:
            n_ordered += 1
            if not first_moves:
                first_moves = tuple(m[0].split("_i")[0].split("_j")[0] for m in combo)

    if n_ordered:
        verdict = "decomposed"
    elif n_budget_ok and unsearched:
        verdict = "order_unsearched"
    elif n_budget_ok:
        verdict = "no_admissible_order"
    else:
        verdict = "no_move_assignment"
    return {"verdict": verdict, "units": len(slots),
            "budget_ok": n_budget_ok, "ordered": n_ordered,
            "move_types": first_moves}


def cap_chunk(lines):
    caps = defaultdict(int)
    for line in lines:
        rxn = line.strip().rpartition("|")[0]
        if ">>" not in rxn:
            continue
        for side in rxn.split(">>"):
            m = be_matrix(side)
            if m is None:
                continue
            for sym, occ in occupancies(*m):
                if occ > caps[sym]:
                    caps[sym] = occ
    return dict(caps)


def run_chunk(job):
    lines, cap = job
    verdicts, ambiguity, units, moves = Counter(), Counter(), Counter(), Counter()
    for line in lines:
        a = analyse(line, cap)
        verdicts[a["verdict"]] += 1
        if a["verdict"] == "decomposed":
            ambiguity[min(a["ordered"], 20)] += 1
            units[a["units"]] += 1
            # Which of the four moves the chemistry actually uses. Nobody has
            # reported this; it says how much of the alphabet earns its place.
            for name in a.get("move_types", ()):
                moves[name] += 1
    return verdicts, ambiguity, units, moves


def chunked(seq, n):
    size = max(1, (len(seq) + n - 1) // n)
    return [seq[i:i + size] for i in range(0, len(seq), size)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--files", nargs="+", required=True)
    ap.add_argument("--workers", type=int, default=32)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out_json", required=True)
    args = ap.parse_args()

    result = {}
    for path in args.files:
        lines = open(path).read().splitlines(keepends=True)
        if args.limit:
            lines = lines[: args.limit]
        pieces = chunked(lines, args.workers)

        with Pool(args.workers) as pool:
            caps = defaultdict(int)
            for c in pool.imap_unordered(cap_chunk, pieces):
                for sym, occ in c.items():
                    if occ > caps[sym]:
                        caps[sym] = occ
            cap = dict(caps)
            verdicts, ambiguity, units, moves = (Counter(), Counter(), Counter(), Counter())
            for v, a, u, mv in pool.imap_unordered(run_chunk, [(p, cap) for p in pieces]):
                verdicts.update(v)
                ambiguity.update(a)
                units.update(u)
                moves.update(mv)

        n = sum(verdicts.values())
        dec = verdicts.get("decomposed", 0)
        result[path.split("/")[-1]] = {
            "steps": n,
            "capacity_table": dict(sorted(cap.items())),
            "verdicts": dict(verdicts),
            "decomposed_pct": round(100.0 * dec / max(1, n), 2),
            "mean_orderings_when_decomposed": round(
                sum(k * v for k, v in ambiguity.items()) / max(1, sum(ambiguity.values())), 2),
            "orderings_hist": {str(k): ambiguity[k] for k in sorted(ambiguity)},
            "units_hist": {str(k): units[k] for k in sorted(units)},
            "move_type_census": dict(moves.most_common()),
        }
        print(json.dumps({path.split("/")[-1]: result[path.split("/")[-1]]}, indent=2))

    with open(args.out_json, "w") as fh:
        json.dump(result, fh, indent=2)


if __name__ == "__main__":
    main()
