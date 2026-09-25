#!/usr/bin/env python
"""Read the per-step roll-out log of `instrumented_rollout.py` against the
hypotheses of problem02-termination.md. Works for the RMechDB log (has `meta`)
and the FlowER control log (no `meta`).

    .venv/bin/python analyze_instrumented.py results/instrumented_rmechdb.jsonl
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from statistics import mean, median


def pct(k, n):
    return 100 * k / n if n else float("nan")


def bucket(v, edges):
    for lo, hi, lab in edges:
        if lo <= v < hi:
            return lab
    return f">={edges[-1][1]}"


ADM_EDGES = [(0, 20, "<20"), (20, 40, "20-39"), (40, 60, "40-59"), (60, 90, "60-89"), (90, 130, "90-129"), (130, 10**6, "130+")]
N_EDGES = [(0, 10, "<10"), (10, 15, "10-14"), (15, 20, "15-19"), (20, 30, "20-29"), (30, 50, "30-49"), (50, 10**6, "50+")]


def main(path):
    recs = [json.loads(l) for l in open(path)]
    has_meta = any(r.get("meta") for r in recs)
    chains = []
    for r in recs:
        for c in r["chains"]:
            c = dict(c)
            c["meta"] = r.get("meta")
            c["stage"] = r["meta"][1] if r.get("meta") else None
            c["rclass"] = r["meta"][2] if r.get("meta") else None
            c["n_atoms"] = r["n_atoms"]
            c["reactant_n_odd"] = r["reactant_n_odd_diag"]
            c["index"] = r["index"]
            chains.append(c)
    n = len(chains)
    stuck = [c for c in chains if not c["stopped"]]
    stopped = [c for c in chains if c["stopped"]]
    print(f"file: {path}")
    print(f"reactants={len(recs)} chains={n} stuck(never chose Stop)={len(stuck)} ({pct(len(stuck), n):.1f}%)  "
          f"stopped={len(stopped)}  immediate-stop(0 moves)={sum(c['n_moves']==0 for c in chains)} ({pct(sum(c['n_moves']==0 for c in chains), n):.1f}%)")
    print(f"n_moves of stopped chains: " + ", ".join(f"{k}:{v}" for k, v in sorted(Counter(c['n_moves'] for c in stopped).items())))

    # --- A. stuck rate by groups
    def group_stuck(key, label):
        g = defaultdict(lambda: [0, 0])
        for c in chains:
            g[key(c)][1] += 1
            g[key(c)][0] += (not c["stopped"])
        print(f"\n-- stuck rate by {label} --")
        for k in sorted(g, key=lambda x: (x is None, str(x))):
            s, t = g[k]
            print(f"  {str(k):<14} chains={t:<6} stuck={pct(s, t):5.1f}%")
    if has_meta:
        group_stuck(lambda c: c["stage"], "stage")
        group_stuck(lambda c: c["rclass"], "reaction class")
    group_stuck(lambda c: min(c["reactant_n_odd"], 3), "odd-diagonal atoms in reactant (radical centres, capped 3)")
    group_stuck(lambda c: bucket(c["n_atoms"], N_EDGES), "atom count N")

    # --- B. p(Stop) at the reactant (position 0) and the first decision
    p0 = [c["steps"][0]["p_stop"] for c in chains if c["steps"]]
    print(f"\n-- position 0 (state = reactant, Stop always offered since B_r in Sector) --")
    print(f"  p(Stop|B_r): mean={mean(p0):.3f} median={median(p0):.3f}; chains choosing Stop at k=0: {pct(sum(c['n_moves']==0 for c in chains), n):.1f}%")
    if has_meta:
        g = defaultdict(list)
        for c in chains:
            g[c["stage"]].append(c["steps"][0]["p_stop"])
        for k, v in g.items():
            print(f"    {k:<12} mean p(Stop|B_r)={mean(v):.3f}")

    # --- C. Sector visits along the chain
    def sector_stats(group, label):
        offered_frac = []; last_offered = []; reenter = []; p_when_offered = []
        for c in group:
            moves = [s for s in c["steps"] if s["move"] != "STOP"]
            if not moves:
                continue
            off = [s["stop_offered"] for s in moves]
            offered_frac.append(sum(off) / len(off))
            last = max((k for k, o in enumerate(off) if o), default=-1)
            last_offered.append(last)
            reenter.append(sum(off[1:]))
            p_when_offered += [s["p_stop"] for s in moves if s["stop_offered"]]
        print(f"\n-- Sector membership along {label} chains (positions where a move was taken) --")
        print(f"  fraction of positions with Stop offered: mean={mean(offered_frac):.3f}")
        print(f"  last position at which Stop was offered: " + ", ".join(f"{k}:{v}" for k, v in sorted(Counter(last_offered).items())))
        print(f"  chains that never re-enter Sector after position 0: {pct(sum(r==0 for r in reenter), len(reenter)):.1f}%")
        print(f"  p(Stop) when offered (moves taken instead): mean={mean(p_when_offered):.3f} median={median(p_when_offered):.3f}")
    sector_stats(stuck, "STUCK")
    sector_stats(stopped, "STOPPED")

    # --- D. inverse moves (Remark: alphabet closed under inversion)
    def inverse_rate(group):
        k = t = 0
        for c in group:
            mv = [s for s in c["steps"] if s["move"] != "STOP"]
            for s in mv[1:]:
                t += 1; k += s["inverse_of_previous"]
        return pct(k, t), t
    print(f"\n-- immediate undo (move k is the alphabet inverse of move k-1) --")
    print(f"  stuck chains:   {inverse_rate(stuck)[0]:.1f}% of {inverse_rate(stuck)[1]} moves")
    print(f"  stopped chains: {inverse_rate(stopped)[0]:.1f}% of {inverse_rate(stopped)[1]} moves")

    # --- E. p(Stop) vs number of admissible classes and vs N, at offered positions
    print(f"\n-- p(Stop) when offered, by number of competing admissible move classes --")
    g = defaultdict(list)
    for c in chains:
        for s in c["steps"]:
            if s["stop_offered"]:
                g[bucket(s["n_admissible"], ADM_EDGES)].append(s["p_stop"])
    for k in [e[2] for e in ADM_EDGES] + [f">={ADM_EDGES[-1][1]}"]:
        if g.get(k):
            print(f"  {k:<8} n={len(g[k]):<7} mean p(Stop)={mean(g[k]):.3f}")
    print(f"-- p(Stop|B_r) by atom count N --")
    g = defaultdict(list)
    for c in chains:
        g[bucket(c["n_atoms"], N_EDGES)].append(c["steps"][0]["p_stop"])
    for k in [e[2] for e in N_EDGES]:
        if g.get(k):
            print(f"  N {k:<6} n={len(g[k]):<6} mean p(Stop|B_r)={mean(g[k]):.3f}")

    # --- F. p(Stop) when offered vs radical-centre count and vs position k
    print(f"\n-- p(Stop) when offered, by odd-diagonal atoms at that state --")
    g = defaultdict(list)
    for c in chains:
        for s in c["steps"]:
            if s["stop_offered"]:
                g[min(s["n_odd_diag"], 4)].append(s["p_stop"])
    for k in sorted(g):
        print(f"  odd={k}{'+' if k==4 else ' '} n={len(g[k]):<7} mean p(Stop)={mean(g[k]):.3f}")
    print(f"-- p(Stop) when offered, by position k --")
    g = defaultdict(list)
    for c in chains:
        for k, s in enumerate(c["steps"]):
            if s["stop_offered"]:
                g[min(k, 6)].append(s["p_stop"])
    for k in sorted(g):
        print(f"  k={k}{'+' if k==6 else ' '} n={len(g[k]):<7} mean p(Stop)={mean(g[k]):.3f}")

    # --- G. radical count dynamics
    print(f"\n-- odd-diagonal atoms: reactant -> final state --")
    for label, group in (("stuck", stuck), ("stopped", stopped)):
        d = Counter(min(c["final_n_odd_diag"], 5) for c in group)
        print(f"  {label:<8} final odd count: " + ", ".join(f"{k}:{v}" for k, v in sorted(d.items())))
    # --- H. move composition
    print(f"\n-- move kinds (all positions) and hydrogen involvement --")
    for label, group in (("stuck", stuck), ("stopped", stopped)):
        kinds = Counter(); h_touch = 0; tot = 0
        for c in group:
            for s in c["steps"]:
                if s["move"] == "STOP":
                    continue
                kinds[s["move"]] += 1; tot += 1
                h_touch += (s["elem_i"] == "H" or s["elem_j"] == "H")
        comp = ", ".join(f"{k}:{pct(v, tot):.1f}%" for k, v in kinds.most_common())
        print(f"  {label:<8} {comp}; moves touching an H atom: {pct(h_touch, tot):.1f}%")
    print(f"-- first move kind by outcome --")
    for label, group in (("stuck", stuck), ("stopped", [c for c in stopped if c['n_moves'] > 0])):
        kinds = Counter(c["steps"][0]["move"] for c in group)
        tot = sum(kinds.values())
        print(f"  {label:<8} " + ", ".join(f"{k}:{pct(v, tot):.1f}%" for k, v in kinds.most_common()))
    # first-move element pairs, stuck vs stopped
    print(f"-- first move element pair (top 8) --")
    for label, group in (("stuck", stuck), ("stopped", [c for c in stopped if c['n_moves'] > 0])):
        pairs = Counter(f"{c['steps'][0]['move'][:4]}({c['steps'][0]['elem_i']},{c['steps'][0]['elem_j']})" for c in group)
        tot = sum(pairs.values())
        print(f"  {label:<8} " + ", ".join(f"{k}:{pct(v, tot):.0f}%" for k, v in pairs.most_common(8)))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/instrumented_rmechdb.jsonl")
