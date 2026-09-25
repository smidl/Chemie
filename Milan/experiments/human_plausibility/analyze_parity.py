#!/usr/bin/env python
"""Radical bookkeeping along the instrumented chains, by replaying the logged
moves on the reactant's diagonal (no model needed).

A pair move changes a diagonal by 0 or 2 and a single-electron move by 1, so
the *parity* of each atom's lone-electron count flips only under HOMOLYSIS or
COLLIGATION, and the number of odd atoms changes by 0 or +-2. At every state
where Stop was offered, classify the odd atoms as

  fresh      odd now, even in B_r   (a radical the chain created)
  persistent odd now, odd  in B_r   (a radical carried over from the reactant)
  healed     even now, odd in B_r   (a reactant radical the chain paired up)

and read the model's p(Stop) against that signature. In FlowER's corpus the
only odd-parity chemistry is Pd-P homolysis/colligation (main.tex, "Single-
electron moves"): a Stop target there has either 0 fresh radicals or exactly
2 fresh ones created by one homolysis, never a single fresh organic radical
next to a healed one -- which is exactly the product signature of every
propagation step in RMechDB.

    .venv/bin/python analyze_parity.py results/instrumented_rmechdb.jsonl
"""
from __future__ import annotations

import json
import sys
from collections import defaultdict
from statistics import mean

import numpy as np

from fully_explicit_stability import build_batch, fully_explicit_atom_map

KIND_DIAG = {  # (delta x_ii, delta x_jj) per kind, read off models/afm.py DII/DJJ
    "LONE_TO_BOND": (-2, 0), "BOND_TO_LONE": (0, 2), "HOMOLYSIS": (1, 1), "COLLIGATION": (-1, -1),
}


def pct(k, n):
    return 100 * k / n if n else float("nan")


def main(path, flower=False):
    cells = defaultdict(list)          # (fresh, persistent) -> p_stop at offered states
    stopped_at = defaultdict(lambda: [0, 0])  # (fresh, persistent) -> [stopped here, offered here]
    final_sig = defaultdict(int)       # signature of the state a stopped chain emitted
    n_chains = 0
    for line in open(path):
        rec = json.loads(line)
        smiles = rec["reactant"] if flower else fully_explicit_atom_map(rec["reactant"])
        batch, _ = build_batch(smiles)
        diag0 = np.diag(batch["src"][0].numpy()).astype(int)
        odd0 = (diag0 % 2 == 1)
        for ch in rec["chains"]:
            n_chains += 1
            diag = diag0.copy()
            for k, s in enumerate(ch["steps"]):
                odd = (diag % 2 == 1)
                fresh = int((odd & ~odd0).sum())
                persist = int((odd & odd0).sum())
                sig = (fresh, persist)
                if s["stop_offered"]:
                    cells[sig].append(s["p_stop"])
                    stopped_at[sig][1] += 1
                    if s["move"] == "STOP":
                        stopped_at[sig][0] += 1
                        final_sig[sig] += 1
                if s["move"] == "STOP":
                    break
                di, dj = KIND_DIAG[s["move"]]
                diag[s["i"]] += di
                diag[s["j"]] += dj
    print(f"file: {path}  chains={n_chains}")
    print(f"\n{'(fresh, persistent) radicals':<30} {'states w/ Stop offered':>22} {'mean p(Stop)':>13} {'chose Stop here':>16}")
    for sig in sorted(cells, key=lambda s: (-len(cells[s]))):
        n = len(cells[sig])
        if n < 20:
            continue
        print(f"{str(sig):<30} {n:>22} {mean(cells[sig]):>13.3f} {pct(*stopped_at[sig]):>15.1f}%")
    print(f"\nsignature of the state stopped chains emitted (top 8):")
    tot = sum(final_sig.values())
    for sig, c in sorted(final_sig.items(), key=lambda x: -x[1])[:8]:
        print(f"  fresh={sig[0]} persistent={sig[1]}: {c} ({pct(c, tot):.1f}%)")


if __name__ == "__main__":
    p = sys.argv[1] if len(sys.argv) > 1 else "results/instrumented_rmechdb.jsonl"
    # --mapped: the log's reactant is already in FlowER convention (every atom
    # mapped); renumbering it would scramble the move indices.
    main(p, flower=("flower" in p) or ("--mapped" in sys.argv))
