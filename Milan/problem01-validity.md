# Problem 01 — Remark 4's own dropped term, in the one case it wasn't verified against

Found while building `experiments/human_plausibility/` (full context in
`afm-internal-stability.md`). Written up separately because it's a specific,
fixable claim about the code, not a result about the paper's evidence.

**This is not an independent bug report — it's a measurement of a risk the
paper already names.** Remark 4 (p.17): *"On this dataset every hydrogen is
written explicitly and carries an atom map, so it has a row of the matrix
like any other atom and n_i^H = 0 throughout, and measured over 8000 test
reactants, the total number of implicit hydrogens is zero. **The term is
kept in (1) because the formalism is not specific to this dataset, but no
measured quantity depends on it, and in the implementation β_i is a plain
row sum.**"*

That is a direct statement, in the paper's own hand, that (a) the general
formalism carries an implicit-hydrogen term n_i^H, (b) the *implementation*
drops it — `beta = state.sum(-1) - diag` in `stop_mask`/`in_sector` is
exactly "β_i is a plain row sum" — and (c) this is only correct because, on
this dataset, n_i^H is measured to be zero everywhere. RMechDB (curated
literature radical chemistry, used here as an out-of-distribution probe) is
the case Remark 4 doesn't cover: real heavy atoms there carry nonzero
implicit hydrogens (measured, 8,969 sampled atoms: 25,199 at n_H=0, 11,878 at
n_H=1, 9,461 at n_H=2, 7,548 at n_H=3 — the underlying counts run into the
tens of thousands across the corpus). Reinstating n_i^H (as `local_table_h`
below) is doing exactly what Remark 4 says the formalism already anticipates;
this note is the measurement of what happens without it, once the one
dataset property the simplification relies on no longer holds.

## Claim

AFM's advertised guarantee — "a candidate can only leave the chain from a
state that is already a molecule" (`models/afm.py` module docstring) — is
false for a measurable fraction of states *whenever n_i^H is not identically
zero*. The mask that is supposed to enforce it, `stop_mask` + `local_table()`
(the `β_i`-only implementation Remark 4 describes), sometimes says a state is
a valid molecule when RDKit's own sanitizer says it isn't.

## Reproduction

Two real carbons, deliberately given the same `(diag, beta)` reading but
different n_i^H — the term Remark 4 keeps in the math and drops in the code:

```
CH  (n_H=1, 3 heavy bonds): diag=0, beta=3 -> valid  (4 total, correct)
CH2 (n_H=2, forced to 3 heavy bonds): diag=0, beta=3 -> invalid (over-valent)
```

`local_table()[C, diag=0, beta=3]` returns **`True` for both** — it has no
n_H axis to tell them apart, exactly the simplification Remark 4 names. RDKit
accepts the first and raises on the second:

```
AtomValenceException: Explicit valence for atom # 1 C, 6, is greater than permitted
```

This isn't a rare corner case: on the 2,814-reaction stability check
(`experiments/human_plausibility/afm_sampled_stability.py`), 43.5% of chains
that `stop_mask` approved (i.e. the model legitimately chose to stop, not a
budget timeout) still failed RDKit reconstruction — 52% of a 170-case sample
of those were this exact failure mode (plain `AtomValenceException`, not the
aromaticity/Kekulé residue Appendix J.3 already reports, a different and
separately-acknowledged limitation of the checker).

## Root cause

The four-move alphabet (`LONE_TO_BOND`, `BOND_TO_LONE`, `HOMOLYSIS`,
`COLLIGATION`) only ever moves electrons between two *heavy* atoms — no move
touches a bond to hydrogen, so n_i^H is fixed for the whole trajectory once
the reactant is parsed (`chem._lone_pairs` reads it once, via
`atom.GetTotalNumHs()`, and folds it into `diag`; nothing downstream carries
it forward as its own quantity). `stop_mask`'s admissibility table is keyed
only on `(element, diag, beta)` — `β_i`, per Remark 4, with no separate n_H
axis. Built by aggregating over all atoms at that key, the table necessarily
conflates atoms that share a `(diag, beta)` reading but differ in n_i^H, and
admits whichever case is in the majority for that key — wrongly, for the
minority. On the paper's own dataset the minority is empty (n_i^H ≡ 0
everywhere, per Remark 4's own measurement), so the conflation is invisible;
on RMechDB it is not.

## Why the paper's own metrics never caught this

Two independent reasons, both consistent with Remark 4 rather than
contradicting it. First, and primarily: Remark 4's own measurement (n_i^H = 0
over all 8,000 test reactants) means the conflation this note reports simply
has no minority case to be wrong about on that split — there is nothing for
the paper's own evaluation to catch, because the situation doesn't occur
there. Second, a separate, compounding reason: `models/afm.py`'s `_emit()`
(used inside `mapped_candidates`, the same path `eval.py`'s headline numbers
come from) silently replaces any candidate that fails to reconstruct with
**the unchanged reactant** before any metric runs. The reactant always
reconstructs, so a generation failure becomes "predicted no reaction
happened" — passes validity and every conservation check, costs only step
accuracy. `afm_nano` reports `validity_micro_top1: 1.0` on its own standard
test split for both reasons at once; RMechDB's radical chemistry, where
n_i^H is not zero, was never part of that split.

## Impact

- **The published validity guarantee needs Remark 4's qualifier stated where
  the guarantee itself is, not only in the appendix.** As implemented it
  holds conditional on n_i^H ≡ 0, which the appendix already measures and
  states — but the main-text guarantee ("a candidate can only leave the chain
  from a state that is already a molecule") reads unconditional. Reinstating
  n_i^H (below) removes the condition instead of just documenting it.
- **Downstream metrics that rely on `mapped_candidates`' reconstruction
  (validity, step accuracy, anything built on `_emit`) are quietly biased**
  toward "no reaction predicted" on exactly the states this bug produces,
  rather than reporting them as failures.
- Likely worse on chemistry further from the training distribution (RMechDB
  radicals here) than on the paper's own in-distribution test split, since the
  table's blind spots are wherever the corpus under-samples a given
  `(element, diag, beta)` key relative to the H-count distribution behind it.
- **The same bug reaches into training, not just inference.** `in_sector()`
  (`models/afm.py:261`), which `decompose()` calls to decide whether a
  training step's *known-correct* product is "a state the chain may stop
  in," uses the identical `local_table()`. A real, valid product whose atom
  happens to be the H-count minority for its `(element, diag, beta)` key can
  be wrongly marked not-in-sector, making `decompose()` return `None` and
  `CollateAFM.trainable()` drop that step from training entirely — the bug
  can silently shrink and bias the training set, not only mislead inference.

## Two more explanations checked (numbers corrected below)

Before treating a very-high stuck rate as evidence the model merely needs
*more room* or *more hydrogens*, both were checked directly:

- **Not (mainly) a budget problem.** Raising `max_moves` from 12 to 40 (3.3x)
  on a 300-reaction sample: 65.3% stuck at 12, 64.0% at 40 (re-measured against
  the corrected table below; an earlier pass against a still-buggy version of
  the fix read 99.3%/99.2% — see the correction note). Barely moves either
  way — a real wall for a majority of chains, not a clock running out, though
  a substantial minority (~35%) does resolve given more room.
- **Not (mainly) the missing-explicit-hydrogen ceiling.** A real, separate
  limitation exists (below), but it isn't the dominant driver: reactions with
  a mobile hydrogen already promoted to an explicit atom are stuck 62.5% of
  the time; reactions with none at all are stuck 58.2% — close, not the stark
  split a dominant cause would produce.

Both point the same way, just less starkly than first measured: a majority of
self-sampled chains don't find a state the corrected mask allows them to stop
from, largely independent of budget or hydrogen access — a real competence
gap, but not the near-total one first reported.

## A related, separate limitation: hydrogen promotion is frozen before generation starts

Why isn't every hydrogen just represented explicitly, avoiding this whole
class of bug? Cost: the representation is O(N²) throughout (attention over
the bond-electron matrix, a `NUM_MOVES x N x N` logit tensor per step), and
the overwhelming majority of hydrogens are spectators in any given step —
making all of them explicit would multiply that cost for every training
example to benefit the rare ones that need it.

The actual design instead promotes only the hydrogens a step's *known*
mechanism moves (2,545 individually-mapped `[H:n]` atoms found in this
corpus) — but that promotion is decided from the known reactant-product pair
at *training-data-construction* time, not by the model. At generation time,
the model can only move a hydrogen that happened to already be promoted in
the given input; it has no move to reveal a hydrogen it decides, mid-
generation, that it needs. This is real and worth keeping in view (a possible
target for a fifth "reveal" move type, longer-term), but the explicit-H test
above shows it is not the explanation for the current numbers.

## Fix implemented and tested (2026-09-18, corrected same day)

Add implicit-hydrogen count as a fourth axis to the validity table
(`(element, diag, beta, n_H)`), built the same way `local_table()` already
is — pure enumeration, no training data, no retraining needed to deploy (the
table is a non-persistent buffer, recomputed fresh, never part of the
checkpoint). This does not let the alphabet *repair* an over-valent state (it
still has no move that touches hydrogen) — a mechanism arriving at a
genuinely hydrogen-inconsistent state would still need to be rejected
earlier, or the alphabet extended — but it makes `stop_mask` a correct
arbiter of what it already claims to check, rather than a table that
provably disagrees with itself on identical keys.

**Correction, same day.** The first implementation (external, in
`experiments/human_plausibility/corrected_mask_stability.py`, not touching
Milan's checkout) had its own bug: the probe used to build the corrected
table adds `n_H` fixed hydrogens to a synthetic test molecule, but the
electron-count and atom-composition checks that decide whether the probe
"survived" were never updated to expect them — so *every* probe with `n_H >
0` failed, regardless of real validity. That table had only 9,584 admissible
entries; fixing both checks (expected electrons `+= 2 * n_H`, expected atoms
`+= n_H` hydrogens) raises it to **45,692**. Caught by testing the exact CH
vs. CH2 case from the reproduction above directly against the table: it
initially rejected CH (should be admissible) as well as CH2 (correctly
rejected), which is not what a correct fix does. The numbers below are from
the corrected version, now implemented directly in `models/afm.py` (not
external) as part of the Phase 0 work below, since a real fix needs to reach
training too, not just this experiment's inference calls.

Reran the exact same self-sampled rollout (`afm_sampled_stability.py`) with
only the mask corrected, same checkpoint, same reactants:

| | mid reconstructs | final reconstructs | chains hit `max_moves` budget (2.3x width) |
|---|---|---|---|
| Original (buggy 3-axis) mask | 21.6% | 47.4% | 16.2% |
| Corrected (4-axis, H-aware) mask | **13.8%** | **50.9%** | ~60-65%¹ |

¹ from the two ruled-out checks above (300-400 reaction samples), not the full
run; the full-run budget-exhaustion rate was not separately tabulated.

**Read plainly, this time accurately: fixing the bug does not produce the
dramatic collapse first reported.** Final-state reconstruction is
essentially unchanged, if anything slightly better (47.4% -> 50.9%) — most
final states the model reaches do not depend on the specific H-bookkeeping
this bug affects. Mid-mechanism reconstruction drops (21.6% -> 13.8%): a real,
smaller tightening, consistent with a stricter per-step stop option changing
which trajectories get sampled at all, not merely which endpoints get
accepted. The substantial, real finding that survives is the ~60-65%
stuck rate from the two ruled-out checks above — a genuine, large minority
(not a near-total) inability to satisfy a correct stopping criterion,
independent of budget or hydrogen access. That is still worth a retrain to
address, just a materially smaller claim than "only 2% of what looked like
success was real."

## Retrain campaign — on hold; see "Retraining is a no-op" below

Goal: a checkpoint whose stop decision is trained under the *corrected*
criterion, closing the ~60-65% stuck-rate gap above (not the earlier,
incorrect ~98% figure). Two phases, gated by an explicit decision point — the
first is inexpensive and answers whether the second is worth funding.

**Phase 1 should not be launched as written.** Before any GPU time was spent,
checking what the corrected mask actually changes on the *existing* training
corpus found `n_i^H` is 0 for essentially every real training step already —
see the section below. `training_loss` never encounters a state where the
corrected `stop_mask` disagrees with the original, so a retrain on this
corpus, with this fix, reproduces the current checkpoint's weights up to
noise. The phases below are kept as a record of the original plan and would
need a different premise (a training corpus that actually contains nonzero
`n_i^H` states) to be worth running.

Built on top of `fix/radical-moves` (uncommitted, predates this work; its own
independent fix generalizes `_radical_moves` for multi-move radical training
targets, see the branch's diff and `bug_radical_moves.md`) — same branch,
since both fixes touch `decompose()`'s pipeline. Per instruction, this round
stays within Phase 0's own code-and-data-selection scope, not `training_loss`
in isolation from it, though in practice the two ended up needing the same
`n_H` plumbing since `training_loss` calls the same masked `_score`.

### Phase 0 — done (2026-09-18)

1. **`chem.py`**: added `atom_n_hydrogens(mol)`, ordered like
   `atom_types_and_be`. Committed (`30756c7`, `fix/radical-moves`).
2. **`models/afm.py`**: added `local_table_h()`/`_probe_h()`/`_build_table_h()`
   (the 4-axis table, cached separately as `local_table_h.npy`), and threaded
   `n_H` through `in_sector()`, `decompose()`, `stop_mask()`, `_score()`,
   `training_loss()`, `_rollout()`, and `mapped_candidates()`. Committed, same
   commit.
3. **`CollateAFM`**: `featurize()`/`collate()` now compute and carry `n_H`
   through to the batch dict. Committed, same commit.
4. **Pushed to `rci` and reconciled with the live RCI checkout**
   (`~/ArrowFlowMatching`, where `sbatch` jobs actually run). That checkout
   had its own uncommitted diff — byte-identical to the radical-moves half of
   the pushed commit — safely stashed (not dropped) rather than discarded, and
   the checkout switched to `fix/radical-moves`. No stale feature cache
   existed to invalidate (`data/flower_new_dataset/cache/` doesn't exist yet —
   nothing has actually started training; all queued jobs were still
   `PENDING`), so the next real run builds it fresh, already `n_H`-aware.
5. **Sanity check, on the real corpus**: sampled 20,000 real training steps
   and compared `decompose()`'s `usable` verdict with `n_H` forced to zero
   (mathematically identical to the pre-fix table — `_probe_h(...,0)` reduces
   to exactly `_probe(...)`) against the real per-atom count. **0 recovered,
   1 newly dropped, 99.98% unchanged.** Unlike the separate radical-moves fix
   (41-78% of radical steps recovered), the H-count bug barely touches which
   training examples get used at all — real curated products mostly aren't
   the ambiguous minority-hydrogen-count case the bug mishandles. Its
   measured effect is almost entirely at inference/self-generation time (the
   mid-mechanism/final-reconstruction numbers above), where the model
   wanders into states real chemistry never produces as a training target.

### Phase 1 — nano pilot (the actual go/no-go experiment)

One retrain at `nano` (the repo's own quoted cost: ~26 GPU-hours, one seed),
identical to the existing checkpoint's config in every other way, so the only
variable is the corrected mask/data. Compare against the current `afm_nano`
checkpoint on:

- **This experiment's own stuck-rate proxy** (`afm_sampled_stability.py`,
  rerun against the new checkpoint — the fix now lives in the model itself,
  so no separate script is needed) — the primary signal. Baseline to beat is
  the corrected-mask number on the *current* checkpoint, ~60-65% stuck, not
  the original, incorrect ~98%; a plausible "worth continuing" threshold is a
  large fraction of that gap closed, exact number to be set by the user.
- **`eval.py`'s standard metrics** (step accuracy, validity, conservation) on
  the paper's own test split — must not regress materially, or the fix has
  traded a hidden bug for an open one.
- **The human-plausibility rank test and alphabet-composition check**
  (`score_reactions.py`/`analyze.py`, `alphabet_composition.py`) rerun against
  the new checkpoint — does interpretability agreement hold up or improve
  once the model is trained under the corrected constraint?

Also worth deciding in advance: `nano` is 1.2M parameters. It may simply lack
the capacity to learn a materially stricter criterion well, in which case a
modest improvement (not a full recovery) at `nano` would not be evidence the
fix failed — only that `nano` is the wrong width to see its full effect. Flag
this rather than over- or under-reading the pilot's number in isolation.

### Phase 2 — full width-ladder validation (large; separate approval)

Only if Phase 1 clears its bar. Matching the paper's own protocol
(`scripts/submit_table.py`: 5 widths x 5 training seeds x 5 eval seeds), this
is the same scale as the paper's original comparison table — real multi-day,
many-GPU-hour RCI compute, not a small follow-on. This needs its own explicit
sign-off when Phase 1's result is in hand, not a standing green light from
"design a retrain campaign."

## Retraining is a no-op on this corpus — a preprocessing-only alternative (2026-09-18)

**Why retrain, if the training set already has `n_i^H` = 0 everywhere?** That
question, asked before Phase 1 was launched, is the right one. Sampling the
real training corpus directly (20,000+ steps, both even- and odd-parity)
found **0.00% have a nonzero per-atom hydrogen count** — 2 of 40,014
even-parity steps and 0 of 1,034 odd-parity steps. `training_loss` calls the
same masked `_score`/`stop_mask` that inference does, so if the states it
ever scores all have `n_i^H = 0`, the corrected 4-axis table and the original
3-axis one agree on every one of them by construction (`_probe_h(..., 0)`
reduces exactly to `_probe(...)`). Retraining with the fix, on this corpus,
cannot change the learned weights beyond optimizer noise.

The reason is Remark 4 itself: FlowER's own preprocessing maps **every**
hydrogen as its own explicit graph atom before training, so `n_i^H` is
identically 0 by the data's own construction, not by luck. The bug only bites
at the boundary the paper's own remark names — new data, such as RMechDB fed
in at inference here, that does not follow that convention and leaves most
hydrogens implicit.

That reframes the fix. If the checkpoint already expects every hydrogen
explicit, the cheapest correct fix is not a code patch to `stop_mask` and not
a retrain — it is making new data match the convention the checkpoint was
already trained under, with **zero changes to `models/afm.py` and zero
retraining**.

### What was tried

`experiments/human_plausibility/fully_explicit_stability.py`
(`fully_explicit_atom_map`): parse the RMechDB reactant, run RDKit's
`Chem.AddHs()` to materialize every implicit hydrogen as its own atom, then
assign every atom — hydrogens included — a fresh contiguous map number. This
makes `n_i^H` exactly 0 for every atom, by the same mechanism as FlowER's own
preprocessing, before the SMILES ever reaches the model.

Critically, this ran against the **unmodified, currently-checked-out**
`models/afm.py`/`chem.py` (the `filter-only` lineage — no `n_h` parameter
anywhere in `_score`, `stop_mask`, or `_rollout`) and the same,
un-retrained `afm_nano` checkpoint used throughout this document. The only
thing that changed between this run and the original `afm_sampled_stability.py`
baseline is the input SMILES convention. `n_h` was independently recomputed
per reactant as a sanity check on the preprocessing itself (not fed to the
model, since this code path takes no such argument): 0 nonzero atoms across
all 2,814 reactants, confirming the transform does what it claims.

Same self-sampled rollout, same reactant set (`multistep.json`, all 2,814),
same `num_chains=3`:

| | mid reconstructs | final reconstructs |
|---|---|---|
| Original code + RMechDB's own mapping (implicit H) | 21.6% | 47.4% |
| Corrected 4-axis (H-aware) mask, same mapping | 13.8% | 50.9% |
| **Unmodified code + fully-explicit-H preprocessing** | **17.6%** | **60.9%** |

### Reading this honestly

Final-product reconstruction is the best of the three under preprocessing
alone (60.9%, beating both the untouched baseline and the code patch) with
no model change at all — consistent with the hypothesis that the checkpoint
already knows what to do with these states when they are presented the way
it was trained to see them, and the earlier low numbers were partly an
input-convention mismatch rather than purely a model limitation.

**Mid-mechanism reconstruction does not follow the same pattern**: 17.6% is
worse than the untouched baseline (21.6%), though still better than the code
patch (13.8%). This is not the clean "gap closed" result the question
predicted, and it should not be reported as one. A plausible but *unverified*
explanation: `Chem.AddHs()` roughly triples the atom count for a typical
organic reactant, so every per-step move (`kind`, `i`, `j`) now ranges over a
correspondingly larger set of atoms, most of them hydrogens irrelevant to the
actual reaction — a much larger softmax at every step than the model saw
mid-chain during training on this specific class of reactant sizes, which
would degrade intermediate move selection even where the final stop decision
still lands correctly. The two reconstruction populations are also not
strictly comparable: a larger `N` plausibly changes the chain-length
distribution itself, so "mid" spans a different mix of positions here than in
the RMechDB-native rows. Neither claim is verified — flagged as the next
thing to check, not asserted.

**Bottom line**: preprocessing to match FlowER's own convention is a real,
zero-code, zero-retrain lever, and it is the best lever tried so far for
final-product reconstruction specifically. It is not a substitute for
understanding the mid-mechanism gap, which remains open and is now better
isolated (it survives both the code patch and the input-convention fix, so it
is not solely an `n_i^H`-bookkeeping artifact).

## Splitting the mid-mechanism sample (2026-09-18)

The mid-mechanism gap survives both fixes tried above, which raises the
question this section answers: is it one effect, or several conflated ones?
`experiments/human_plausibility/analyze_mid_gap.py` joins every self-sampled
mid-mechanism step (`fully_explicit_stability.jsonl`, 38,292 steps over 2,814
reactants x 3 chains) back to `multistep.json`'s reaction-class/stage
metadata and RDKit-derived size features, and breaks reconstruction rate down
by each.

**Dominant finding: most of the gap is the already-documented stuck-chain
problem, counted twice.** Splitting steps by whether *their own chain*
eventually finds a valid stop within the 12-move budget (`max_moves=12`) or
exhausts it without stopping:

| | share of all mid-steps | reconstructs |
|---|---|---|
| Chain hits the 12-move budget, never stops | 86.6% (33,165 / 38,292) | 12.1% |
| Chain stops on its own | 13.4% (5,127 / 38,292) | **53.6%** |

Across all 8,442 sampled chains (2,814 reactants x 3), 35.7% (3,015) run out
the full 12-move budget without ever choosing to stop — this is the same
population the earlier ~60-65% stuck-rate estimate was sampling. Because a
stuck chain keeps moving (and keeps contributing steps) for far longer than a
well-behaved one, it dominates the mid-mechanism step *count* even more than
it dominates the chain count: 87% of all scored mid-steps come from chains
that never find a valid stop. **The 17.6% aggregate mid-mechanism number is
therefore mostly a restatement of the stuck-rate problem, not an independent
finding about intermediate-state quality.** When a chain does behave well,
its intermediate states reconstruct at 53.6% — well short of the final-state
rate (60.9%) but much closer to it than the aggregate number suggested, and
not the separate, mysterious defect it first looked like.

Position within the chain tells the same story from a different angle:
reconstruction is 50.1% at the first self-generated move (a state one step
removed from the real, valid reactant) but falls to 8.3% by position 3+ (66%
of all mid-steps) — consistent with error/wandering accumulating specifically
in chains that don't stop, not with a flat, position-independent weakness.

**Independent of stuck-ness, reaction class still matters — a plausible
class-imbalance effect.** `Termination`-stage steps (6.6% of chains) and
`recombine`-class steps (0.7%) reconstruct at 6.4% and 3.3% respectively,
markedly worse than the corpus-dominant `Propagation`/`abstraction` steps
(53% of the corpus, 15.6%) or `addition`/`resonance` (20.5%/22.3%) —  **and
this is not explained by the stuck-chain mechanism above**: `Termination` and
`homolyze` chains actually have the *lowest* stuck rates (2.8%, 1.0%, vs
43.4% for `Propagation`), so most of their mid-steps come from chains that
already found a valid stop, yet those intermediate states still fail to
reconstruct unusually often. The plainest reading is ordinary undertraining
on rare reaction types, not a hydrogen-bookkeeping or move-space artifact —
worth checking against the real FlowER training corpus's own class balance,
not just this test corpus's, before treating it as confirmed.

**Size does not cleanly support an OOD-by-molecule-size story.** The raw
marginal trend runs the *other* way: reactants with 24+ heavy atoms
reconstruct mid-steps at 26.4% vs 14.5% for 8-11 heavy atoms — bigger, not
smaller, reconstructs better. This is more plausibly a confound with reaction
class (larger substrates skew toward `addition`/`resonance`, which already
reconstruct better) than genuine evidence that size helps; it does rule out
"the model just can't handle bigger post-`AddHs` graphs" as a standalone
explanation, though, since that would predict the opposite sign.

**The separately-documented `_radical_moves()` training-data bug
(`bug_radical_moves.md`) is not testable on this corpus.** 38,289 of 38,292
mid-steps (99.99%) come from reactants whose human-annotated route contains a
HOMOLYSIS/COLLIGATION move — this corpus is essentially all radical
chemistry, so there is no non-radical contrast group here to check whether
mid-mechanism failure concentrates on the multi-move radical training data
that bug drops. Confirming or ruling out that hypothesis needs either a
predominantly polar/heterolytic multi-step test corpus, or a direct check of
which training steps the bug actually dropped against these reactants' local
BE-matrix deltas — neither has been done yet.

**Failure is only moderately shared across preprocessing variants.** Per
reactant, the mid-step reconstruction rate correlates at r=0.308 between the
fully-explicit-H run and the original RMechDB-native-mapping run (1,761
reactants with mid-steps in both). Only 0.5% of reactants reconstruct every
mid-step in both variants and 5.8% reconstruct none in either; most sit in
between. A correlation this far from both 0 and 1 is consistent with mid-step
difficulty being partly an intrinsic property of the reactant (surviving the
preprocessing change) and partly sensitive to the input convention itself
(e.g. the move-space-dilution effect proposed above) — neither a pure
reactant-OOD story nor a pure preprocessing-artifact story fits alone.

**Correction (2026-09-18, later the same day; see `problem02-termination.md`)**:
splitting the *final* states the same way settles the matter. Chains that
chose `Stop` on their own reconstruct **4,529 / 4,529 = 100.0%** —
Proposition 2 holds exactly on the preprocessed data. The "final reconstructs
60.9%" above counted the 12th state of a never-stopped chain as a product
(those reconstruct 2.1%), and every mid-mechanism number measured
intermediates the paper itself says need not be molecules. There is one
phenomenon here, 35% of chains never choosing `Stop`, and it is 0.4% on
FlowER's own test reactants. Its cause is not hydrogen bookkeeping and not
class imbalance: it is the radical sector (`problem02-termination.md`, H1′).
The paragraph below is kept as the record of the intermediate reading.

**Revised picture (superseded)**: what looked like one open "mid-mechanism gap" is at
least two distinguishable effects — (1) a large-volume one, chains that never
find a valid stop, which is the stuck-rate problem already under discussion,
not a new defect, and (2) a smaller-volume but real one, rare reaction
classes (`Termination`, `recombine`) reconstructing poorly independent of
stuck-ness, consistent with ordinary class imbalance. The move-space-dilution
hypothesis remains plausible but unconfirmed and is not needed to explain
most of the observed gap.

## Where the supporting data lives

`experiments/human_plausibility/README.md` ("Why is final reconstruction so
low" section) and `afm-internal-stability.md` — full stability numbers, the
DiscreteFlowER/entrywise-interpolation controls, and the chain-length/
stuck-chain analysis this was found alongside.
`experiments/human_plausibility/fully_explicit_stability.py` and its
`results/fully_explicit_stability.jsonl` — the preprocessing-only run above,
against the unmodified `models/afm.py`.
`experiments/human_plausibility/analyze_mid_gap.py` — the mid-mechanism
sample-splitting analysis (stuck-chain confound, reaction-class breakdown,
cross-variant correlation).
