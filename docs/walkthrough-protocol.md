# Freezing the walkthrough procedure, and a held-out set

**Date:** 2026-08-08 · **Supersedes the ad-hoc S1 development in** `walkthrough-s1-mapping.md`

## The objection, and how much of it holds

*"The computational machinery changes with every molecule. If these six train it, we need another
six to test."*

Correct, and it is ADR 0004's "never accept a training-objective result at pilot scale" applied to
ourselves. Set A has already been used for development three times over:

- the mapping method was chosen **after** MCS failed on these six;
- `SUBMERGED_BARRIER` was added to the guard **because** #95 has a negative reference;
- the `removeHs` verification bug was found **by** these molecules.

So any number computed on set A is in-sample. That is settled and not worth arguing.

One refinement, because it changes what to do next. **A walkthrough is not a benchmark.** The brief
was a procedure a chemist can read and criticise — and for that, in-sample is not merely acceptable,
it is the point: you want the reviewer to see exactly where it breaks. The line is crossed the
moment a *number* is quoted as performance. So:

- **Set A → illustration.** Every stage, every intermediate, every failure, shown. No accuracy claim.
- **Set B → the only source of any claim.** Run once, after the freeze, untouched until then.

## What is frozen, as of now

No per-molecule intervention. The procedure is exactly this and does not branch on the reaction:

1. **S1 map** — RXNMapper on the heavy atoms; hydrogens propagate to their parent heavy atom.
2. **S1 accept/reject**, three checks, all automatic:
   - implied heavy-atom bond changes ≤ 3;
   - hydrogen map sets identical on both sides (re-parsed with `removeHs = False`);
   - every atom carries a map number.
   Fail any → **the reaction is reported as unmapped and does not proceed**. No hand map.
3. **S2** fragment-wise embed, **S3** contact placement at 2.5 Å, **S4** endpoint optimisation,
   **S4b** separated-fragment reference, **S5** IDPP, **S6** NEB, **S7** guard, **S8** barrier vs
   BH9 — all as already specified, each rung re-optimising its own endpoints.

**The two hand maps are cancelled.** #95 and #407 stay as failures. A procedure that needs a human
on 2 of 6 is not a procedure, and hand-mapping them would conceal the one defect this exercise most
needs to surface — that mapping is unowned and neither RXNMapper's confidence nor a bond-change
check detects its failures. **"Maps 4 of 6 unaided" is the result**, not an embarrassment to be
patched.

## Set B, selected by rule before anything is run

The candidate pool is the 18 neutral, closed-shell, multi-fragment BH9 reactions at ≤ 30 atoms
(`out/bh9_index.json`). Set A took six; twelve remain. Set B mirrors A's type composition
(1 × VII, 4 × II, 1 × IX), taking type II at ranks 1/3/5/7 by ascending barrier to span the range,
and type IX at the median:

| # | class | reaction | atoms | ref |
|---|---|---|---|---|
| 408 | VII | proton transfer, aryl carbamate + H₂O | 25 | 17.32 |
| 80 | II | Diels–Alder, dimethyltetrazine + cyclopropene | 24 | 6.61 |
| 101 | II | [3+2], nitrone + maleic anhydride | 28 | 10.45 |
| 103 | II | [3+2], cyclooctyne + methyl azide (SPAAC) | 29 | 12.65 |
| 91 | II | Diels–Alder, thiophene S-oxide + cyclopentenone | 22 | 16.35 |
| 435 | IX | nucleophilic addition, divinyl sulfone + methylimidazole | 25 | 13.77 |

**A known asymmetry, stated rather than hidden:** set B is systematically larger — mean 25.5 atoms
against A's 20.2 — because A took the small ones. B is therefore the *harder* set on cost and on
conformational freedom, so a B result at least as good as A's is meaningful, and a worse one is
partly confounded by size. Fixing this would require re-drawing both sets, which would spend the
held-out property we just created. Not worth it at n = 6.

## What n = 6 can and cannot support

Set B gives six Bernoulli trials on "does the procedure run unaided and return a number". A 6/6 has
a Wilson interval of roughly [61 %, 100 %] — so it can support *"no new failure mode appeared"* and
cannot support any accuracy figure. The **failure modes** are the informative output at this size,
not the rate.

If a barrier MAE is ever to be quoted, it needs the full 18-reaction pool or a wider BH9 draw, run
after this freeze, and reported as one number with its CI rather than six anecdotes.

## Pre-registered, before set B is run

1. Every set-A failure mode recurs in set B at a similar rate — in particular, **mapping succeeds
   unaided on 4 of 6**, not 6 of 6.
2. No *new* class of failure appears in B that A did not show.
3. Barriers on the mapped subset land within the DFT error BH9 itself reports for the functional
   used — for pericyclic reactions that is ~8 kcal/mol at PBE and ~2–3 at ωB97X, not better.

Prediction 1 is the one worth watching. If B maps 6/6, the S1 checks were tuned to A's failures and
we have learned less than it looks.
