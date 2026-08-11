# Thesis Proposal — proposed content

*Follows the SW-1 template (v14.0, 23.07.2026); headings and numbering match it. Target 8–10 pages.
Supporting background is in the companion `thesis-A-*.md` files in this folder.*

---

## 1. Working Title

**The Effect of Noise-Model Assumptions on the Quality of Active Learning: A Sensitivity Study on
Chemical Reaction Data**

*Alternatives:* "How Much Does the Noise Model Matter in Active Learning?"; "Noise-Model
Mis-specification and the Failure of Uncertainty-Guided Acquisition".

## 2. Abstract

Active learning tries to cut the number of labels a model needs by choosing what to label instead of
sampling at random. Results in chemistry are inconsistent: some studies report clear gains, others
find no difference from random selection, and there is no accepted explanation for the split.

Nearly every active-learning method assumes something about how labels are corrupted — a *noise
model*. The usual assumption is the simplest one: independent, identically distributed, Gaussian
noise of constant size. Real measurements break all three parts of it.

This thesis asks how much that matters. It varies the true noise structure — how it depends on the
input, how heavy its tails are, and how strongly it correlates between measurements — while keeping
the learner's assumed model fixed, and measures what happens to active-learning performance relative
to random sampling. One prediction is examined closely: that input-dependent noise makes
uncertainty-guided acquisition pick the *least reliably measured* examples, and so perform worse
than random.

The noise structure of real high-throughput chemistry datasets is also characterised from replicate
measurements. The expected result is a sensitivity map: which noise assumptions matter, which do
not, and when active learning is worth its overhead.

## 3. Introduction

**Background.** Labels are the bottleneck in scientific machine learning. One high-throughput
measurement consumes reagent and instrument time; one first-principles calculation can consume
hours. Active learning attacks this by letting the model pick what to label, usually where its
predictive uncertainty is largest.

**The overlooked assumption.** Predictive uncertainty is not observed — it is produced by a model
that assumes how observations are corrupted. The default is noise that is independent, identically
distributed, Gaussian and of constant size. Experimental chemistry data is none of these:
reliability varies between reactions, gross errors happen, and measurements on the same plate share
systematic error.

**Academic relevance.** Theory says the advantage of adaptive over random sampling depends on the
noise regime and can vanish completely. The empirical literature mostly reports outcomes without
mentioning noise at all, which may be why similar studies disagree.

**Practical relevance.** Active learning costs something: uncertainty estimates, retraining between
rounds, a sequential workflow. Knowing in advance whether that pays off is worth having.

**Structure.** Section 4 states the gap, 5 the objectives, 6 the questions and hypotheses, 7 the
literature, 8 the method, 9–10 expected results and contribution, 11–13 plan, resources, references.

## 4. Problem Statement

**What is not known.** Which departures from the standard noise assumption actually degrade active
learning, by how much, and whether any can reverse its advantage. Also unknown: what noise structure
real reaction datasets have.

**Why it matters.** Without this, a negative active-learning result cannot be read. The failure could
be the uncertainty estimator, the acquisition rule, the batch construction, or the data — and these
are not currently separable. Every new dataset becomes a gamble.

**Who is affected.** Anyone spending a fixed budget on expensive labels: experimental laboratories,
computational campaigns, and active-learning users working with noisy measurements.

**Consequences.** Budgets go to machinery that may not help; contradictory benchmarks accumulate;
methods built on idealised noise get deployed where the idealisation fails.

## 5. Research Objectives

1. **Correct** two defects in the available implementation — batch selection with no diversity term,
   and too few repeats of the initial labelled set — so later comparisons can be interpreted.
2. **Characterise** the noise structure of real reaction datasets from replicate measurements:
   input-dependence, tail behaviour, and within-batch correlation.
3. **Measure** how sensitive active learning is to controlled departures from the standard noise
   assumption, using constructed noise where the truth is known exactly.
4. **Test** whether input-dependent noise inverts the advantage of uncertainty-guided acquisition,
   and whether acquiring on the reducible component only prevents that.

## 6. Research Questions and Hypotheses

**RQ1.** Which departures from i.i.d. constant-variance Gaussian noise affect active-learning
performance, and which do not?

**RQ2.** What noise structure do real reaction datasets have?

**RQ3.** Under which departures, if any, does uncertainty-guided acquisition become *worse* than
random rather than merely equal to it?

Hypotheses are grouped by axis, each with a stated prior expectation.

**Axis A — variance structure.**
- **H1 (control).** Under constant-variance noise, ranking is unaffected; any loss comes from the
  lower attainable error floor, not from acquisition.
- **H2.** Under input-dependent noise the advantage falls monotonically with R, the ratio of
  irreducible to reducible variation across the pool.
- **H3.** Above some R the advantage **changes sign** — acquisition starts picking the worst-measured
  points.
- **H4.** Acquiring on the estimated *reducible* component only prevents the inversion, as far as the
  decomposition is accurate.

**Axis B — tail behaviour.**
- **H5.** Under heavy-tailed noise, acquisition chases outliers; the damage scales with the
  contamination fraction, not the nominal variance.

**Axis C — dependence.**
- **H6.** When measurements in a batch share error, the information gained from a batch is
  overestimated, compounding with the defect in Objective 1.

**Axis D — estimator (pre-registered null).**
- **H7.** Improving only the *estimator* — e.g. swapping a constant-variance Gaussian process for one
  with input-dependent noise, acquisition unchanged — does **not** change the outcome. Registered as
  a null in advance: earlier unpublished experiments in the host group, and a parallel study, both
  found better noise modelling did not improve downstream decisions, and the published successes came
  from changing *what is acquired* instead. A positive result would contradict that and be reported.

## 7. Preliminary Literature Review

**Theory.** Classical results tie the advantage of adaptive over passive sampling to
problem-dependent quantities including the noise regime, with the advantage vanishing in the
high-noise limit. Batch acquisition is governed by submodularity of information — a set of queries is
worth less than the sum of its members, so picking the *k* top-scoring points is known to be
suboptimal (Kirsch, van Amersfoort & Gal, 2019). Splitting predictive uncertainty into an
irreducible (*aleatoric*) and a reducible (*epistemic*) part underpins Axis A: only the second can be
removed by labelling.

**Findings.** Uncertainty estimation for molecular properties has been benchmarked, with wide
variation between scalable methods (Scalia, Grambow, Pernici, Li & Green, 2020). Active-learning
pipelines evaluated under distribution shift beat random on learning-curve area in all fourteen
slices tested but on the final precision–recall metric in only nine (Yin, Gao, Panapitiya &
Saldanha, 2026) — the metric changes the answer. Bayesian deep learning with several uncertainty
estimators has been applied to reaction feasibility on high-throughput data (Zhong et al., 2025),
which supplies the experimental testbed here.

**A pattern in the successes.** Where noise-aware methods have helped, the gain came from changing
*what is acquired*, not from fitting noise better. Heteroscedastic Bayesian optimisation beat both
its homoscedastic counterpart and random sampling by adding acquisition rules that explicitly
penalise aleatoric noise (Griffiths, Aldrick, Garcia-Ortegon, Lalchand & Lee, 2022). Active label
cleaning won under a fixed budget by re-annotating suspect labels rather than acquiring new ones
(Bernhardt et al., 2022). A survey covers the label-noise case (Mots'oehli & Baek, 2023). This is why
Axis A and Axis D are separated, and why Axis D is a null.

**Gap.** The literature benchmarks active learning but does not test its sensitivity to the noise
assumptions it rests on, and rarely reports the noise structure of the data used.

**Fit.** Here the noise model is the independent variable, not a fixed background assumption.

## 8. Methodology

**Design.** Quantitative and computational, in two parts: a descriptive study of real data, then a
controlled simulation with known ground truth. The first says which regions of the second matter.

**Data.** No new data is collected.
- **Deterministic** computed reaction barriers as a noise-free base for constructed noise (BH9 —
  Prasad et al., 2022 — plus a larger deterministic set for scale).
- **Real experimental** high-throughput reaction data with genuine measurement noise (Zhong et al.,
  2025).
- A **public experimental** dataset for comparability (Perera et al., 2018).

**Part 1 — descriptive.** From replicate measurements, estimate how variance depends on the input,
how heavy the residual tails are, and how strongly error correlates within a batch. Replicates are
required; without them these can be bounded but not measured, which is stated as a limitation.

**Part 2 — controlled.** A factorial design crossing true noise structure (Axes A–C, each swept
through a range that includes the standard assumption as a control) with acquisition target (total
predictive uncertainty, reducible only, irreducible only) and uncertainty estimator. Because noise is
constructed on a deterministic base, both components are known exactly, which also allows the
estimators themselves to be checked.

**Sampling.** Repeated randomised simulations, with the initial labelled set drawn independently
across both strategy and repeat so the comparison is not confounded with one shared draw. At least
20 repeats per configuration; the final count set by a power calculation on pilot runs.

**Analysis.** Primary outcome: difference in learning-curve area against random selection, with
bootstrap confidence intervals over matched repeats. Sensitivity is the change in that difference per
unit change along each axis — reported also where it is indistinguishable from zero. Where a sign
change is predicted, hypotheses are separated by the sign of the interval, not by significance alone.
Secondary: final error and calibration.

**Ethics.** No human participants, personal data or animals. All datasets are published and used
under their licences. Computation reuses existing labels, so energy cost is modest.

**Limitations.** Constructed noise is a model of real noise; mitigated by informing it with Part 1 and
testing more than one form per axis. Results hold for one task family and one model class, with no
claim beyond that. Part 1 depends on replicates being available.

## 9. Expected Results

- A **sensitivity map**: the effect of each noise axis on active-learning performance, with
  confidence intervals — including axes where the effect is negligible, which are equally informative.
- A **null under constant-variance noise** (H1), showing where the problem is not.
- A **dose–response curve** for input-dependent noise, and whether an inversion occurs (H3).
- A **characterisation of noise in real reaction data**, apparently not previously reported, which
  says whether the regimes tested are practically relevant.
- A **corrected baseline** showing how much of an earlier null result came from batch selection
  rather than the data. That null may reverse once the defect is removed; this is expected, not a
  failure.

## 10. Expected Contribution

**Academic.** A systematic sensitivity analysis of active learning with respect to its own noise
assumptions — missing from a literature that reports outcomes without reference to noise. The method
transfers to other domains with noisy oracles.

**Practical.** Guidance on when active learning repays its overhead, based on a dataset property
measurable in advance from replicates. For a laboratory weighing up a sequential workflow, that turns
a judgement call into a check.

**Methodological.** Two reusable corrections — diversity-aware batch selection, and correct
replication of the initial design — with a measurement of how much each changes the conclusion.

## 11. Preliminary Table of Contents and Timeline

| # | Chapter | Months |
|---|---|---|
| 1 | Introduction | 1 |
| 2 | Background and related work | 1–2 |
| 3 | Methods: testbeds, noise models, acquisition strategies, statistics | 2–3 |
| 4 | Results I: correcting the baseline | 3–4 |
| 5 | Results II: noise structure of real reaction data | 4 |
| 6 | Results III: sensitivity to each noise axis | 4–5 |
| 7 | Results IV: the input-dependent case, and whether it can be fixed | 5–6 |
| 8 | Discussion, limitations, future work | 6 |
| 9 | Conclusion | 6 |

**Risk structure.** Ordered so the uncertain work is last, with three defensible results before it.

- *Month 3* — corrected baseline and fixed statistics. Guaranteed, whatever follows.
- *Month 4* — noise structure of real data. Descriptive, cannot fail, and sets the emphasis for
  Chapter 6.
- *Month 5* — the sensitivity map. A factorial always produces a result, including the useful finding
  that active learning is robust to some axes.
- *Month 6* — the mitigation question, the only genuinely uncertain part.

## 12. Required Tools and Resources

- **Datasets:** all listed above are already accessible; nothing new to acquire.
- **Software:** Python; PyTorch or JAX; RDKit; scikit-learn; standard scientific libraries. An
  existing implementation of several uncertainty estimators and acquisition strategies serves as the
  starting point.
- **Compute:** cluster access with batch submission. Requirements are modest — repeated training of
  small models, not first-principles calculation. **The account and group membership should be
  arranged at the start, not when first needed.**
- **Supervision:** access to earlier results and to parallel studies whose methodological standards
  are adopted here.

## 13. Preliminary References

*Verified against Crossref or arXiv metadata. APA style.*

1. Bernhardt, M., Castro, D. C., Tanno, R., Schwaighofer, A., Tezcan, K. C., Monteiro, M., et al.
   (2022). Active label cleaning for improved dataset quality under resource constraints. *Nature
   Communications, 13*. https://doi.org/10.1038/s41467-022-28818-3
2. Griffiths, R.-R., Aldrick, A. A., Garcia-Ortegon, M., Lalchand, V., & Lee, A. A. (2022).
   Achieving robustness to aleatoric uncertainty with heteroscedastic Bayesian optimisation.
   *Machine Learning: Science and Technology, 3*(1), 015004.
   https://doi.org/10.1088/2632-2153/ac298c
3. Kirsch, A., van Amersfoort, J., & Gal, Y. (2019). *BatchBALD: Efficient and diverse batch
   acquisition for deep Bayesian active learning*. arXiv:1906.08158.
4. Mots'oehli, M., & Baek, K. (2023). *Deep active learning in the presence of label noise: A
   survey*. arXiv:2302.11075.
5. Perera, D., Tucker, J. W., Brahmbhatt, S., Helal, C. J., Chong, A., Farrell, W., Richardson, P.,
   & Sach, N. W. (2018). A platform for automated nanomole-scale reaction screening and
   micromole-scale synthesis in flow. *Science, 359*(6374), 429–434.
   https://doi.org/10.1126/science.aap9112
6. Prasad, V. K., Pei, Z., Edelmann, S., Otero-de-la-Roza, A., & DiLabio, G. A. (2022). BH9, a new
   comprehensive benchmark data set for barrier heights and reaction energies. *Journal of Chemical
   Theory and Computation, 18*(1), 151–166. https://doi.org/10.1021/acs.jctc.1c00694
7. Scalia, G., Grambow, C. A., Pernici, B., Li, Y.-P., & Green, W. H. (2020). Evaluating scalable
   uncertainty estimation methods for deep learning-based molecular property prediction. *Journal of
   Chemical Information and Modeling, 60*(6), 2697–2717. https://doi.org/10.1021/acs.jcim.9b00975
8. Yin, T., Gao, P., Panapitiya, G., & Saldanha, E. G. (2026). Out-of-distribution evaluation of
   active learning pipelines for molecular property prediction. *RSC Advances, 16*, 5281–5295.
   https://doi.org/10.1039/d5ra08055j
9. Zhong, H., Liu, Y., Sun, H., Liu, Y., Zhang, R., Li, B., Yang, Y., & Huang, Y. (2025). Towards
   global reaction feasibility and robustness prediction with high-throughput data and Bayesian deep
   learning. *Nature Communications, 16*. https://doi.org/10.1038/s41467-025-59812-0

**Three to nine more needed.** The template asks for 10–20; the nine above have confirmed metadata.
Do **not** complete the list from memory or from search snippets — author lists in this area are
often garbled by secondary sources, and one attribution in an earlier draft was wrong until checked.
Verify each via Crossref (by DOI) or the arXiv API. Still to cover: a general active-learning survey;
theory on when adaptive sampling lowers label complexity; rates under noise conditions; Bayesian
active learning by disagreement; Monte-Carlo dropout and deep ensembles; the aleatoric/epistemic
split; robust regression under heavy tails; and the deterministic reaction dataset, cited to its own
paper.
