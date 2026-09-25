#!/usr/bin/env python
"""Census of FlowER's training corpus for the quantities the paper's radical
appendix asserts about the *test* split (main.tex, "Single-electron moves"):
which elements ever carry an odd diagonal, which element pairs ever undergo a
single-electron move, and how often a Stop target sits on a state with an
unpaired electron on C/N/O/H. Run on the machine that holds train.txt::

    python corpus_census.py --txt data/flower_new_dataset/train.txt --sample 200000

Uses only `chem.py` from the ArrowFlowMatching checkout it is run inside.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, ".")
import chem  # noqa: E402

ORGANIC = {"C", "N", "O", "H", "S", "F", "Cl", "Br", "I"}


def be(smiles):
    mol = chem.mol_from_mapped_smiles(smiles)
    atom_index, mat = chem.atom_types_and_be(mol)
    symbols = [chem.ELEM_LIST[k] for k in atom_index]
    return symbols, mat


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--txt", required=True)
    ap.add_argument("--sample", type=int, default=200000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="corpus_census.json")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    lines = []
    with open(args.txt) as fh:
        for k, line in enumerate(fh):
            if ">>" not in line:
                continue
            if len(lines) < args.sample:
                lines.append(line)
            else:  # reservoir sampling
                j = rng.randrange(k + 1)
                if j < args.sample:
                    lines[j] = line

    odd_react = Counter()      # element -> #reactant atoms with odd diagonal
    odd_prod = Counter()       # element -> #product atoms with odd diagonal
    atoms_by_elem = Counter()  # element -> #reactant atoms (denominator)
    odd_delta_pairs = Counter()  # frozenset of elements whose diagonal changes by odd -> #steps
    n_steps = n_identity = n_odd_steps = 0
    prod_has_organic_radical = 0
    react_has_organic_radical = 0
    identity_with_organic_radical = 0
    n_atoms_hist = Counter()
    failed = 0
    for line in lines:
        try:
            # data.py::_parse_line -- `reactant>>product|field|field...`
            r, p = line.strip().split("|")[0].split(">>")
            sr, br = be(r)
            sp, bp = be(p)
        except Exception:
            failed += 1
            continue
        n_steps += 1
        n_atoms_hist[len(sr) // 10 * 10] += 1
        dr = np.diag(br).astype(int); dp = np.diag(bp).astype(int)
        for s in sr:
            atoms_by_elem[s] += 1
        for s, d in zip(sr, dr):
            if d % 2:
                odd_react[s] += 1
        for s, d in zip(sp, dp):
            if d % 2:
                odd_prod[s] += 1
        r_org = any(d % 2 and s in ORGANIC for s, d in zip(sr, dr))
        p_org = any(d % 2 and s in ORGANIC for s, d in zip(sp, dp))
        react_has_organic_radical += r_org
        prod_has_organic_radical += p_org
        identity = np.array_equal(br, bp)
        n_identity += identity
        identity_with_organic_radical += identity and p_org
        delta = dp - dr
        odd_atoms = [sr[k] for k in np.nonzero(delta % 2)[0]]
        if odd_atoms:
            n_odd_steps += 1
            odd_delta_pairs[" ".join(sorted(odd_atoms))] += 1

    def frac(c):
        return {k: round(v / n_steps, 5) for k, v in c.most_common(30)}

    result = {
        "n_steps": n_steps, "failed": failed,
        "identity_frac": round(n_identity / n_steps, 4),
        "odd_parity_step_frac": round(n_odd_steps / n_steps, 5),
        "odd_delta_element_sets_top30": dict(odd_delta_pairs.most_common(30)),
        "reactant_odd_diag_atoms_by_element": dict(odd_react.most_common(30)),
        "product_odd_diag_atoms_by_element": dict(odd_prod.most_common(30)),
        "atoms_by_element_top20": dict(atoms_by_elem.most_common(20)),
        "steps_with_organic_radical_in_reactant_frac": round(react_has_organic_radical / n_steps, 5),
        "steps_with_organic_radical_in_product_frac": round(prod_has_organic_radical / n_steps, 5),
        "identity_steps_with_organic_radical": identity_with_organic_radical,
        "n_atoms_hist_by_decade": dict(sorted(n_atoms_hist.items())),
    }
    json.dump(result, open(args.out, "w"), indent=1)
    print(json.dumps(result, indent=1))


if __name__ == "__main__":
    main()
