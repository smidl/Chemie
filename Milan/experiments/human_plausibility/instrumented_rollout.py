#!/usr/bin/env python
"""Per-step log of AFM's own roll-out: what the chain does, and what it was offered.

The stability runs recorded only the reconstructed SMILES at each position.
Every hypothesis about *why* 35.7% of chains never choose Stop within the
S=12 budget (problem02-termination.md) needs quantities those files do not
hold: at each position, was the Stop class offered at all (x in Sector, the
gate of eq. (head) in the paper), what probability did the model put on it,
how many move classes competed with it, which move was taken and by which
atoms, and whether that move undid the previous one (Remark "closed under
inversion"). This script re-runs the same sample-decode roll-out as
`fully_explicit_stability.py` -- unmodified `models/afm.py`, same `afm_nano`
checkpoint -- and writes one JSON record per chain with the per-step log.

Input convention is selectable so the same log can be produced for RMechDB
reactants (`--targets multistep.json`, fully-explicit-H preprocessing) and for
FlowER's own test reactants (`--flower_txt <file>`, already fully mapped),
giving the in-distribution control the paper does not report.

Run (from this directory)::

    .venv/bin/python instrumented_rollout.py --num_chains 3
    .venv/bin/python instrumented_rollout.py --flower_txt data/flower_test_sample.txt --num_chains 3
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import torch

from fully_explicit_stability import build_batch, fully_explicit_atom_map
from score_reactions import AFM_REPO, HERE, load_model

sys.path.insert(0, str(AFM_REPO))

import chem  # noqa: E402
from models.afm import NUM_MOVES, _sample_step, scatter_moves  # noqa: E402

#: kind indices, read off models/afm.py: LONE_TO_BOND, BOND_TO_LONE, HOMOLYSIS, COLLIGATION.
KIND_NAMES = ["LONE_TO_BOND", "BOND_TO_LONE", "HOMOLYSIS", "COLLIGATION"]


def is_inverse(prev, cur) -> bool:
    """Is `cur` the alphabet's inverse of `prev` (Remark: closed under inversion)?

    lone->bond(i,j) is undone by bond->lone(j,i) and vice versa; homolysis(i,j)
    and colligation(i,j) undo each other (both symmetric, offered with i<j).
    """
    if prev is None:
        return False
    pk, pi, pj = prev
    ck, ci, cj = cur
    if pk == 0 and ck == 1:
        return (ci, cj) == (pj, pi)
    if pk == 1 and ck == 0:
        return (ci, cj) == (pj, pi)
    if {pk, ck} == {2, 3}:
        return (ci, cj) == (pi, pj)
    return False


@torch.no_grad()
def instrumented_chains(model, atom_ids, lengths, source, width: int, elem_symbols: list[str]):
    assert model.hparams.decode == "sample"
    rows = width
    atom_ids = atom_ids.repeat_interleave(width, dim=0)
    lengths = lengths.repeat_interleave(width, dim=0)
    source = source.repeat_interleave(width, dim=0)
    n = source.shape[-1]
    size = int(lengths[0].item())

    state = source.clone()
    score = torch.zeros(rows)
    done = torch.zeros(rows, dtype=torch.bool)
    step = torch.zeros(rows)
    logs = [[] for _ in range(rows)]
    prev_move = [None] * rows
    stopped = [False] * rows
    for _ in range(model.max_moves):
        log_probs = model._score(atom_ids, lengths, state, source, step)
        stop_lp = log_probs[:, -1]
        stop_offered = torch.isfinite(stop_lp)
        n_admissible = torch.isfinite(log_probs[:, :-1]).sum(1)
        diag = torch.diagonal(state, dim1=-2, dim2=-1)[:, :size]
        n_odd = (diag % 2 == 1).sum(1)
        choice, score, _ = _sample_step(log_probs, score, done, width)
        kind, rest = choice // (n * n), choice % (n * n)
        i_idx, j_idx = rest // n, rest % n
        live = ~done & (choice != NUM_MOVES * n * n)
        for row in range(rows):
            if done[row]:
                continue
            entry = {
                "stop_offered": bool(stop_offered[row]),
                "p_stop": float(stop_lp[row].exp()) if stop_offered[row] else 0.0,
                "n_admissible": int(n_admissible[row]),
                "n_odd_diag": int(n_odd[row]),
            }
            if live[row]:
                mv = (int(kind[row]), int(i_idx[row]), int(j_idx[row]))
                entry.update(
                    move=KIND_NAMES[mv[0]], i=mv[1], j=mv[2],
                    elem_i=elem_symbols[mv[1]], elem_j=elem_symbols[mv[2]],
                    inverse_of_previous=is_inverse(prev_move[row], mv),
                )
                prev_move[row] = mv
            else:
                entry.update(move="STOP")
                stopped[row] = True
            logs[row].append(entry)
        scatter_moves(state, kind, i_idx, j_idx, live)
        step = step + live.float()
        done = ~live
        if bool(done.all()):
            break
    # after the budget, record Sector membership and n_odd of the final state
    log_probs = model._score(atom_ids, lengths, state, source, step)
    final_offered = torch.isfinite(log_probs[:, -1])
    diag = torch.diagonal(state, dim1=-2, dim2=-1)[:, :size]
    out = []
    for row in range(rows):
        n_moves = sum(1 for e in logs[row] if e["move"] != "STOP")
        out.append({
            "stopped": stopped[row],
            "n_moves": n_moves,
            "final_in_sector": bool(final_offered[row]),
            "final_n_odd_diag": int((diag[row] % 2 == 1).sum()),
            "steps": logs[row],
        })
    return out


def flower_reactants(path: Path, limit: int | None):
    """FlowER's released txt: one `reactant>>product` mapped-SMILES pair per line."""
    out = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line or ">>" not in line:
                continue
            out.append(line.split(">>")[0].split()[0])
            if limit and len(out) >= limit:
                break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", default=str(HERE / "multistep.json"))
    ap.add_argument("--flower_txt", default=None,
                     help="If given, roll out FlowER's own (already fully mapped) reactants instead.")
    ap.add_argument("--ckpt", default=str(AFM_REPO / "outputs/runs/afm_nano/checkpoints/best.ckpt"))
    ap.add_argument("--emb_dim", type=int, default=128)
    ap.add_argument("--enc_filter_size", type=int, default=512)
    ap.add_argument("--num_chains", type=int, default=3)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.flower_txt:
        reactants = flower_reactants(Path(args.flower_txt), args.limit)
        metas = [None] * len(reactants)
        default_out = HERE / "results" / "instrumented_flower.jsonl"
        preprocess = lambda s: s  # noqa: E731 -- already every atom mapped, hydrogens included
    else:
        targets = json.load(open(args.targets))
        if args.limit:
            targets = targets[: args.limit]
        reactants = [t["reactant"] for t in targets]
        metas = [t.get("meta") for t in targets]
        default_out = HERE / "results" / "instrumented_rmechdb.jsonl"
        preprocess = fully_explicit_atom_map
    out_path = Path(args.out) if args.out else default_out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    model = load_model(Path(args.ckpt), args.emb_dim, args.enc_filter_size, model_name="afm")

    n_written = n_failed = 0
    with open(out_path, "w") as fh:
        for idx, (smiles, meta) in enumerate(zip(reactants, metas)):
            try:
                mapped = preprocess(smiles)
                if mapped is None:
                    n_failed += 1
                    continue
                batch, _ = build_batch(mapped)
                mol = batch["reactant_mols"][0]
                symbols = [None] * mol.GetNumAtoms()
                for atom in mol.GetAtoms():
                    symbols[atom.GetIntProp("molAtomMapNumber") - 1] = atom.GetSymbol()
                source = model._source(batch)
                chains = instrumented_chains(
                    model, batch["atom_ids"], batch["lengths"], source, args.num_chains, symbols
                )
            except Exception as exc:  # noqa: BLE001
                n_failed += 1
                print(f"[{idx}] failed: {exc}")
                continue
            n_atoms = int(batch["lengths"][0])
            reactant_odd = int((torch.diagonal(source[0])[:n_atoms] % 2 == 1).sum())
            fh.write(json.dumps({
                "index": idx, "reactant": smiles, "meta": meta, "n_atoms": n_atoms,
                "reactant_n_odd_diag": reactant_odd, "chains": chains,
            }) + "\n")
            n_written += 1
            if (idx + 1) % 200 == 0:
                print(f"{idx + 1}/{len(reactants)} processed", flush=True)
    print(f"Done. {n_written} reactants written, {n_failed} failed. Wrote {out_path}")


if __name__ == "__main__":
    main()
