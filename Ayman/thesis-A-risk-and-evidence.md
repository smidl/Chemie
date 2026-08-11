# Is the heteroscedastic focus risky? — evidence, validation, and a de-risked structure

**Date:** 2026-08-11 · Answers three objections raised against `thesis-A-noise-precision.md`:
(1) heteroscedastic GPs already gave *us* negative results; (2) without a simulator we cannot
separate epistemic from aleatoric, so how is anything validated; (3) is the focus too risky for a
master's thesis.

## 1. The literature *does* have positive evidence — and it is all the same shape

Searched, and the pattern is consistent enough to be the most useful thing in this note.

**Positive result 1 — heteroscedastic BO.** Griffiths, Aldrick, Garcia-Ortegon, Lalchand & Lee,
*Achieving robustness to aleatoric uncertainty with heteroscedastic Bayesian optimisation*,
**Machine Learning: Science and Technology 3(1), 015004 (2022)**, DOI `10.1088/2632-2153/ac298c`
(Crossref-verified; arXiv 1910.07779). They report improvement over homoscedastic BO **and over
random** on toy problems and two real scientific datasets.

**But read what they changed.** They did not merely fit noise better. They introduced two new
acquisition heuristics — a heteroscedastic extension of augmented expected improvement, and
*aleatoric noise-penalised expected improvement* — that **explicitly penalise aleatoric noise in the
suggestion**. And their objective is different: they want inputs that are *robust*, i.e. in
low-noise regions, not merely optimal in the mean.

**Positive result 2 — active label cleaning.** Bernhardt, Castro, Tanno, Schwaighofer, Tezcan,
Monteiro et al., *Active label cleaning for improved dataset quality under resource constraints*,
**Nature Communications 13 (2022)**, DOI `10.1038/s41467-022-28818-3` (Crossref-verified). Prioritising
samples for **re-annotation** by estimated label correctness beats the alternatives under a fixed
budget. Again: the *action* changed — relabel rather than label new — not the surrogate's accuracy.

There is also a survey of exactly this intersection: Mots'oehli & Baek, *Deep Active Learning in the
Presence of Label Noise: A Survey*, arXiv:2302.11075 — a starting point for the literature section.

**The pattern, which resolves your objection rather than dodging it.** Every positive result I could
find comes from **changing what is acquired or optimised**. Every negative result I know of — yours,
and DecisionBO's — comes from **improving the model and leaving the decision rule alone**. That is
the same lesson DecisionBO reached independently: *objective structure matters, model quality does
not.*

This is directly actionable for the thesis:

- **H4 (acquire on the epistemic component only) sits on the side with positive evidence** — it is
  an acquisition change, structurally the same move as ANPEI.
- **H6 (a better-specified estimator improves acquisition) sits on the side with negative
  evidence** — yours. It should be **demoted from a mechanism claim to a pre-registered null**: *we
  expect estimator quality alone not to move the inversion point.* If it does, that contradicts your
  prior result and is worth reporting loudly. If it does not, we have corroborated a real effect at
  a third site.

That inversion of H6 costs nothing and converts your negative experience from a threat into a
pre-registered prediction.

## 2. Validation without a simulator

The objection is right that we cannot observe the epistemic/aleatoric split directly on real data.
But the thesis does not need to.

**On constructed data we have both components exactly**, because we build σ²(x) ourselves on top of a
deterministic function. That *is* the simulator — it just happens to be one we write in an afternoon
rather than a physical model. Its role is to establish the relationship between R and acquisition
performance, and to validate that a given estimator recovers R.

**On real data we can measure the aleatoric component empirically, from replicates.** The sample
variance across repeated measurements at the same input is an unbiased estimate of σ²(x) requiring
no model at all. That gives a model-free ground truth for the denominator's competitor.

**And the epistemic component never needs a ground truth**, because the quantity being validated is
*behavioural*, not latent. The prediction under test is "at this R, uncertainty-guided acquisition
will not beat random" — and whether it beats random is **directly measurable** on the real dataset by
running it. We are validating a prediction about an observable outcome, not estimating a hidden
variable.

**A second model-free check** is available: an estimator's aleatoric head can be validated by
predicting **held-out replicate variance**. That is a genuine, falsifiable test of the decomposition
that needs no simulator.

**What this makes load-bearing.** Replicates. Without them, R on real data can only be bounded, the
aleatoric head cannot be validated, and the real-data arm degrades from a test to an illustration.
**This must be checked in week one, before the proposal is finalised** — if the acid–amine data has
no replicate wells, the real-data testbed should be swapped for a public HTE set that has them.

## 3. Is it too risky? — restructure so the answer is no

The risk is real but it is concentrated in one hypothesis, and the thesis can be ordered so the
uncertain part comes last.

**Layer 1 — descriptive, cannot fail.** *Do real chemistry datasets have input-dependent label
noise, and how much?* Measured from replicates. This either finds heteroscedasticity or does not,
and both answers are informative and, as far as I can tell, unpublished for reaction data. It also
directly determines whether the rest of the thesis is worth doing — and if R turns out to be small
everywhere, **that is itself the answer to the research question**: our AL failures are *not* about
noise structure, and attention moves to the batch confound and to sufficiency.

**Layer 2 — controlled, cannot fail to produce a curve.** The R sweep on constructed noise. A
simulation study always yields a dose–response; the only open question is where the sign change sits
and whether it exists. Even "no inversion up to R = 100" is a clean, quotable result that bounds the
mechanism.

**Layer 3 — the risky part.** Whether epistemic-only acquisition rescues performance, and whether
estimator choice matters. This is where your negative experience predicts a null, and it is
deliberately **last**.

Plus the two prerequisite fixes (batch selection, replication), which are guaranteed results in
their own right by month three.

So the thesis has three independent sources of a defensible contribution before reaching the part
that might not work. That is the definition of an acceptable risk profile for a master's thesis.

## 4. What changes in the proposal

- **H6 becomes a pre-registered null**, with your prior negative cited as the reason for expecting
  it.
- **Layer 1 is promoted to the first results chapter** — the descriptive measurement of R on real
  data, currently buried in the validation step.
- **The framing shifts from "fixing AL" to "deciding whether to run AL".** The diagnostic does not
  require the fix to work. If high-R tasks cannot be rescued, the correct advice is *do not run
  active learning here* — and that is still a useful, defensible deliverable. Arguably a more
  honest one.
