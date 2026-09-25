#!/usr/bin/env python
"""Where does the chemist's own move sequence sit in AFM's self-generated score histogram?

Question (see README.md for the full brief): when AFM samples its own candidate
mechanisms for a reaction, is the chemist's mechanism a typical, high-probability
draw -- even when it is not the model's single top pick?

Every piece of chemistry/model logic here is reused, not reimplemented:

* ``chem.mol_from_mapped_smiles`` / ``chem.atom_types_and_be`` -- the exact
  functions the training pipeline uses to turn a mapped SMILES into the model's
  ``(atom_ids, source)`` tensors (ArrowFlowMatching/chem.py).
* ``models.afm.ArrowFlowMatching.mapped_candidates`` -- unmodified; gives the
  self-sampled score histogram for free.
* ``teacher_forced_score`` below is a straight adaptation of
  ``ArrowFlowMatching.training_loss`` (same ``_score`` / ``scatter_moves`` calls),
  just summed over the whole given path instead of one randomly sampled position.
* The move-name -> (kind, i, j) table is read off ``analysis/decompose_steps.py``'s
  MOVES_PLUS/MOVES_MINUS against ``models/afm.py``'s DII/DJJ/DIJ tables, not
  guessed.
* The human move sequences themselves come from ``analysis/rmechdb_arrows.py``'s
  ``--dump_targets`` output (an additive change to that script, not a rewrite):
  only the reactions where the chemist's arrows exact-match one of the alphabet's
  own admissible decompositions (see README.md's scoping note).

Run (from this directory)::

    .venv/bin/python score_reactions.py --limit 20 --num_samples 200
"""
from __future__ import annotations

import argparse
import json
import sys
import types
from pathlib import Path

import torch
from rdkit import Chem, RDLogger

HERE = Path(__file__).resolve().parent
AFM_REPO = HERE.parent.parent / "ArrowFlowMatching"
ANALYSIS = HERE.parent.parent / "analysis"
sys.path.insert(0, str(AFM_REPO))
sys.path.insert(0, str(ANALYSIS))

RDLogger.DisableLog("rdApp.*")

import chem  # noqa: E402
from models.afm import ArrowFlowMatching, NUM_MOVES, scatter_moves  # noqa: E402
from rmechdb_arrows import reduced_matrix  # noqa: E402  (for the featurization cross-check)

_PS = Chem.SmilesParserParams()
_PS.removeHs = False
_PS.sanitize = True

#: decompose_steps.py's move names -> models/afm.py's (kind, swap_i_j) convention.
#: Cross-checked, not assumed: decompose_steps.MOVES_PLUS/MOVES_MINUS list
#: (dii, djj, dij) triples of (-2,0,+1) / (0,-2,+1) / (0,+2,-1) / (+2,0,-1) /
#: (+1,+1,-1) / (-1,-1,+1) for LONE_TO_BOND_i/_j, BOND_TO_LONE_j/_i, HOMOLYSIS,
#: COLLIGATION; afm.py's DII=(-2,0,1,-1) DJJ=(0,2,1,-1) DIJ=(1,-1,-1,1) are the
#: same four triples in a fixed order, kind = position in those tuples. Where the
#: two tables disagree only in which atom is (i, j), the atoms are swapped instead.
NAME_TO_KIND = {
    "LONE_TO_BOND_i": (0, False),
    "LONE_TO_BOND_j": (0, True),
    "BOND_TO_LONE_j": (1, False),
    "BOND_TO_LONE_i": (1, True),
    "HOMOLYSIS": (2, False),
    "COLLIGATION": (3, False),
}


def load_model(ckpt_path: Path, emb_dim: int, enc_filter_size: int, model_name: str = "afm"):
    """Instantiate a model exactly as configured and load its checkpoint weights.

    Hydra composes ``configs/model/<model_name>.yaml`` + ``configs/model/common.yaml``,
    the same files ``train.py``/``eval.py`` use, with the ``nano``-width overrides
    ``README.md`` documents (``emb_dim=128 enc_filter_size=512``) -- read directly
    off each checkpoint's own saved hyperparameters, not guessed. AFM additionally
    needs ``decode=sample`` (its beam/sample choice); the other models here have
    no such hyperparameter.

    Some checkpoints' ``hyper_parameters`` were pickled against a sibling repo
    (Milan's own ``MechReact``, ``models.flower_cons``) this checkout does not
    have; a stub module lets ``torch.load`` skip that unused metadata rather than
    failing to import a module we don't need.
    """
    import hydra

    stub = types.ModuleType("models.flower_cons")

    def _stub_getattr(name):
        if name.startswith("__") and name.endswith("__"):
            raise AttributeError(name)
        return type(name, (), {})

    stub.__getattr__ = _stub_getattr
    sys.modules.setdefault("models.flower_cons", stub)

    overrides = [f"model={model_name}", f"model.emb_dim={emb_dim}", f"model.enc_filter_size={enc_filter_size}"]
    if model_name == "afm":
        overrides.append("model.decode=sample")
    with hydra.initialize_config_dir(config_dir=str(AFM_REPO / "configs"), version_base=None):
        cfg = hydra.compose(config_name="default_eval", overrides=overrides)
    model = hydra.utils.instantiate(cfg.model)
    ckpt = torch.load(str(ckpt_path), map_location="cpu", weights_only=False)
    missing, unexpected = model.load_state_dict(ckpt["state_dict"], strict=True)
    assert not missing and not unexpected, (missing, unexpected)
    model.eval()
    return model


def complete_atom_map(reactant_smiles: str):
    """Give every atom a contiguous 1-based map number; ``chem.py`` requires it.

    RMechDB maps only the reacting atoms. Renumbering every atom by its RDKit
    parse index (any fixed 1..N labelling works -- ``_traverse_mapped`` places
    each atom at ``map_number - 1`` regardless of what that number is) keeps every
    originally-mapped atom's number recoverable via the returned ``old_to_new``.
    """
    mol = Chem.MolFromSmiles(reactant_smiles, _PS)
    if mol is None:
        return None, None
    old_to_new = {}
    for atom in mol.GetAtoms():
        old = atom.GetAtomMapNum()
        new = atom.GetIdx() + 1
        if old:
            old_to_new[old] = new
        atom.SetAtomMapNum(new)
    return Chem.MolToSmiles(mol, canonical=False), old_to_new


def build_batch(mapped_smiles: str):
    mol = chem.mol_from_mapped_smiles(mapped_smiles)
    atom_index, be = chem.atom_types_and_be(mol)
    n = len(atom_index)
    batch = {
        "src": torch.as_tensor(be, dtype=torch.float32).unsqueeze(0),
        "lengths": torch.tensor([n]),
        "atom_ids": torch.as_tensor(atom_index, dtype=torch.long).unsqueeze(0),
        "reactant_mols": [mol],
    }
    return batch, be


def cross_check_featurization(be, old_to_new, reactant_smiles: str) -> bool:
    """The model's own BE matrix, restricted to reacting atoms, must match
    ``rmechdb_arrows.py``'s independently-built reduced matrix -- built from the
    same SMILES by a different route (aromatic handling in particular differs
    between the two). A mismatch means the move sequence would be teacher-forced
    against a state it does not actually start from, so such reactions are
    excluded rather than silently scored.
    """
    r = reduced_matrix(reactant_smiles)
    if r is None:
        return False
    diag, bonds, elements, _ = r
    for n, sym in elements.items():
        new = old_to_new[n] - 1
        if chem.ELEM_LIST[chem.ATOM_TO_IDX[sym]] != sym:
            return False
        if be[new, new] != diag[n]:
            return False
    for (i, j), order in bonds.items():
        a, b = old_to_new[i] - 1, old_to_new[j] - 1
        if be[a, b] != order:
            return False
    return True


#: kind indices that are symmetric under swapping (i, j) -- read off afm.py's
#: SYMMETRIC = (False, False, True, True) for (LONE_TO_BOND, BOND_TO_LONE,
#: HOMOLYSIS, COLLIGATION).
_SYMMETRIC_KINDS = {2, 3}


def to_model_moves(moves, old_to_new) -> torch.Tensor:
    """``[[name, i, j], ...]`` (RMechDB map-number space) -> ``(1, T, 3)`` (kind, i, j),
    0-based, matching ``chem.atom_types_and_be``'s ``map_number - 1`` ordering.

    ``move_mask`` offers a symmetric kind (HOMOLYSIS, COLLIGATION) on the upper
    triangle only -- "the same physical move is not two classes of the same
    softmax" -- so those two kinds additionally need ``i < j``, independent of
    whichever order ``decompose_steps.py``'s move tuple happened to carry.
    """
    out = []
    for name, i, j in moves:
        kind, swap = NAME_TO_KIND[name]
        a, b = old_to_new[i], old_to_new[j]
        if swap:
            a, b = b, a
        a, b = a - 1, b - 1
        if kind in _SYMMETRIC_KINDS and a > b:
            a, b = b, a
        out.append((kind, a, b))
    return torch.tensor(out, dtype=torch.long).unsqueeze(0)


@torch.no_grad()
def teacher_forced_score(model, atom_ids, lengths, source, moves: torch.Tensor):
    """Sum of the log-probability AFM assigns to each of the chemist's own moves,
    in order, plus the final stop decision.

    The teacher-forced twin of ``ArrowFlowMatching.training_loss``: identical
    per-step ``_score`` / ``scatter_moves`` calls, but walking the whole given
    path rather than sampling one random position along it -- so ``Score.logp``
    (the quantity ``mapped_candidates`` reports for a self-generated trajectory)
    and this function's return value are the same statistic, one teacher-forced
    and one sampled. The input must be in the released data's convention, every
    hydrogen an explicit mapped atom (`problem01-validity.md`).
    """
    state = source.clone()
    b, n, _ = source.shape
    step = torch.zeros(b)
    total = 0.0
    for t in range(moves.shape[1]):
        kind, i, j = moves[0, t]
        log_probs = model._score(atom_ids, lengths, state, source, step)
        move_index = (kind * n + i) * n + j
        total += log_probs[0, move_index].item()
        scatter_moves(state, kind.view(1), i.view(1), j.view(1), torch.ones(1, dtype=torch.bool))
        step = step + 1
    log_probs = model._score(atom_ids, lengths, state, source, step)
    stop_index = NUM_MOVES * n * n
    total += log_probs[0, stop_index].item()
    return total, moves.shape[1] + 1


@torch.no_grad()
def sampled_scores(model, batch, num_samples: int) -> list[float]:
    """Self-generated trajectory log-probabilities for the same reactant, via the
    model's own unmodified ``mapped_candidates`` (sampling decode, set in
    ``load_model``). One call per reaction keeps memory bounded; ``num_samples``
    trades histogram resolution for runtime."""
    candidates = model.mapped_candidates(batch, num_samples)[0]
    return [score.logp for _, score in candidates]


@torch.no_grad()
def sampled_move_kind_counts(model, atom_ids, lengths, source, width: int) -> torch.Tensor:
    """Per self-generated trajectory, how many times each of the 4 move kinds fired.

    Same roll-out ``ArrowFlowMatching._rollout`` runs inside ``mapped_candidates``
    (repeat_interleave, per-step ``_score``, ``scatter_moves``, the
    ``choice == NUM_MOVES * n * n`` stop test) -- it just also tallies ``kind``
    per step instead of only keeping the final state and score. Restricted to
    sample decode (what ``load_model`` always sets here): a sampled hypothesis
    never competes for another's slot, so unlike beam search there is no
    ``parent`` reindexing to carry through.

    Returns
    -------
    torch.Tensor
        ``(width, NUM_MOVES)`` counts, one row per sampled trajectory.
    """
    assert model.hparams.decode == "sample", "beam decode reorders slots; not handled here"
    rows = width
    atom_ids = atom_ids.repeat_interleave(width, dim=0)
    lengths = lengths.repeat_interleave(width, dim=0)
    source = source.repeat_interleave(width, dim=0)
    n = source.shape[-1]

    state = source.clone()
    score = torch.zeros(rows)
    done = torch.zeros(rows, dtype=torch.bool)
    step = torch.zeros(rows)
    counts = torch.zeros(rows, NUM_MOVES)
    for _ in range(model.max_moves):
        log_probs = model._score(atom_ids, lengths, state, source, step)
        from models.afm import _sample_step  # local: avoid importing at module scope
        choice, score, _ = _sample_step(log_probs, score, done, width)
        kind, rest = choice // (n * n), choice % (n * n)
        live = ~done & (choice != NUM_MOVES * n * n)
        counts[torch.arange(rows), kind.clamp(0, NUM_MOVES - 1)] += live.float()
        scatter_moves(state, kind, rest // n, rest % n, live)
        step = step + live.float()
        done = ~live
        if bool(done.all()):
            break
    return counts


@torch.no_grad()
def sampled_intermediates(model, atom_ids, lengths, source, reactant_mol, width: int) -> list[list[str]]:
    """``width`` self-generated trajectories -> reconstructed SMILES after every
    move actually taken (last entry per chain = that chain's final answer).

    Same restricted copy of ``_rollout`` as ``sampled_move_kind_counts`` (sample
    decode only), except it reconstructs a SMILES at every live step
    (``chem.product_smiles_from_be``) instead of tallying move kinds. Every
    state along the way is a representable bond-electron matrix by
    construction (the guarantee move masking exists to provide), independent
    of whether that state happens to be one the chain is *also* allowed to
    stop from -- so unlike ``ArrowFlowMatching._rollout`` itself, this needs no
    ``settled``/fallback bookkeeping to get a valid reconstruction at each step.
    """
    assert model.hparams.decode == "sample", "beam decode reorders slots; not handled here"
    from models.afm import _sample_step

    rows = width
    atom_ids = atom_ids.repeat_interleave(width, dim=0)
    lengths = lengths.repeat_interleave(width, dim=0)
    source = source.repeat_interleave(width, dim=0)
    n = source.shape[-1]

    state = source.clone()
    score = torch.zeros(rows)
    done = torch.zeros(rows, dtype=torch.bool)
    step = torch.zeros(rows)
    chains: list[list[str]] = [[] for _ in range(rows)]
    for _ in range(model.max_moves):
        log_probs = model._score(atom_ids, lengths, state, source, step)
        choice, score, _ = _sample_step(log_probs, score, done, width)
        kind, rest = choice // (n * n), choice % (n * n)
        live = ~done & (choice != NUM_MOVES * n * n)
        scatter_moves(state, kind, rest // n, rest % n, live)
        step = step + live.float()
        done = ~live
        for row in range(rows):
            if live[row]:
                size = int(lengths[row].item())
                chains[row].append(chem.product_smiles_from_be(reactant_mol, state[row, :size, :size].numpy()))
        if bool(done.all()):
            break
    return chains


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--targets", default=str(HERE / "targets.json"))
    ap.add_argument("--ckpt", default=str(AFM_REPO / "outputs/runs/afm_nano/checkpoints/best.ckpt"))
    ap.add_argument("--emb_dim", type=int, default=128)
    ap.add_argument("--enc_filter_size", type=int, default=512)
    ap.add_argument("--num_samples", type=int, default=200)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out", default=str(HERE / "results" / "scores.jsonl"))
    args = ap.parse_args()

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    targets = json.load(open(args.targets))
    if args.limit:
        targets = targets[: args.limit]

    model = load_model(Path(args.ckpt), args.emb_dim, args.enc_filter_size)
    # Imported here: fully_explicit_stability imports this module at load time.
    from fully_explicit_stability import fully_explicit_atom_map

    kept, excluded = 0, 0
    with open(args.out, "w") as out_fh:
        for idx, rec in enumerate(targets):
            # The released data's convention, every hydrogen its own mapped atom
            # (problem01-validity.md). Heavy-atom map numbers coincide with
            # complete_atom_map's, so its old_to_new translates the chemist's moves.
            mapped_smiles = fully_explicit_atom_map(rec["reactant"])
            _, old_to_new = complete_atom_map(rec["reactant"])
            if mapped_smiles is None:
                excluded += 1
                continue
            batch, be = build_batch(mapped_smiles)
            if not cross_check_featurization(be, old_to_new, rec["reactant"]):
                excluded += 1
                continue
            try:
                moves = to_model_moves(rec["moves"], old_to_new)
                # `_source` is what every model entry point (mapped_candidates,
                # training_loss) calls before touching `batch["src"]` -- it casts
                # the padded float matrix to the long tensor the embeddings need.
                source = model._source(batch)
                human_logp, human_len = teacher_forced_score(
                    model, batch["atom_ids"], batch["lengths"], source, moves
                )
                sampled = sampled_scores(model, batch, args.num_samples)
            except Exception as exc:  # noqa: BLE001 -- record and move on, one reaction must not sink the run
                excluded += 1
                print(f"[{idx}] failed: {exc}", file=sys.stderr)
                continue
            kept += 1
            out_fh.write(json.dumps({
                "index": idx,
                "reactant": rec["reactant"],
                "human_logp": human_logp,
                "human_length": human_len,
                "sampled_logps": sampled,
                "meta": rec["meta"],
            }) + "\n")
            out_fh.flush()
            if (idx + 1) % 25 == 0:
                print(f"{idx + 1}/{len(targets)} processed ({kept} kept, {excluded} excluded)")

    print(f"Done. {kept} kept, {excluded} excluded. Wrote {args.out}")


if __name__ == "__main__":
    main()
