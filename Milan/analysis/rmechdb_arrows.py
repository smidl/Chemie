#!/usr/bin/env python
"""Do the alphabet's recovered moves agree with RMechDB's curated curly arrows?

Turns the uniqueness result of decompose_steps.py into a correctness result. The
FlowER conversion of RMechDB drops the arrow annotations; the registered download
keeps them, so for the first time we can ask not just "does the alphabet admit a
mechanism" but "is it the chemist's mechanism".

The comparable published number: ArrowFinder (miller2025_arrowfinder) matched the
curated arrow annotation exactly in 1230 of 1337 PMechDB cases (92.0%), with 101
(7.6%) recovering the product by a "functionally equivalent" but differently
drawn mechanism.

RMechDB arrow grammar, read off the data: arrows separated by ";", each
"SOURCE SEP SINK" where a bare map number is a lone-electron slot and a comma
pair is a bond; SEP "-" moves ONE electron (fish-hook), "=" moves TWO (pair).
The alphabet's four moves expand into that grammar exactly:

    LONE_TO_BOND(i->j)   i=i,j
    BOND_TO_LONE(i,j->j) i,j=j
    HOMOLYSIS(i,j)       i,j-i ; i,j-j
    COLLIGATION(i,j)     i-i,j ; j-i,j

so a recovered move multiset can be expanded and compared with the curated
multiset directly.

Two representational facts to expect, not to treat as bugs. A chemist may route
a fish-hook straight from one bond into another ("20,21-10,20"), where the
alphabet must spend two moves passing through the atom, so arrow counts differ
while the net electron flow is identical. And the same net flow may admit several
drawings. Both are the phenomenon ArrowFinder's 101 cases measure.

RMechDB maps ONLY the reacting atoms. The bond-electron matrix is therefore built
over the mapped atoms alone, with every unmapped neighbour and implicit hydrogen
folded into a per-atom context degree -- the reduction afm.pdf itself uses. It is
valid exactly when that context is a spectator, which is checked per row and
reported rather than assumed.

  .venv/bin/python rmechdb_arrows.py --csv rmechdb_data/all.csv --out_json out.json

``--dump_targets PATH`` additionally writes, for every exact-arrow-match row, the
reactant SMILES and the winning move sequence (atom-map-number space, same
convention as MOVES_PLUS/MOVES_MINUS) -- everything this script already computes
but did not use to persist. Downstream consumer: ``experiments/human_plausibility/``.
"""
import argparse
import csv
import itertools
import json
import sys
from collections import Counter, defaultdict

from rdkit import Chem, RDLogger

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from decompose_steps import (  # noqa: E402
    MOVES_MINUS, MOVES_PLUS, VALENCE, admissible, components, order_component,
)

RDLogger.DisableLog("rdApp.*")

_PS = Chem.SmilesParserParams()
_PS.removeHs = False
_PS.sanitize = True

MAX_UNITS = 10
MAX_COMPONENT = 7


def reduced_matrix(smiles):
    """BE matrix over mapped atoms only.

    Returns (diag, bonds, elements, context) or None. `context` is the per-atom
    bond order to everything unmapped plus implicit hydrogens; it must be equal
    on both sides for the reduction to be sound.
    """
    mol = Chem.MolFromSmiles(smiles, _PS)
    if mol is None:
        return None
    try:
        Chem.Kekulize(mol, clearAromaticFlags=True)
    except Exception:
        return None

    mapped = {}
    for atom in mol.GetAtoms():
        n = atom.GetAtomMapNum()
        if n:
            if atom.GetSymbol() not in VALENCE:
                return None
            mapped[n] = atom
    if not mapped:
        return None

    elements = {n: a.GetSymbol() for n, a in mapped.items()}
    bonds, context = {}, {}
    for n, atom in mapped.items():
        ctx = atom.GetTotalNumHs()
        for nb in atom.GetNeighbors():
            order = mol.GetBondBetweenAtoms(atom.GetIdx(), nb.GetIdx()).GetBondTypeAsDouble()
            if order != int(order):
                return None
            order = int(order)
            m = nb.GetAtomMapNum()
            if m and m in mapped:
                bonds[(n, m) if n < m else (m, n)] = order
            else:
                ctx += order
        context[n] = ctx

    diag = {}
    for n, atom in mapped.items():
        inner = sum(o for (i, j), o in bonds.items() if i == n or j == n)
        diag[n] = VALENCE[elements[n]] - atom.GetFormalCharge() - inner - context[n]
    return diag, bonds, elements, context


def parse_arrows(code):
    """'10,11-10;20-10,20' -> multiset of (n_electrons, source, sink) tuples.

    A slot is an int (lone electrons on that atom) or a sorted 2-tuple (a bond).
    """
    out = []
    for piece in code.split(";"):
        piece = piece.strip()
        if not piece:
            continue
        if "=" in piece:
            sep, n = "=", 2
        elif "-" in piece:
            sep, n = "-", 1
        else:
            return None
        src, _, dst = piece.partition(sep)

        def slot(s):
            # Three pieces in the released file are malformed (a stray ";" and two
            # rows reading "22,23-21-22", apparently a typo for "21,22"). Reject
            # the row rather than crash on it.
            try:
                parts = [int(x) for x in s.split(",")]
            except ValueError:
                return None
            if len(parts) == 1:
                return parts[0]
            if len(parts) == 2:
                return tuple(sorted(parts))
            return None

        # PMechDB writes a bond-forming sink with a trailing comma: "10=20," is
        # "the pair on 10 forms the bond to 20", i.e. the sink orbital is the new
        # sigma(source, 20), not a lone pair on 20. 1,156 of the curated rows use
        # it. Resolve it against the source before parsing the slot; without this
        # the row is rejected and the arrow comparison silently loses them.
        a = slot(src)
        if dst.endswith(",") and isinstance(a, int):
            b = slot(dst[:-1])
            if isinstance(b, int):
                b = tuple(sorted((a, b)))
        else:
            b = slot(dst)
        if a is None or b is None:
            return None
        out.append((n, a, b))
    return Counter(out) if out else None


def canonicalise_arrows(curated):
    """Rewrite every bond-to-bond arrow through the atom the two bonds share.

    A chemist may move electrons straight from bond (a,k) into bond (k,b); the
    alphabet has no such move and writes the same flow as two arrows that pass
    through k, ``(a,k) -> k ; k -> (k,b)`` (a fish-hook each way for one
    electron, the two halves of a bond migration for a pair, Remark "bond
    migration is a composition"). The shared atom is unique, so the rewrite
    is deterministic and the comparison becomes one of electron flow rather
    than of drawing. Returns (canonical multiset, number of arrows rewritten),
    or (None, n) if some bond-to-bond arrow has no shared atom.
    """
    out, rewritten = Counter(), 0
    for (n, a, b), count in curated.items():
        if isinstance(a, tuple) and isinstance(b, tuple):
            shared = set(a) & set(b)
            if len(shared) != 1:
                return None, rewritten
            k = shared.pop()
            out[(n, a, k)] += count
            out[(n, k, b)] += count
            rewritten += count
        else:
            out[(n, a, b)] += count
    return out, rewritten


def moves_to_arrows(moves):
    """Expand a recovered move multiset into the curated arrow grammar."""
    out = Counter()
    for name, i, j, dii, djj, dij in moves:
        pair = tuple(sorted((i, j)))
        if name.startswith("LONE_TO_BOND"):
            donor = i if dii == -2 else j
            out[(2, donor, pair)] += 1
        elif name.startswith("BOND_TO_LONE"):
            acceptor = j if djj == +2 else i
            out[(2, pair, acceptor)] += 1
        elif name == "HOMOLYSIS":
            out[(1, pair, i)] += 1
            out[(1, pair, j)] += 1
        elif name == "COLLIGATION":
            out[(1, i, pair)] += 1
            out[(1, j, pair)] += 1
    return out


def decompose(r, p, cap):
    """All move multisets with a matching electron budget AND an admissible order."""
    r_diag, r_bonds, r_elem, _ = r
    p_diag, p_bonds, p_elem, _ = p
    delta = {}
    for key in set(r_bonds) | set(p_bonds):
        d = p_bonds.get(key, 0) - r_bonds.get(key, 0)
        if d:
            delta[key] = d
    if not delta:
        return "no_bond_change", []

    slots = []
    for (i, j), d in delta.items():
        table = MOVES_PLUS if d > 0 else MOVES_MINUS
        for _ in range(abs(d)):
            slots.append([(name, i, j, dii, djj, dij) for name, dii, djj, dij in table])
    if len(slots) > MAX_UNITS:
        return "too_large", []

    required = {n: p_diag[n] - r_diag[n] for n in r_diag}
    found = []
    for combo in itertools.product(*slots):
        contrib = Counter()
        for _, i, j, dii, djj, _ in combo:
            contrib[i] += dii
            contrib[j] += djj
        if any(contrib.get(n, 0) != required[n] for n in required):
            continue
        comps = components(list(combo))
        if any(len(c) > MAX_COMPONENT for c in comps):
            continue
        d, b, ok, ordered = dict(r_diag), dict(r_bonds), True, []
        for comp in comps:
            got = order_component(d, b, r_elem, cap, list(combo), comp)
            if got is None:
                ok = False
                break
            perm, d, b = got
            # Components share no atoms (by construction of `components()`), so
            # applying one component's own admissible order fully before the next
            # cannot un-admit a step already checked; but *within* a component the
            # order matters -- `combo`'s own order is just its slot-assignment
            # order and is not guaranteed admissible on its own (a step can be
            # valid only in the order `order_component` found, e.g. a bond must
            # form before the atom that will need its new radical can donate it).
            ordered.extend(combo[idx] for idx in perm)
        if ok:
            found.append(ordered)
    return ("decomposed" if found else "no_decomposition"), found


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out_json", required=True)
    ap.add_argument("--examples", type=int, default=6)
    ap.add_argument("--dump_targets", default=None,
                     help="Also write exact-match (reactant SMILES, move sequence) pairs here.")
    ap.add_argument("--dump_multistep", default=None,
                     help="Also write one admissible multi-move (reactant SMILES, move sequence) "
                          "pair per decomposed reaction whose first found decomposition has >=2 "
                          "moves -- regardless of whether it matches the curated arrows. For testing "
                          "properties of alphabet-admissible intermediates, not human agreement.")
    args = ap.parse_args()

    rows = []
    with open(args.csv) as fh:
        for rec in csv.reader(fh):
            if not rec or ">>" not in rec[0]:
                continue
            smirks, _, code = rec[0].strip().rpartition(" ")
            rows.append((smirks, code, rec[1:] if len(rec) > 1 else []))

    # Capacity table measured from these endpoints, as in decompose_steps.py.
    cap = defaultdict(int)
    parsed = []
    for smirks, code, meta in rows:
        if ">>" not in smirks:
            continue
        src, _, dst = smirks.partition(">>")
        r, p = reduced_matrix(src), reduced_matrix(dst)
        parsed.append((r, p, code, meta, src))
        for m in (r, p):
            if m is None:
                continue
            diag, bonds, elements, context = m
            for n, sym in elements.items():
                beta = sum(o for (i, j), o in bonds.items() if i == n or j == n) + context[n]
                occ = diag[n] + 2 * beta
                if occ > cap[sym]:
                    cap[sym] = occ
    cap = dict(cap)

    verdicts, arrow_cmp, examples = Counter(), Counter(), []
    three_centre = Counter()
    counts_curated, counts_ours = Counter(), Counter()
    targets = []
    multistep = []
    for r, p, code, meta, src in parsed:
        if r is None or p is None:
            verdicts["unparsed"] += 1
            continue
        if set(r[2]) != set(p[2]):
            verdicts["mapped_set_differs"] += 1
            continue
        if r[3] != p[3]:
            verdicts["context_changed"] += 1   # unmapped environment not a spectator
            continue
        curated = parse_arrows(code)
        if curated is None:
            verdicts["bad_arrow_code"] += 1
            continue

        # A curated arrow whose source AND sink are both bonds is a direct
        # bond-to-bond transfer -- a three-centre event.  The four-move alphabet
        # has no such move: it must route the electron through the shared atom,
        # asserting a discrete radical intermediate where the chemist drew a
        # concerted step.  This is exactly the extension afm.pdf's Limitation (iv)
        # anticipates, so counting it says how often that extension is needed.
        if any(isinstance(a, tuple) and isinstance(b, tuple) for _, a, b in curated):
            three_centre["curated_has_bond_to_bond"] += 1
        else:
            three_centre["curated_all_expressible"] += 1

        verdict, found = decompose(r, p, cap)
        verdicts[verdict] += 1
        if verdict != "decomposed":
            continue

        if args.dump_multistep and len(found[0]) >= 2:
            # Any admissible decomposition demonstrates real, alphabet-legal
            # intermediates -- doesn't need to match the curated arrows, unlike
            # `--dump_targets`. `found[0]`: whichever the search returned first.
            multistep.append({
                "reactant": src,
                "moves": [[name, i, j] for name, i, j, *_ in found[0]],
                "n_moves": len(found[0]),
                "meta": meta,
            })

        ours = [moves_to_arrows(m) for m in found]
        counts_curated[sum(curated.values())] += 1
        # `ours` holds arrow Counters; `found` holds move lists. Count arrows.
        counts_ours[min(sum(a.values()) for a in ours)] += 1
        if any(a == curated for a in ours):
            arrow_cmp["exact_match_as_drawn"] += 1
        canonical, rewritten = canonicalise_arrows(curated)
        if canonical is None:
            arrow_cmp["bond_to_bond_without_shared_atom"] += 1
            continue
        if rewritten:
            arrow_cmp["rows_with_bond_to_bond_arrows"] += 1
        matches = [combo for combo, a in zip(found, ours) if a == canonical]
        if matches:
            arrow_cmp["same_electron_flow"] += 1
            arrow_cmp[f"same_flow_{len(matches[0])}_moves"] += 1
            if args.dump_targets:
                # `matches[0]`: one admissible move sequence expanding to the
                # chemist's (canonicalised) arrows, in the (name, i, j, dii, djj,
                # dij) form `decompose()` returns -- atom-map-number space.
                targets.append({
                    "reactant": src,
                    "moves": [[name, i, j] for name, i, j, *_ in matches[0]],
                    "n_moves": len(matches[0]),
                    "arrows_rewritten": rewritten,
                    "meta": meta,
                })
        else:
            arrow_cmp["different_flow"] += 1
            cls = meta[2] if len(meta) > 2 else "?"
            arrow_cmp[f"different_flow_{cls}"] += 1
            arrow_cmp[f"different_flow_{cls}_curated_arrows_{sum(curated.values())}"] += 1
            if len(examples) < args.examples:
                examples.append({
                    "arrows_curated": sorted(map(str, curated.elements())),
                    "arrows_canonical": sorted(map(str, canonical.elements())),
                    "arrows_ours": sorted(map(str, ours[0].elements())),
                    "meta": meta,
                })

    dec = verdicts.get("decomposed", 0)
    matched = arrow_cmp.get("same_electron_flow", 0)
    out = {
        "csv": args.csv,
        "rows": len(rows),
        "capacity_table": dict(sorted(cap.items())),
        "verdicts": dict(verdicts),
        "decomposed_pct_of_rows": round(100.0 * dec / max(1, len(rows)), 2),
        "arrow_comparison": dict(arrow_cmp),
        "three_centre": dict(three_centre),
        "exact_arrow_match_pct_of_decomposed": round(100.0 * matched / max(1, dec), 2),
        "curated_arrow_count_hist": {str(k): v for k, v in sorted(counts_curated.items())},
        "our_arrow_count_hist": {str(k): v for k, v in sorted(counts_ours.items())},
        "examples_of_disagreement": examples,
    }
    with open(args.out_json, "w") as fh:
        json.dump(out, fh, indent=2)
    if args.dump_targets:
        with open(args.dump_targets, "w") as fh:
            json.dump(targets, fh, indent=2)
        print(f"Wrote {len(targets)} exact-match targets to {args.dump_targets}")
    if args.dump_multistep:
        with open(args.dump_multistep, "w") as fh:
            json.dump(multistep, fh, indent=2)
        print(f"Wrote {len(multistep)} multi-move decompositions to {args.dump_multistep}")
    print(json.dumps({k: v for k, v in out.items() if k != "examples_of_disagreement"}, indent=2))
    for e in examples[:3]:
        print("\ncurated:", e["arrows_curated"], "\nours   :", e["arrows_ours"], "\nmeta   :", e["meta"])


if __name__ == "__main__":
    main()
