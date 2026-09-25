#!/usr/bin/env python
"""Does label-free move recovery reproduce the chemist's arrows?

MAELLE (nguyen2026_maelle, arXiv:2608.27429, EPFL) claims the one thing AFM does
not: mechanism-like moves recovered from the two endpoints alone, with no
expert elementary-step annotation.  Its Table 1 marks the FlowER family -- and so
AFM, which trains on that corpus -- with a cross in the "Mech. step label-free"
column.  The claim is never validated against a chemist: the recovered moves are
called "pseudo mechanistic" (their section 4) and are checked only through
downstream product accuracy on USPTO-480K.

This measures it directly, on curated data they did not use, where the chemist's
arrows are recorded.  Nothing of theirs is needed but the rule: their move
recovery is fully specified in section 4.3 and Appendix C, and is reimplemented
here.  No model, no training, no checkpoint.

Their rule, verbatim in structure:
  * State: integer occupation in ELECTRON PAIRS over bonding sites e_ij, lone
    sites e_ii and per-atom hydrogen sites e_i^H (Appendix B).
  * Augment with a virtual site e_0 absorbing any imbalance, so transport is
    balanced (Appendix C, the two ~o formulas).
  * Cost C[e,e'] = min over reactant and product graphs of the shortest-path
    distance between the sites' constituent atoms; cost to/from e_0 a large
    constant c_0 (Appendix C).
  * Solve balanced integer transport; every off-diagonal entry becomes FLOW
    (pair moved), DEL (to e_0) or ADD (from e_0) -- their Eq. 8.

Comparison.  A FLOW of one pair from site a to site b is exactly the chemist's
two-electron arrow (2, a, b) in RMechDB/PMechDB grammar, so the recovered move
multiset and the curated multiset live in the same space.  Curated arrows are
canonicalised first (bond-to-bond arrows rewritten through their shared atom),
the same normalisation `rmechdb_arrows.py` applies before its own comparison --
otherwise we would be scoring drawing style, not electron flow.

Positive control (ADR-0004 section 2).  The same rows are run through this tree's
own model-free decomposition (`rmechdb_arrows.decompose`) in the same pass.  A
run in which the control also fails cannot separate "their rule does not recover
chemistry" from "our row handling is broken", and must not be reported as the
former.

Scope.  Polar only.  MAELLE's own Limitations say it "models electron pairs
rather than individual electrons, which precludes radical reactions involving
unpaired electrons", so RMechDB is out of its domain by construction; that
exclusion is reported as a count, not as a failure.

  .venv/bin/python maelle_ot_recovery.py \
      --csv ../../datasets/pmechdb_data/manually_curated_train.csv \
      --out_json results/maelle_ot_pmechdb.json
"""
import argparse
import csv
import json
from collections import Counter, defaultdict

import numpy as np
from scipy.optimize import linprog

from rdkit import Chem

from rmechdb_arrows import (
    reduced_matrix,
    parse_arrows,
    canonicalise_arrows,
    decompose,
    _PS,
)


def split_context(smiles):
    """Per mapped atom, separate implicit hydrogens from bonds to unmapped heavy
    atoms.  `reduced_matrix` sums the two into one `context` number; MAELLE keeps
    them apart -- a pooled hydrogen site sits ON the atom (distance 0) while a
    neighbouring heavy atom is a separate node whose bond site is one bond away.
    Lumping them makes unmapped neighbours look like zero-cost donors."""
    mol = Chem.MolFromSmiles(smiles, _PS)
    if mol is None:
        return None
    try:
        Chem.Kekulize(mol, clearAromaticFlags=True)
    except Exception:
        return None
    nh, un = {}, {}
    for atom in mol.GetAtoms():
        n = atom.GetAtomMapNum()
        if not n:
            continue
        nh[n] = atom.GetTotalNumHs()
        tot = 0
        for nb in atom.GetNeighbors():
            if not nb.GetAtomMapNum():
                o = mol.GetBondBetweenAtoms(atom.GetIdx(), nb.GetIdx()).GetBondTypeAsDouble()
                if o != int(o):
                    return None
                tot += int(o)
        un[n] = tot
    return nh, un

INF = 10**6


# ---------------------------------------------------------------- their state

def occupation(m, nh, un):
    """BE matrix -> MAELLE occupation in electron PAIRS, or None if unpaired.

    Sites: ('B', i, j) bonding, ('L', i) lone, ('H', i) the per-atom pooled
    hydrogen/context site.  `context` is bond order to unmapped neighbours plus
    implicit hydrogens; the caller has already checked it is equal on both sides,
    so these sites carry no net change and act only as spectator donors, which is
    what MAELLE's e_i^H does.

    Returns (occ, odd_atoms).  `odd_atoms` is non-empty exactly when some atom
    carries an odd non-bonding electron count, i.e. an unpaired electron, which
    MAELLE's pair-valued occupation cannot represent at all.
    """
    diag, bonds, elements, context = m
    odd = sorted(n for n, z in diag.items() if z % 2)
    occ = {}
    for (i, j), order in bonds.items():
        occ[("B", i, j)] = order
    for n, z in diag.items():
        occ[("L", n)] = z // 2
    for n in context:
        occ[("H", n)] = nh[n]      # pooled hydrogens: on the atom, distance 0
        # Bonds to unmapped heavy atoms.  Kept as their own site only so the
        # spectator check can test hydrogens and heavy context separately; the
        # COST is that of any bond site at this atom, i.e. zero distance, because
        # their cost minimises over a site's constituent atoms and this bond has
        # the mapped atom as one of them.
        occ[("U", n)] = un[n]
    return occ, odd


def site_atoms(site):
    return (site[1], site[2]) if site[0] == "B" else (site[1],)


def cost_matrix(sites, r_bonds, p_bonds, atoms, c0):
    """C[e,e'] = min over the two graphs of shortest-path distance between the
    sites' constituent atoms; large constant to/from the virtual site."""

    def apsp(bonds):
        idx = {a: k for k, a in enumerate(atoms)}
        n = len(atoms)
        d = np.full((n, n), INF, dtype=np.int64)
        np.fill_diagonal(d, 0)
        for (i, j) in bonds:
            if i in idx and j in idx:
                d[idx[i], idx[j]] = d[idx[j], idx[i]] = 1
        for k in range(n):
            d = np.minimum(d, d[:, k, None] + d[None, k, :])
        return idx, d

    ridx, rd = apsp(r_bonds)
    pidx, pd = apsp(p_bonds)
    n = len(sites)
    C = np.zeros((n + 1, n + 1), dtype=np.int64)
    for a, ea in enumerate(sites):
        for b, eb in enumerate(sites):
            best = INF
            for va in site_atoms(ea):
                for vb in site_atoms(eb):
                    best = min(best, rd[ridx[va], ridx[vb]], pd[pidx[va], pidx[vb]])
            C[a, b] = best
    C[n, :] = C[:, n] = c0
    np.fill_diagonal(C, 0)   # a site to itself is distance zero
    return C


def transport(ox, oy, C):
    """Balanced integer optimal transport.  The marginal constraint matrix is
    totally unimodular and the marginals are integral, so an LP vertex is
    integral; HiGHS returns a vertex."""
    n = len(ox)
    A, b = [], []
    for i in range(n):                                   # row marginals
        row = np.zeros(n * n)
        row[i * n:(i + 1) * n] = 1
        A.append(row)
        b.append(ox[i])
    for j in range(n - 1):                               # column marginals (one dropped: redundant)
        col = np.zeros(n * n)
        col[j::n] = 1
        A.append(col)
        b.append(oy[j])
    res = linprog(C.reshape(-1).astype(float), A_eq=np.array(A), b_eq=np.array(b),
                  bounds=(0, None), method="highs-ds")   # dual simplex: a vertex, hence integral
    if not res.success:
        return None
    return np.rint(res.x.reshape(n, n)).astype(int)


def count_optimal_plans(ox, oy, C, k, rng):
    """How many DISTINCT mechanisms does their objective call optimal?

    Their cost is a coarse integer graph distance, so the optimum is rarely
    unique and the plan a solver returns is decided by its tie-breaking, not by
    chemistry.  Re-solve k times with an infinitesimal random perturbation of the
    cost (small enough that it can only break ties between integer-cost optima),
    keep the solutions whose true integer cost equals the optimum, and count how
    many distinct arrow multisets appear.  This is a LOWER BOUND on the number of
    mechanisms their objective cannot distinguish.
    """
    base = transport(ox, oy, C)
    if base is None:
        return None, None
    opt = int((C * base).sum())
    seen = set()
    for _ in range(k):
        noise = rng.random(C.shape) * 1e-6
        T = transport(ox, oy, C + noise)
        if T is None or int((C * T).sum()) != opt:
            continue
        seen.add(tuple(sorted(
            (a, b, int(T[a, b])) for a in range(T.shape[0]) for b in range(T.shape[1])
            if a != b and T[a, b])))
    return opt, len(seen)


def plan_to_arrows(T, sites):
    """Their Eq. 8, expressed in the curated arrow grammar.

    A FLOW of one pair a->b is the chemist's (2, a, b).  DEL and ADD have no
    arrow: a chemist never draws a pair appearing from or vanishing into nothing.
    They are counted, not translated.
    """
    n = len(sites)

    def slot(site):
        return (site[1], site[2]) if site[0] == "B" else site[1]

    arrows, n_del, n_add, n_ctx = Counter(), 0, 0, 0
    for a in range(n + 1):
        for b in range(n + 1):
            if a == b or T[a, b] == 0:
                continue
            k = int(T[a, b])
            if a == n:
                n_add += k
            elif b == n:
                n_del += k
            else:
                if sites[a][0] == "H" or sites[b][0] == "H":
                    n_ctx += k
                arrows[(2, slot(sites[a]), slot(sites[b]))] += k
    return arrows, n_del, n_add, n_ctx


def chemist_plan_cost(canonical, sites, C, ox, oy):
    """Score the chemist's own arrows AS a transport plan under their cost.

    This is the measurement that decides the experiment.  Asking only whether the
    solver's chosen plan equals the chemist's confuses two very different
    criticisms, because their cost is a coarse integer graph distance with many
    ties and the optimum is rarely unique.  The sharp questions are:
      (a) is the chemist's mechanism a FEASIBLE transport plan at all, and
      (b) if so, is it OPTIMAL under their objective?
    If it is optimal, their rule admits the chemist's answer but cannot single it
    out -- under-determined.  If it costs strictly more, their objective actively
    prefers a different electron flow from the one chemistry takes.
    """
    idx = {s_: k for k, s_ in enumerate(sites)}

    def sites_of(a, b):
        """RMechDB/PMechDB sink grammar, read off the data.

        A bond source is a tuple.  A bare-integer SINK is ambiguous in the raw
        grammar and the data resolves it by the source: after a bond source it is
        the lone pair on that atom ("20,21=21"), but after an atom source it is
        the NEW bond between the two ("10=20" forms sigma(10,20), the same reading
        `parse_arrows` applies only when the file writes the trailing comma
        "10=20,").  Reading the bare form as a lone pair puts the electrons on the
        wrong site and makes the chemist's own mechanism look infeasible.
        """
        sa = ("B", a[0], a[1]) if isinstance(a, tuple) else ("L", a)
        if isinstance(b, tuple):
            sb = ("B", b[0], b[1])
        elif isinstance(a, int):
            i, j = sorted((a, b))
            sb = ("B", i, j)
        else:
            sb = ("L", b)
        return sa, sb

    net = [0] * len(sites)
    cost = 0
    for (n, a, b), k in canonical.items():
        if n != 2:
            return None, None          # a fish-hook: not a pair transport at all
        sa, sb = sites_of(a, b)
        if sa not in idx or sb not in idx:
            return None, None
        net[idx[sa]] -= k
        net[idx[sb]] += k
        cost += k * int(C[idx[sa], idx[sb]])
    want = [y - x for x, y in zip(ox[:len(sites)], oy[:len(sites)])]
    return (cost if net == want else None), net == want


# ---------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--out_json", required=True)
    ap.add_argument("--c0", type=int, default=100,
                    help="penalty for the virtual site; their 'large constant'. Sweep it.")
    ap.add_argument("--examples", type=int, default=6)
    ap.add_argument("--degeneracy_k", type=int, default=20,
                    help="random tie-break re-solves per row; 0 to skip")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    rng = np.random.default_rng(args.seed)
    degen = []

    rows = []
    with open(args.csv) as fh:
        for rec in csv.reader(fh):
            if not rec or ">>" not in rec[0]:
                continue
            smirks, _, code = rec[0].strip().rpartition(" ")
            rows.append((smirks, code))

    cap = defaultdict(int)
    parsed = []
    for smirks, code in rows:
        src, _, dst = smirks.partition(">>")
        r, p = reduced_matrix(src), reduced_matrix(dst)
        parsed.append((r, p, code, src, dst))
        for m in (r, p):
            if m is None:
                continue
            diag, bonds, elements, context = m
            for n, sym in elements.items():
                beta = sum(o for (i, j), o in bonds.items() if i == n or j == n) + context[n]
                cap[sym] = max(cap[sym], diag[n] + 2 * beta)
    cap = dict(cap)

    v = Counter()
    move_stats = Counter()
    examples = []
    for r, p, code, src, dst_smiles in parsed:
        if r is None or p is None:
            v["unparsed"] += 1
            continue
        if set(r[2]) != set(p[2]):
            v["mapped_set_differs"] += 1
            continue
        if r[3] != p[3]:
            v["context_changed"] += 1
            continue
        curated = parse_arrows(code)
        if curated is None:
            v["bad_arrow_code"] += 1
            continue
        canonical, _ = canonicalise_arrows(curated)
        if canonical is None:
            v["bond_to_bond_without_shared_atom"] += 1
            continue

        ctx_r, ctx_p = split_context(src), split_context(dst_smiles)
        if ctx_r is None or ctx_p is None:
            v["context_unparsed"] += 1
            continue
        if ctx_r[0] != ctx_p[0] or ctx_r[1] != ctx_p[1]:
            v["h_or_unmapped_changed"] += 1
            continue
        ox_map, odd_r = occupation(r, *ctx_r)
        oy_map, odd_p = occupation(p, *ctx_p)
        if odd_r or odd_p:
            v["unpaired_electron_not_representable"] += 1
            continue
        v["representable"] += 1

        sites = sorted(set(ox_map) | set(oy_map))
        atoms = sorted(r[2])
        ox = [ox_map.get(s, 0) for s in sites]
        oy = [oy_map.get(s, 0) for s in sites]
        gain = sum(max(b - a, 0) for a, b in zip(ox, oy))
        loss = sum(max(a - b, 0) for a, b in zip(ox, oy))
        ox.append(gain)          # their augmented ~o_x
        oy.append(loss)          # their augmented ~o_y

        C = cost_matrix(sites, r[1], p[1], atoms, args.c0)
        T = transport(ox, oy, C)
        if T is None:
            v["ot_failed"] += 1
            continue

        if args.degeneracy_k:
            _, n_distinct = count_optimal_plans(ox, oy, C, args.degeneracy_k, rng)
            if n_distinct:
                degen.append(n_distinct)

        ours, n_del, n_add, n_ctx = plan_to_arrows(T, sites)
        move_stats["rows_with_del_or_add"] += 1 if (n_del or n_add) else 0
        move_stats["rows_touching_context_site"] += 1 if n_ctx else 0
        move_stats["total_del"] += n_del
        move_stats["total_add"] += n_add

        # positive control: this tree's own decomposition on the identical row
        verdict, found = decompose(r, p, cap)
        control_ok = verdict == "decomposed"
        v[f"control_{verdict}"] += 1

        opt_cost = int((C[:len(sites) + 1, :len(sites) + 1] * T).sum())
        ch_cost, feasible = chemist_plan_cost(canonical, sites, C, ox, oy)
        if feasible is None:
            v["chemist_plan_not_pair_transport"] += 1
        elif not feasible:
            v["chemist_plan_infeasible_marginals"] += 1
        elif ch_cost == opt_cost:
            v["chemist_plan_IS_optimal"] += 1
        elif ch_cost > opt_cost:
            v["chemist_plan_costs_MORE_than_optimum"] += 1
            move_stats["excess_cost_total"] += ch_cost - opt_cost
        else:
            v["chemist_plan_cheaper_than_lp_BUG"] += 1

        if ours == canonical:
            v["ot_matches_chemist"] += 1
        else:
            v["ot_differs_from_chemist"] += 1
            if len(examples) < args.examples:
                examples.append({
                    "reactant": src,
                    "arrows_curated": sorted(map(str, curated.elements())),
                    "arrows_canonical": sorted(map(str, canonical.elements())),
                    "arrows_from_their_OT": sorted(map(str, ours.elements())),
                    "del": n_del, "add": n_add, "context_moves": n_ctx,
                    "our_control_decomposed": control_ok,
                })

    rep = v["representable"]
    matched = v["ot_matches_chemist"]
    out = {
        "csv": args.csv,
        "c0": args.c0,
        "rows": len(rows),
        "verdicts": dict(v),
        "move_stats": dict(move_stats),
        "ot_match_pct_of_representable": round(100.0 * matched / max(1, rep), 2),
        "chemist_plan_optimal_pct_of_scored": round(
            100.0 * v["chemist_plan_IS_optimal"]
            / max(1, v["chemist_plan_IS_optimal"] + v["chemist_plan_costs_MORE_than_optimum"]), 2),
        "control_decomposed_pct_of_representable":
            round(100.0 * v["control_decomposed"] / max(1, rep), 2),
        "degeneracy": {
            "rows_scored": len(degen),
            "resolves_per_row": args.degeneracy_k,
            "distinct_optimal_plans_mean": round(float(np.mean(degen)), 3) if degen else None,
            "distinct_optimal_plans_median": float(np.median(degen)) if degen else None,
            "rows_with_a_unique_optimum": int(sum(1 for d in degen if d == 1)),
            "note": "lower bound: at most `resolves_per_row` distinct plans can be observed",
        },
        "examples_of_disagreement": examples,
    }
    with open(args.out_json, "w") as fh:
        json.dump(out, fh, indent=2)
    print(json.dumps({k: out[k] for k in
                      ("rows", "verdicts", "move_stats",
                       "ot_match_pct_of_representable",
                       "chemist_plan_optimal_pct_of_scored", "degeneracy",
                       "control_decomposed_pct_of_representable")}, indent=2))


if __name__ == "__main__":
    main()
