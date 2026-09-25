# Are AFM's intermediates chemically sane, or merely valence-legal?

Short summary of the checks in `experiments/human_plausibility/` (full detail,
caveats and code pointers there). **Supersedes an earlier version of this
file** that reported AFM's intermediates as ~100% stable — that number came
from a check that never touched the trained model's weights at all. Once the
model's own generative process was actually tested, the conclusion reverses.
Kept here in full because the reversal, and why it happened, is the finding.

## Question

AFM's mask guarantees every intermediate along a mechanism is a
*valence-representable* molecule — but the paper's own flagged limitation is
that valence-admissible is not the same as chemically plausible; a real answer
needs DFT (the separate, not-yet-launched `specialty_11` NEB line). A cheap
proxy that needs no GPU: can each intermediate be embedded in 3D and locally
energy-minimized with a standard force field? And since a pass-rate alone
can't tell "the guarantee is doing real work" from "a lenient proxy passes
almost anything," a model with no such guarantee (DiscreteFlowER) was tested
as a control, and a model-free entrywise-interpolation baseline besides.

## Data

2,814 RMechDB reactions with a genuine ≥2-move admissible decomposition found
by the alphabet's own combinatorial search (`analysis/decompose_steps.py`; a
new `--dump_multistep` flag on `analysis/rmechdb_arrows.py` persists it —
*any* admissible decomposition, not necessarily the chemist's curated one,
since this tests the alphabet's intermediates, not human agreement). Same
2,814 reactants used across every row below, so the numbers are directly
comparable.

## Algorithm

Four different things were walked through the same embed/force-field proxy,
and the differences between them are the whole result:

1. **AFM, algorithmic path.** Apply the alphabet's own admissible move
   sequence (`decompose_steps.py`'s combinatorial search, which enforces a
   **per-element** valence cap at *every* step) via `scatter_moves` directly —
   no trained weights touched at all.
2. **AFM, real trained model.** Let `afm_nano` generate its own mechanism
   (`_rollout`'s sample decode, i.e. the same process `mapped_candidates`
   uses), recording a SMILES after every move actually taken.
3. **DiscreteFlowER, real trained model.** Let `flower_discrete_nano` generate
   its own Euler chain (10 steps), recording a SMILES after every step. No
   move alphabet exists for this model, so there is no chemist or algorithmic
   path to walk it through — self-generation is its only option.
4. **Entrywise interpolation toward the *true* product, no model at all.**
   DiscreteFlowER's own forward-noising schedule
   (`flip = symmetrize(rand < h/(1-i·h))`), but with the *true* product
   (mechanically computed by applying row 1's move sequence, not predicted)
   standing in for the model's guess at every step. Isolates whether
   entrywise resampling is inherently prone to invalid states, independent of
   how good the model's predictions are.

Every reconstructed state, mid-mechanism and final alike, was checked for: (a)
does it reconstruct to a valid molecule at all — impossible to fail for row 1,
by construction — (b) does it embed in 3D (RDKit ETKDG), (c) does a force
field (MMFF, falling back to UFF) converge on it.

## Result (2026-09-18)

| | mid-mechanism reconstructs | final reconstructs |
|---|---|---|
| 1. AFM, algorithmic path (no weights) | 100.0% | 100.0% |
| 2. AFM, real trained model (self-sampled) | **21.6%** | 47.4% |
| 3. DiscreteFlowER, real trained model (self-sampled) | 47.5% | 41.6% |
| 4. Entrywise interpolation toward the true product (no model) | 64.7% | 100.0%¹ |

¹ by construction — row 4's target *is* the true product.

**Row 2 vs. row 3 is the real finding, and it's the opposite of what row 1
alone suggested: AFM's actual trained model produces *less* reconstructable
mid-mechanism intermediates than DiscreteFlowER's, a model with no
admissibility guarantee whatsoever.**

Why rows 1 and 2 disagree so sharply, traced to source: `models/afm.py`'s
`move_mask` — checked at *every* step — only enforces generic, element-
agnostic bounds (`MAX_DIAG=14`, `MAX_BETA=12`, sized for the whole periodic
table). Real per-element valence (`local_table()`) is enforced only once, at
the **stop** decision (`stop_mask`). So the model is structurally free to
wander through states where, say, a carbon atom is transiently at bonding
count 6 — globally representable, nowhere near a real carbon — as long as it
returns to a per-element-valid state before choosing to stop. `nano`'s move
choices exploit that slack far more than DiscreteFlowER's context-free
resampling does. Row 1's 100% reflects a *stricter* check
(`decompose_steps.py`'s own per-element-at-every-step search), never the
model's own per-step behaviour.

Two further measurements on the same self-sampled AFM chains explain the
mechanism concretely:
- **Chains are ~80% longer than necessary.** For the same reactants, the
  algorithmic minimal decomposition averages **2.13 moves**; AFM's
  self-sampled chains average **3.84**.
- **16.2% of chains never find a legitimate stop at all** — they exhaust the
  `max_moves=12` budget still in a state the model won't stop from.
- Within a chain, invalid steps are usually a single-step blip immediately
  followed by a valid one (4,191 of the observed invalid runs are length 1) —
  a real but self-correcting overshoot-and-return pattern — but a second,
  worse population never corrects: invalid runs of length 11-12 (629+347
  occurrences) account for most of the budget-exhausted chains.

Row 4 (64.7%, guided by the *true* answer, no model at all) puts a floor
under row 3: even perfect knowledge of the destination, run through pure
entrywise resampling, produces an invalid intermediate about a third of the
time. DiscreteFlowER's actual rate (47.5%) is worse than that floor, so its
gap from row 1 is partly the representation and partly the (`nano`,
undertrained) model — whereas AFM's shortfall (row 2 vs. row 1) is *entirely*
attributable to the model's own per-step mask being looser than the
alphabet's theoretical best case, since the representation itself, walked
strictly, hits 100%.

## Why final reconstruction is only 47.4% for AFM's real model

Split by whether the chain actually found a state it was willing to stop
from:

| | n | final reconstructs |
|---|---|---|
| Chains that hit `max_moves=12` without ever stopping | 1,324 | 0.7% |
| Chains that legitimately stopped (`stop_mask` said yes) | 6,826 | 56.5% |

The stuck 16.2% behave exactly as expected — a chain that never found a
state worth stopping from produces junk almost universally when forced to
end. The more important number is the other row: **43.5% of the time even a
*legitimate* stop — the model's own per-element table (`local_table()`) said
the state is a real molecule — still fails RDKit's sanitizer.** Sampling many
such cases directly and reading the raw error rather than guessing: the
dominant failure (52% of a 170-case sample) is a plain `AtomValenceException`
— genuine over-valence (one concrete case: a carbon RDKit reports at valence
6 that the model's own table had marked admissible) — not the aromaticity /
kekulization edge case `_emit`'s own docstring warns about. So `stop_mask`'s
table and RDKit's real valence rules disagree on a non-trivial slice of
states; this is a gap in the model's internal self-consistency, not only in
its choice of which states to pass through.

**This was never visible to the paper's own reported metrics, and here is
exactly why.** `models/afm.py`'s `_emit()` — used inside `mapped_candidates`,
the same code path `eval.py`'s headline numbers come from — silently replaces
any candidate that fails to reconstruct with **the unchanged reactant**
before any metric is computed. The reactant always reconstructs (it's the
original, already-valid input), so a generation failure becomes "predicted no
reaction happened," which trivially passes validity and every conservation
check. It would only cost step accuracy (a wrong prediction) — and RMechDB's
radical chemistry was never part of the paper's own USPTO-derived test split
to begin with. This same `nano` checkpoint reports `validity_micro_top1: 1.0`
on its own standard test split (`ArrowFlowMatching/outputs/runs/afm_nano/…/metrics_*.json`
from the earlier calibration run). Structurally, not by oversight, the
paper's validity metric cannot show this failure mode.

## Update: the mask bug is fixed and tested (`problem01-validity.md`)

The `(diag,beta)`-only table behind row 2's stop decision was traced to a
specific bug (implicit hydrogens aren't tracked) and fixed with a corrected,
H-aware table — see `problem01-validity.md` for the full diagnosis, repro, and
a second bug caught in the first attempt at the fix itself (corrected same
day). Applying the properly-corrected fix to this same checkpoint,
unretrained: mid-mechanism reconstruction drops (21.6% -> 13.8%), but final
reconstruction is essentially unchanged, if anything slightly better (47.4% ->
50.9%) — most final states the model reaches don't depend on the specific
H-bookkeeping this bug affects. The real, surviving finding is narrower than
first reported: a large minority of self-sampled chains (roughly 60-65%,
checked two ways) never find a state the corrected mask will let them stop
from at all, largely independent of move budget or hydrogen access — a
genuine competence gap, but not the near-total (~98%) one the buggy version of
the fix suggested. The masking fix itself is free and immediately correct
(now implemented directly in `models/afm.py`, not as an external patch); a
model trained under it would likely still improve on the stuck rate, just
from a real ~60-65% baseline rather than an inflated ~98% one.

## Correction and re-scoping (2026-09-18, see `problem02-termination.md`)

Every RMechDB number above was measured on a model that is out of
distribution on that data (its radical sector is one Pd–P move deep), and
two of the readings were artefacts: the "final reconstructs 47–61%" rows
counted the 12th state of a never-terminated chain as a product, and the
mid-mechanism rows graded intermediates the paper explicitly does not claim
to be molecules (Limitation iii). What survives: Proposition 2 holds exactly
— every chain that chose `Stop` reconstructs (4,529/4,529 with explicit
hydrogens) — and the alphabet-strict row 1 stands. The question this
experiment asks, *are the states the chain actually visits readable, stable
chemistry*, has to be answered where the released checkpoint terminates
normally: on FlowER's own test reactants (stuck rate 0.4%, vs 35% on RMechDB).

**In-distribution plan (running locally):**
- `instrumented_rollout.py --flower_txt data/flower_test_sample.txt` — 3,000
  FlowER test steps (random sample of `test.txt` from RCI), 3 chains each,
  per-step move log. Done: `results/instrumented_flower.jsonl`.
- `flower_intermediate_stability.py` — replays the log, reconstructs every
  intermediate and emitted final, and reports three things kept apart:
  in-Sector (the paper's own "is a molecule"), reconstructs, embeds /
  force-field converges. First pass on 1,000 reactants.
- `flower_discrete_stability.py --flower_txt ...` — the DiscreteFlowER
  control on the *same* 1,000 FlowER reactants, so the mask-vs-no-mask
  comparison is apples-to-apples for the first time (the earlier control ran
  on RMechDB, where AFM was out of distribution).
- RMechDB stays in this note as a finding, not a benchmark: on a radical
  substrate the readable intermediate says "C–H broken, done".

### In-distribution result (2026-09-18; first 1,000 of the 3,000 sampled FlowER test steps, 3 chains each)

| | chains scored | mid-states n | mid in Sector | mid reconstructs | mid embeds | mid FF-converges | finals n | final reconstructs | final FF-converges |
|---|---|---|---|---|---|---|---|---|---|
| AFM (released), self-sampled | 2,442 (+558 immediate `Stop`) | 3,822 | **30.9%** | 59.4% | 59.2% | 34.8% | 2,433 | **100.0%** | 63.7% |
| DiscreteFlowER (released), 10 Euler steps | 3,000 | 27,000 | n/a (no Sector) | 69.5% | 69.5% | 45.6% | 3,000 | 97.4% | 63.1% |

Read with the paper's own definitions: AFM's *emitted* states are molecules
without exception (Proposition 2; DiscreteFlowER's are not, 97.4%), and about
a third of the states an in-distribution chain passes through are molecules
too — the paper's book-keeping intermediates (Limitation iii) are the other
two thirds, and 59% of all intermediates still reconstruct to *something*
RDKit accepts. DiscreteFlowER's higher mid-state numbers are not evidence of
better intermediates: its Euler chain resamples a small random subset of
entries per step (copy-initialised, most positions unchanged), so most of its
"intermediates" are the reactant or the product with one or two entries
switched, which trivially reconstruct. The comparable quantity is the final
row. Force-field convergence at ~63% for *both* models' finals is a ceiling
of the proxy (MMFF, 500 iterations, 60–150-atom molecules), not chemistry — on
the small RMechDB molecules the same proxy converges at 96%.

**Fine-tuning made intermediates more readable, not less** (RMechDB test
split, `flower_intermediate_stability.py` on the instrumented test logs):
mid-states in Sector 11.9% (released, wandering) → **81.0%** (fine-tune B),
reconstruct 14.1% → 81.4%, FF-converge 13.9% → 79.6%; finals 100% in Sector
for both. Details in `afm-human-check.md` § Track 2.

## Headline caveat

Not DFT-quality evidence, and can't rule out a real barrier problem — that's
what the `specialty_11` NEB line is for. `nano` width throughout, and
DiscreteFlowER's untuned 10-step Euler schedule; not the paper's own
full-scale validity numbers, but the same conditions applied to every row
here, which is what makes the comparison fair. This does **not** show AFM's
construction is a bad idea — row 1 shows the alphabet itself, applied
strictly, is fully stable; it shows this particular `nano` checkpoint's
learned move policy doesn't yet make full use of the guarantee the
architecture is *capable* of providing. Whether that's a `nano`-scale
training artifact or persists at full scale is untested here.
