#!/usr/bin/env python
"""Internal stability of AFM's self-generated intermediates, in distribution.

The RMechDB stability runs measured a model that was out of distribution
(problem02-termination.md); the honest number for "are the states the chain
visits readable, stable chemistry" is on FlowER's own test reactants, where
the released checkpoint terminates normally. This replays the per-step move
log of `instrumented_rollout.py --flower_txt` (no model needed), reconstructs
every intermediate and every emitted final state with the repo's own
`chem.product_smiles_from_be`, and applies the same embed / force-field proxy
as the earlier runs (`intermediate_stability.stability_metrics`).

Three facts are reported per position, kept apart on purpose: whether the
state is in the Sector (`Stop` was offered -- the paper's own notion of "a
molecule"), whether it reconstructs, and whether it embeds / converges.
The paper says intermediates need *not* be in the Sector (Limitation iii);
how often they are anyway is the question.

    .venv/bin/python flower_intermediate_stability.py --limit 1000
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

import torch

from fully_explicit_stability import build_batch
from intermediate_stability import stability_metrics
from score_reactions import AFM_REPO, HERE

sys.path.insert(0, str(AFM_REPO))
import chem  # noqa: E402
from models.afm import scatter_moves  # noqa: E402

KIND_INDEX = {"LONE_TO_BOND": 0, "BOND_TO_LONE": 1, "HOMOLYSIS": 2, "COLLIGATION": 3}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", default=str(HERE / "results" / "instrumented_flower.jsonl"))
    ap.add_argument("--limit", type=int, default=None, help="reactants to process")
    ap.add_argument("--out", default=str(HERE / "results" / "flower_intermediate_stability.jsonl"))
    args = ap.parse_args()

    c = Counter()
    with open(args.out, "w") as out_fh:
        for n_rec, line in enumerate(open(args.log)):
            if args.limit and n_rec >= args.limit:
                break
            rec = json.loads(line)
            batch, _ = build_batch(rec["reactant"])
            mol = batch["reactant_mols"][0]
            size = int(batch["lengths"][0])
            src = batch["src"].long()
            per_chain = []
            for ch in rec["chains"]:
                state = src.clone()
                moves = [s for s in ch["steps"] if s["move"] != "STOP"]
                if not moves:
                    c["chains_0_moves"] += 1
                    continue
                c["chains"] += 1
                steps_out = []
                for pos, s in enumerate(moves):
                    scatter_moves(state, torch.tensor([KIND_INDEX[s["move"]]]), torch.tensor([s["i"]]),
                                  torch.tensor([s["j"]]), torch.ones(1, dtype=torch.bool))
                    is_final = pos == len(moves) - 1 and ch["stopped"]
                    which = "final" if is_final else "mid"
                    # Sector membership of the state *after* this move is the
                    # stop_offered flag logged at the next decision.
                    nxt = ch["steps"][pos + 1] if pos + 1 < len(ch["steps"]) else None
                    in_sector = bool(nxt["stop_offered"]) if nxt else None
                    smiles = chem.product_smiles_from_be(mol, state[0, :size, :size].numpy())
                    m = {"position": pos, "kind": which, "in_sector": in_sector, "reconstructs": bool(smiles)}
                    c[f"{which}_n"] += 1
                    c[f"{which}_in_sector"] += bool(in_sector)
                    if smiles:
                        c[f"{which}_reconstructs"] += 1
                        m.update(stability_metrics(smiles), smiles=smiles)
                        c[f"{which}_embeds"] += bool(m.get("embeds"))
                        c[f"{which}_converged"] += bool(m.get("converged"))
                    steps_out.append(m)
                per_chain.append({"stopped": ch["stopped"], "steps": steps_out})
            out_fh.write(json.dumps({"index": rec["index"], "n_atoms": rec["n_atoms"], "chains": per_chain}) + "\n")
            if (n_rec + 1) % 100 == 0:
                print(f"{n_rec + 1} reactants processed", flush=True)

    def pct(k, n):
        return 100 * k / n if n else float("nan")

    print(f"\nchains with >=1 move: {c['chains']}  (immediate Stop, not scored: {c['chains_0_moves']})")
    for which in ("mid", "final"):
        n = c[f"{which}_n"]
        print(f"{which:<6} n={n:<6} in Sector={pct(c[f'{which}_in_sector'], n):5.1f}%  reconstructs={pct(c[f'{which}_reconstructs'], n):5.1f}%  "
              f"embeds={pct(c[f'{which}_embeds'], n):5.1f}%  FF-converges={pct(c[f'{which}_converged'], n):5.1f}%")
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
