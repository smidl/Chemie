#!/usr/bin/env python
"""Does the model use the same mix of move types as the chemist does?

Cheap interpretability check, complementary to the rank-based one in
``score_reactions.py``/``analyze.py``: not "does the model prefer the human's
specific mechanism" but "does it reach for the same *kind* of chemistry" --
e.g. does it default to homolysis/colligation (radical-flavoured moves) at
roughly the rate a radical-chemistry corpus like RMechDB actually does, or does
it lean on lone-pair moves regardless of context?

Two tallies, same 4 buckets (LONE_TO_BOND, BOND_TO_LONE, HOMOLYSIS, COLLIGATION):

* chemist side -- the exact-match target move sequences (``targets.json``),
  translated through the same ``NAME_TO_KIND`` table ``score_reactions.py``
  already validated (fixed the symmetric-move ordering bug there).
* model side -- ``sampled_move_kind_counts``, tallied over self-generated
  samples for the same reactants (new, but a direct instrument of
  ``_rollout``'s own loop, not new chemistry).

Run (from this directory)::

    .venv/bin/python alphabet_composition.py --num_samples 50
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import torch

from score_reactions import (
    AFM_REPO, HERE, NAME_TO_KIND, build_batch, complete_atom_map,
    load_model, sampled_move_kind_counts, to_model_moves,
)

KIND_NAMES = ["LONE_TO_BOND", "BOND_TO_LONE", "HOMOLYSIS", "COLLIGATION"]


def chemist_counts(moves: list[list]) -> Counter:
    c = Counter()
    for name, _, _ in moves:
        kind, _ = NAME_TO_KIND[name]
        c[kind] += 1
    return c


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", default=str(HERE / "targets.json"))
    ap.add_argument("--ckpt", default=str(AFM_REPO / "outputs/runs/afm_nano/checkpoints/best.ckpt"))
    ap.add_argument("--emb_dim", type=int, default=128)
    ap.add_argument("--enc_filter_size", type=int, default=512)
    ap.add_argument("--num_samples", type=int, default=50)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", default=str(HERE / "results" / "alphabet_composition.json"))
    args = ap.parse_args()

    targets = json.load(open(args.targets))
    if args.limit:
        targets = targets[: args.limit]

    model = load_model(Path(args.ckpt), args.emb_dim, args.enc_filter_size)

    human_totals = Counter()
    model_totals = torch.zeros(len(KIND_NAMES))
    n_ok = 0
    for idx, rec in enumerate(targets):
        mapped_smiles, old_to_new = complete_atom_map(rec["reactant"])
        if mapped_smiles is None:
            continue
        batch, _ = build_batch(mapped_smiles)
        source = model._source(batch)
        try:
            counts = sampled_move_kind_counts(
                model, batch["atom_ids"], batch["lengths"], source, batch["n_h"], args.num_samples
            )
        except Exception as exc:  # noqa: BLE001
            print(f"[{idx}] failed: {exc}")
            continue
        model_totals += counts.sum(dim=0)
        human_totals += chemist_counts(rec["moves"])
        n_ok += 1
        if (idx + 1) % 200 == 0:
            print(f"{idx + 1}/{len(targets)} processed")

    human_total = sum(human_totals.values())
    model_total = model_totals.sum().item()
    print(f"\n{n_ok} reactions processed\n")
    print(f"{'move kind':<14}{'chemist %':>12}{'model %':>12}")
    out_rows = []
    for k, name in enumerate(KIND_NAMES):
        h_pct = 100 * human_totals.get(k, 0) / human_total if human_total else 0.0
        m_pct = 100 * model_totals[k].item() / model_total if model_total else 0.0
        print(f"{name:<14}{h_pct:>11.1f}%{m_pct:>11.1f}%")
        out_rows.append({
            "kind": name,
            "chemist_count": human_totals.get(k, 0), "chemist_pct": round(h_pct, 2),
            "model_count": model_totals[k].item(), "model_pct": round(m_pct, 2),
        })

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as fh:
        json.dump({
            "n_reactions": n_ok, "num_samples": args.num_samples,
            "chemist_total_moves": human_total, "model_total_moves": model_total,
            "by_kind": out_rows,
        }, fh, indent=2)
    print(f"\nWrote {args.out}")


if __name__ == "__main__":
    main()
