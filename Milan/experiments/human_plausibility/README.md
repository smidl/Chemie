# Does AFM's own scoring agree with the chemist, even when it isn't the top pick?

## Question

AFM's selling point is that its mechanisms are drawn in a chemist-readable
language (curly arrows), not just that it predicts the right product. The
existing check of that (`../../analysis/rmechdb_arrows.py`) only asks whether
the four-move alphabet can *represent* a chemist's curated mechanism at all
(96.68% of RMechDB, see its own results). It says nothing about whether the
*trained model* considers that mechanism any good — a model could find a valid
decomposition and never rank it above chance.

Top-1 exact-match is also the wrong follow-up metric: only 39.2% of the
alphabet-expressible steps match the chemist's specific arrows exactly, and the
rest (60.8%) are chemically equivalent but drawn differently — multiple
arrow-pushings can represent the same electron flow, so "the chemist's arrows"
is one valid rendering, not *the* answer. Demanding the model reproduce that one
rendering exactly conflates "wrong" with "right, drawn another way".

So instead: **is the chemist's mechanism a typical, high-probability answer
under the model's own learned scoring — even when it is not the model's single
top pick?** AFM computes an exact trajectory log-probability for every
mechanism it can consider (`Score.logp` in `models/base.py`), so this is
directly measurable: score the chemist's own move sequence under the trained
model (teacher-forced, not decoded), and see where that score falls inside a
histogram of the same model's own self-generated candidates for the same
reaction.

## Scope

Restricted to RMechDB's **2,057 "exact arrow match" reactions** (of 5,426
curated radical steps; ~39% of the 96.68% that decompose at all) — the ones
where the chemist's curly arrows translate unambiguously into one specific
alphabet move-sequence. For the other 60.8% ("equivalent, drawn differently"),
there is no single canonical move-sequence to call "the chemist's mechanism";
picking one of several equally-valid alternatives would smuggle in a choice the
data itself doesn't make, so those are left out rather than guessed at.

## How much is RMechDB really ground truth here?

Worth keeping in view when reading the result:

- It is curated literature chemistry, not a physical/DFT ground truth — a human
  notational choice about how to draw a mechanism, not verified against
  experimental or computed barriers in this pipeline.
- 121 RMechDB steps (2.2%) have arrows touching no bond-order change the
  bond-electron matrix even represents; 56 (1.0%) break the
  "unmapped-context-is-a-spectator" assumption the whole reduction needs. Both
  already excluded upstream.
- 58.7% of curated steps have an *odd* fish-hook count, structurally
  unreachable by an alphabet that always moves electrons in pairs — not a model
  failure, a representational one (`../../plan.md` §3d,
  `afm-alphabet-limitation-quantified` note).
- Even restricted to the 39.2% "exact match" set used here, that's still one
  curator's rendering of a mechanism a chemist judged sufficient for the
  transformation — not proof no other rendering, or no other mechanism
  entirely, would also be defensible.

None of this invalidates the percentile question above; it bounds how strong a
claim "the human mechanism scores at percentile X" can license.

## Model

`ArrowFlowMatching/outputs/runs/afm_nano/checkpoints/best.ckpt`. Despite the
local folder name, this checkpoint's own saved hyperparameters
(`hyper_parameters['collate_fn']` is a `CollateConstrained`, `emb_dim=128`,
`enc_filter_size=512`) show it is what Milan's own repo calls the
`flower_cons` model at `nano` width — i.e. exactly the AFM architecture
(`configs/model/afm.yaml`'s own docstring: "the same categorical head over the
constrained move alphabet"), at the **same nano width the paper's own headline
comparison table uses** (`ArrowFlowMatching/README.md`: "The comparison table
in the paper uses one run per model at the smallest width, nano"). Not a toy
model built for this check — the smallest rung of the paper's own ladder.

The checkpoint's pickled metadata references a sibling repo
(`models.flower_cons`, Milan's own `MechReact` layout) this checkout doesn't
have; `score_reactions.py`'s `load_model` stubs that module out before
`torch.load` so the (unused) metadata doesn't block reading the state dict, and
then verifies the state dict matches this repo's own `ArrowFlowMatching`
architecture key-for-key (`strict=True`) — if it didn't, that would itself be
worth knowing, and the run would fail loudly rather than silently loading the
wrong weights.

## Input

Per reaction: the reactant SMILES and the chemist's move sequence (RMechDB
atom-map-number space), taken from `../../analysis/rmechdb_arrows.py --dump_targets`
(an additive change to that script — it already computed this internally,
just didn't persist it; see `targets.json`).

## Output

Per reaction: the teacher-forced log-probability of the chemist's mechanism,
and a sample of ~200 of the model's own self-generated trajectory
log-probabilities for the same reactant (`models.afm.ArrowFlowMatching.mapped_candidates`,
unmodified, `decode=sample`). `analyze.py` turns that into a percentile — the
share of the model's own samples the human mechanism matches or beats — and
reports the distribution across the corpus, plus the same statistic restricted
to reactions where the model could actually have drawn more than one distinct
path (a reaction with only one admissible move isn't a discriminating test of
anything).

## Pipeline

```
.venv/bin/python score_reactions.py --num_samples 200      # writes results/scores.jsonl
.venv/bin/python analyze.py                                 # writes results/summary.json, prints the aggregate
```

`score_reactions.py` reuses, rather than reimplements:

- `ArrowFlowMatching/chem.py`'s `mol_from_mapped_smiles` / `atom_types_and_be` —
  the exact functions the training pipeline uses to featurize a molecule.
- `ArrowFlowMatching/models/afm.py`'s `mapped_candidates` (unmodified) for the
  self-generated histogram, and `_score` / `scatter_moves` — the same two calls
  `training_loss` makes — for the teacher-forced human score (summed over the
  whole given path instead of one randomly sampled position; see
  `teacher_forced_score`'s docstring).
- `../../analysis/decompose_steps.py` / `rmechdb_arrows.py`'s own move
  semantics for the name → `(kind, i, j)` translation table, cross-checked
  against `afm.py`'s `DII`/`DJJ`/`DIJ` tables rather than assumed. One subtlety
  caught this way and worth flagging: `move_mask` offers a symmetric move type
  (HOMOLYSIS, COLLIGATION) on the upper triangle only (`i < j`), so translating
  those without re-sorting the pair produced spurious `-inf` scores — fixed in
  `to_model_moves`, not a real model limitation.
- A per-reaction cross-check (`cross_check_featurization`) that the model's own
  BE matrix agrees with `rmechdb_arrows.py`'s independently-built reduced
  matrix before trusting a score; a mismatch (the two scripts handle aromatic
  bonds differently) excludes the reaction rather than silently scoring it
  against the wrong starting state.

## Result, 2026-09-17

Full run, all 2,057 exact-match reactions, `afm_nano`, 200 self-generated
samples per reaction (`results/scores.jsonl`, `results/summary.json`). A first
pass reported this as a single blended percentile, which hid an important
distinction: "the human ranks 1st out of 1 possible mechanism" and "1st out of
11" are very different claims. `analyze.py` now collapses the 200 samples per
reaction to **distinct mechanisms by score** (rounded to 3 d.p., to absorb
float noise between the two independent scoring paths — stable to 2-5 d.p.,
checked) and gives the human mechanism a **rank** among them (1 = the model's
own best; ties go to the human), broken down by how many distinct mechanisms
the model actually produced:

| distinct mechanisms the model drew | # reactions | human ranks 1st (top) | human ranks last (bottom) |
|---|---|---|---|
| 1 (no real choice — not a test) | 1,433 (70%) | 99.9% (trivial) | 99.9% (trivial) |
| 2 | 275 | 97.1% | 2.9% |
| 3 | 81 | 91.4% | 0.0% |
| 4 | 64 | 92.2% | 1.6% |
| 5 | 35 | 85.7% | 0.0% |
| 6-10 | 92 | 92.4% | 0.0% |
| 11+ | 77 | 76.6% | 0.0% |

Across the **624 reactions where the model genuinely had a choice** (>1
distinct mechanism): human ranks 1st (the model's own best) **92.0%** of the
time, and last (the model's own worst) only **1.4%** of the time. The
trend is exactly what you'd want to see, not a flat line: as the model
produces more genuinely distinct alternatives (a harder test — more ways to
rank the human low), the top-1 rate drifts down (97% at 2 alternatives → 77%
at 11+) but never collapses toward chance.

Read together with the caveats above: this is not "the model always agrees
with the chemist" — about 8% of discriminating cases favour a different
mechanism, occasionally the human's own worst — but where AFM's alphabet *can*
express the chemist's mechanism, the trained model overwhelmingly ranks it as
its own best guess, not merely a reachable one, on a `nano`-width checkpoint
never trained on this radical chemistry.

## Caveats specific to this checkpoint

`nano` (1.2M params) is the smallest width in the paper's own ladder, and was
never trained on RMechDB's radical chemistry specifically (USPTO-derived
training split). A low rank is therefore ambiguous by itself: it could mean
the model doesn't generalize to unseen radical chemistry at this scale (not
itself an interpretability failure), or that it prefers a different,
also-valid mechanism over the chemist's specific one (a real interpretability
nuance). The breakdown by number of distinct mechanisms is meant to help
separate "the model had no real choice here" from "the model chose against the
human". 200 samples per reaction is also only a *lower bound* on the model's
true branching factor — a rare alternative mechanism may simply not have been
drawn, so the "11+" row in particular likely undercounts.

## Two further cheap checks, 2026-09-18

Both use `targets.json`/a sibling `multistep.json` and reuse the same
infrastructure; neither needed new compute-heavy work.

### Alphabet composition — does the model reach for the same *kind* of chemistry?

`alphabet_composition.py`. Different question from the rank test above: not
"does the model prefer the human's specific mechanism" but "does it use the
same mix of move types a radical-chemistry corpus actually needs". Tallies
move-kind usage two ways over the same 2,057 reactions: the chemist's own
moves (deterministic, one per reaction) vs. 100 self-generated samples per
reaction from `afm_nano` (`sampled_move_kind_counts`, a direct instrument of
`_rollout`'s own loop, restricted to sample decode where there's no beam
`parent` reindexing to carry through).

| move kind | chemist | model (self-generated) |
|---|---|---|
| LONE_TO_BOND | 0.0% | 3.5% |
| BOND_TO_LONE | 0.0% | 3.7% |
| HOMOLYSIS | 40.5% | 37.5% |
| COLLIGATION | 59.5% | 55.2% |

RMechDB is exclusively radical chemistry, so the chemist never draws the
polar-flavoured moves (LONE_TO_BOND/BOND_TO_LONE) at all. The model's full
generative distribution puts only ~7% of its mass there — close to the
chemist's 0%, not evenly spread across all four kinds (25% each would be the
"no domain awareness" null). A small early run on 20 reactions showed a much
larger gap (~40% polar moves); that was small-sample noise, not the real
number — worth remembering before trusting any composition statistic computed
on a handful of reactions.

### Intermediate stability — are alphabet-admissible intermediates chemically sane?

`intermediate_stability.py`. The paper's own flagged limitation: the mask
guarantees every intermediate is *valence-representable*, not that it's
*chemically plausible* -- real evidence needs DFT (the not-yet-launched
`specialty_11` NEB line). A cheap proxy needing no checkpoint at all: walk the
chemist's own *admissible* move sequence and check whether RDKit can even embed
each intermediate in 3D and locally minimize it with a standard force field. A
structure that fails there is a bad DFT starting point regardless of what the
valence mask says.

Needed a real bug fix first: `rmechdb_arrows.py`'s `decompose()` found a valid
move *multiset* and order via `order_component`, but then stored the moves in
their original unordered slot sequence, not the validated order --
harmless for the existing multiset-based (`Counter`) comparisons, but wrong to
execute step-by-step. Fixed by storing `order_component`'s own validated
permutation instead (`analysis/rmechdb_arrows.py`, `decompose()`). Caught
because the very first multi-move reaction tried threw `AtomValenceException`
building an intermediate that never should have been reachable in that order.
Did not affect the rank-based result above -- every one of its 2,057 targets
is a single move, where order can't be wrong.

Run on 2,814 reactions with a genuine ≥2-move admissible decomposition (a new
`--dump_multistep` flag on `rmechdb_arrows.py`, same additive pattern as
`--dump_targets` -- any admissible decomposition, not necessarily matching the
curated arrows, since this tests the alphabet's intermediates, not human
agreement):

|                        | n     | embeds in 3D | force-field converges |
|------------------------|-------|--------------|------------------------|
| mid-mechanism intermediates | 3,136 | 100.0%   | 98.0%                  |
| final products              | 2,775 | 100.0%   | 98.2%                  |

2,775 of 2,814 reactions (98.6%) reconstructed cleanly end to end; the rest hit
a real chemistry edge case (unkekulizable aromatics, valence-table extent) and
were excluded rather than forced. Headline: by this proxy, intermediates are
indistinguishable from final products -- no sign that the mask's valence-only
guarantee is quietly admitting strained or pathological states. This is not a
DFT-quality energy and can't rule out a real barrier problem the earlier
`specialty_11` line is built to catch (RDKit force fields don't know about
transition states); it's a cheap filter that found nothing to filter, which is
itself useful before spending real compute.

> **Superseded, 2026-09-18 — read the section after the DiscreteFlowER control
> below first.** This result and the DiscreteFlowER section right after it
> never touched `afm_nano`'s trained weights: they walked an *algorithmically*
> validated path (`decompose_steps.py`'s own combinatorial search, which
> enforces a per-element valence cap at every step). Once the actual trained
> model's own self-generated mechanisms were tested, the conclusion reverses —
> see "Corrected comparison" below. Left in place, not deleted, because the
> reversal and why it happened is itself the finding.

## Does the valence mask actually matter? DiscreteFlowER baseline, 2026-09-18

**Superseded below — same caveat as above: this compares an algorithmic AFM
path against DiscreteFlowER's real model, not trained model vs. trained
model. Read "Corrected comparison" for the fair version.**

The intermediate-stability result above is consistent with AFM's mask doing
real work — but also consistent with "a cheap force-field check passes on
almost anything small enough to look like a molecule regardless of how it was
built." The control: `flower_discrete_stability.py` runs the same proxy on
`flower_discrete_nano` (`DiscreteFlowER`, same body, same bond-electron-matrix
representation, same paper) — a model with **no admissibility guarantee on its
intermediates at all**. Each Euler step just resamples a random subset of
matrix entries toward the model's guessed endpoint, with nothing masking off a
chemically nonsensical partial state. It has no move alphabet, so there's no
chemist path to walk it through; each reactant instead gets 3 of the model's
own self-generated chains (`multistep.json`'s 2,814 reactants, all 9
intermediate + 1 final step of each `flow_steps=10` chain scored).

Reported in three tiers instead of two, because the dominant failure mode here
turned out to be a different one than for AFM: does the state even
**reconstruct** to a valid molecule at all (impossible to fail for AFM, by
construction), and only then, does it embed / does the force field converge:

| | n | reconstructs at all | embeds (of those) | FF-converges (of those) |
|---|---|---|---|---|
| **DiscreteFlowER**, mid-mechanism | 75,978 | 47.5% | 100%¹ | 98.7%¹ |
| **DiscreteFlowER**, final products | 8,442 | 41.6% | 100%¹ | 98.8%¹ |
| **AFM**, mid-mechanism (recap) | 3,136 | 100.0% | 100.0% | 98.0% |
| **AFM**, final products (recap) | 2,775 | 100.0% | 100.0% | 98.2% |

¹ as a percentage of the ones that reconstructed at all, i.e. 47.5%×100% of
all DiscreteFlowER mid-mechanism states actually embed, not 100% of all of
them — the table's own raw percentages were of the full count; recomputed here
relative to the "reconstructs" subset for direct comparison to AFM's rows.

**This is the finding the ablation was built to check for, not a wash.**
Whenever a DiscreteFlowER intermediate happens to reconstruct at all, it is
essentially always embeddable and force-field-stable — indistinguishable from
AFM there. The entire gap is at the first, structural tier: more than half of
DiscreteFlowER's intermediates (52.5% mid-mechanism, 58.4% even at the final
step) are not valid molecules *at all*, something AFM's mask makes impossible
by construction. So the earlier "AFM's intermediates are stable" result was
not just the cheap proxy being uniformly lenient — a real, differently-behaved
model on the same chemistry, same representation, same width, fails this exact
test at a >50% rate.

Caveat: `nano`-width, single (untuned) 10-step Euler schedule, no retry/repair
— this is not the paper's own full-scale validity number for FlowER-family
models (which is measured differently, at full width, in the comparison
table). It is, however, the same conditions AFM was tested under in this
experiment, which is what makes it a fair control rather than a mismatched one.

## Corrected comparison: what happens when the trained models actually generate, 2026-09-18

Prompted by a good question: is the AFM row above teacher-forced along the
*chemist's* route? No — the exact-match (human-verified) set turned out to
have zero multi-move reactions, so it was walked along `multistep.json`'s
*algorithmic* decomposition instead, using `scatter_moves` directly with no
model in the loop at all. Two follow-ups closed the gap: run `afm_nano`'s own
trained rollout the same way DiscreteFlowER's was tested (self-sampled,
`score_reactions.sampled_intermediates`, new), and add a model-free entrywise-
interpolation-toward-the-true-product control
(`entrywise_interpolation_stability.py`, new) to separate "bad model" from
"bad representation" for DiscreteFlowER's number.

| | mid-mechanism reconstructs | final reconstructs |
|---|---|---|
| AFM, algorithmic path (no weights, the old "Result" above) | 100.0% | 100.0% |
| **AFM, real trained model (self-sampled)** | **21.6%** | 47.4% |
| DiscreteFlowER, real trained model (self-sampled) | 47.5% | 41.6% |
| Entrywise interpolation toward the *true* product (no model) | 64.7% | 100.0%¹ |

¹ by construction.

**AFM's actual trained model is less stable at intermediate states than
DiscreteFlowER's — the opposite of the earlier headline.** Traced to source:
`models/afm.py`'s `move_mask`, checked at *every* step, only enforces generic
element-agnostic bounds (`MAX_DIAG=14`, `MAX_BETA=12`); real per-element
valence (`local_table()`) is enforced once, only at the **stop** decision
(`stop_mask`). The model is free to wander through states where, say, a carbon
sits at bonding count 6 — globally representable, not a real carbon — for as
long as it likes, as long as it returns to a per-element-valid state before
stopping. `nano`'s learned policy uses that slack heavily.

Concrete evidence of the wandering, from the same self-sampled chains:
- Chains average **3.84 moves**, vs. **2.13** for the algorithmic minimal
  decomposition of the same reactants — ~80% longer than necessary.
- **16.2% of chains hit `max_moves=12` without ever finding a state the model
  will stop from.**
- Invalid steps are usually a single-step blip immediately followed by a
  valid one (4,191 of the observed runs are length 1 — a real, self-correcting
  overshoot) — but a second population never corrects: runs of length 11-12
  (629+347 occurrences) account for most of the budget-exhausted chains.

Row 4 puts a floor under row 3: even guided by the *true* answer, pure
entrywise resampling produces an invalid intermediate about a third of the
time (representation cost), and DiscreteFlowER's actual rate (47.5%) is worse
than that floor (model-quality cost on top). AFM's shortfall, by contrast, is
*entirely* a model/training-scale story: the representation itself, walked
strictly, hits 100% (row 1) — this `nano` checkpoint's move policy just
doesn't make full use of the guarantee the architecture can provide.

**What this does and does not say.** It does not show AFM's construction is a
worse idea than DiscreteFlowER's — the architecture's ceiling (row 1) is still
the strongest result in the table, and rows 2-4 are all `nano`, single-seed,
untuned-schedule numbers. It does say the earlier "~100%, indistinguishable
from final products" framing measured the alphabet's best case, not what this
trained checkpoint actually does when left to generate on its own — and that
distinction is worth having before anyone relies on the original framing.

## Why is final reconstruction so low, and would the paper have caught this?

Split AFM's self-sampled chains by whether they actually found a state worth
stopping from:

| | n | final reconstructs |
|---|---|---|
| Chains that hit `max_moves=12` without ever stopping | 1,324 | 0.7% |
| Chains that legitimately stopped (`stop_mask` said yes) | 6,826 | 56.5% |

The budget-exhausted 16.2% fail almost universally, as expected. The bigger
surprise: **43.5% of legitimate stops — where the model's own per-element
table said the state is a real molecule — still fail RDKit's sanitizer.**
Sampling 170 such cases and reading the raw error directly (not guessing):
88 of them (52%) are a plain `AtomValenceException` — real over-valence (one
concrete case: a carbon at `local_table()`-admissible (diag=0, beta=3) that
RDKit reports as explicit valence 6) — not the aromaticity/kekulization edge
case `_emit`'s own docstring flags. `stop_mask`'s table and RDKit's actual
valence rules disagree on a real slice of states.

**Was any of this tested in the paper? No — traced to why, not just
"probably not."** `models/afm.py`'s `_emit()`, used inside `mapped_candidates`
(the same path `eval.py`'s reported numbers come from), replaces any
candidate that fails to reconstruct with **the unchanged reactant** before any
metric sees it. The reactant always reconstructs, so a generation failure
becomes "predicted no reaction," which passes validity and every conservation
check and only costs step accuracy. This same `afm_nano` checkpoint reports
`validity_micro_top1: 1.0` on its own standard (USPTO-derived) test split
(`analysis/results/calib_afm_nano.json`) — a split RMechDB's radical
chemistry was never part of to begin with. The paper's validity metric cannot
surface this failure mode by construction, independent of whether anyone
thought to look.
