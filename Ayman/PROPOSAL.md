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

Nearly every active-learning method assumes something about how labels are corrupted — a noise
model. The usual assumption is the simplest one: independent, identically distributed, Gaussian
noise of constant size. Real measurements break all three parts of it.

This thesis asks how much that matters. It varies the structure of the noise in the data while
keeping the learner's assumed noise model fixed, and measures what happens to active-learning
performance relative to random sampling. One prediction is examined closely: that noise which varies
across the input space makes uncertainty-guided acquisition pick the least reliably measured
examples, and so perform worse than random.

The noise structure of real high-throughput chemistry datasets is also characterised from replicate
measurements. The expected result is a sensitivity map: which noise assumptions matter, which do
not, and when active learning is worth its overhead.

## 3. Introduction

Labels are the bottleneck in scientific machine learning. A single high-throughput measurement
consumes reagent and instrument time, and a single first-principles calculation can consume hours of
computing. Active learning attacks this by letting the model choose what to label next, usually
picking the examples where its predictive uncertainty is largest.

That uncertainty is not observed. It is produced by a model that assumes something about how
measurements are corrupted, and the assumption is almost always the simplest available: noise that
is independent between measurements, identically distributed, Gaussian, and of constant size across
the input space. Experimental chemistry data satisfies none of these. Some reactions are measured
far more reliably than others, occasional gross errors occur, and measurements sharing a plate share
systematic error.

This matters academically because theory ties the advantage of adaptive over random sampling to the
noise regime, and shows that the advantage can vanish entirely. Yet the empirical literature
generally reports outcomes without reference to noise at all, which may explain why comparable
studies reach opposite conclusions. It matters practically because active learning is not free: it
requires uncertainty estimates, retraining between rounds, and a sequential workflow. Knowing in
advance whether that overhead will repay itself is directly useful to anyone planning a measurement
campaign.

The remainder of the proposal sets out the gap (Section 4), the objectives (5), the questions and
hypotheses (6), the relevant literature (7), the method (8), the expected results and contribution
(9 and 10), and the plan, resources and references (11 to 13).

## 4. Problem Statement

It is not known which departures from the standard noise assumption actually degrade active
learning, by how much, or whether any of them can reverse its advantage rather than merely remove
it. It is also not established what noise structure real chemical reaction datasets have, since
this is rarely reported.

The gap matters because without it a negative active-learning result cannot be interpreted. A
failure might come from the uncertainty estimator, from the acquisition rule, from the way batches
of queries are selected, or from the data itself, and these possibilities are not currently
separable. Each new dataset therefore becomes an independent gamble, and negative findings are
difficult to publish because they cannot be distinguished from implementation error.

Those affected are anyone spending a fixed budget on expensive labels: experimental laboratories
running screening campaigns, groups running first-principles calculations, and more generally any
user of active learning working with noisy measurements. Left unaddressed, budgets continue to be
committed to machinery that may not help, contradictory benchmark results continue to accumulate
without an organising variable, and methods developed under idealised noise assumptions continue to
be deployed where those assumptions fail.

## 5. Research Objectives

1. **Correct** two known defects in the available implementation — batch selection with no diversity
   term, and too few repeats of the initial labelled set — so that later comparisons can be
   interpreted.
2. **Characterise** the noise structure of real reaction datasets from replicate measurements.
3. **Measure** how sensitive active learning is to controlled departures from the standard noise
   assumption, using constructed noise where the truth is known exactly.
4. **Test** whether acquiring on the reducible part of uncertainty alone makes active learning
   robust to those departures.

## 6. Research Questions and Hypotheses

**RQ1.** Which properties of label noise affect the performance of active learning relative to
random sampling, and which do not?

**RQ2.** What noise structure do real chemical reaction datasets have?

**RQ3.** Under which conditions, if any, does uncertainty-guided acquisition become worse than
random rather than merely equal to it?

- **H1.** The *structure* of the noise, not its magnitude, determines whether active learning
  outperforms random sampling. Noise of constant size leaves the ranking of candidates unchanged and
  therefore does not harm acquisition, although it lowers the error that any method can reach.
- **H2.** Where noise varies systematically across the input space, the advantage of
  uncertainty-guided acquisition falls, and beyond some point it changes sign: acquisition begins to
  select the least reliably measured examples and performs worse than random.
- **H3.** Acquisition targeting only the reducible part of predictive uncertainty is more robust to
  noise structure than acquisition on total uncertainty, to the extent that the two parts can be
  separated accurately.
- **H4 (pre-registered null).** Improving the noise model alone, while leaving the acquisition rule
  unchanged, does not improve outcomes. This is stated as a null in advance because earlier
  unpublished experiments in the host group, and a parallel study, both found that better noise
  modelling did not improve downstream decisions, while the published successes in this area came
  from changing what is acquired instead. A positive result would contradict that and be reported
  as such.

## 7. Preliminary Literature Review

Classical results tie the advantage of adaptive over passive sampling to problem-dependent
quantities including the noise regime, with the advantage vanishing in the high-noise limit. Batch
acquisition is governed by the submodularity of information: a set of queries is worth less than the
sum of its members, so selecting the individually highest-scoring points is known to be suboptimal
(Kirsch, van Amersfoort & Gal, 2019). Splitting predictive uncertainty into an irreducible
(aleatoric) and a reducible (epistemic) part underpins H3, since only the second can be removed by
labelling.

Empirically, uncertainty estimation for molecular properties has been benchmarked, with wide
variation between scalable methods (Scalia, Grambow, Pernici, Li & Green, 2020). Active-learning
pipelines evaluated under distribution shift beat random selection on learning-curve area in all
fourteen slices tested, but on the final precision–recall metric in only nine (Yin, Gao, Panapitiya
& Saldanha, 2026), so even the choice of metric changes the answer. Bayesian deep learning with
several uncertainty estimators has been applied to reaction feasibility on high-throughput data
(Zhong et al., 2025), and supplies the experimental testbed used here.

A pattern runs through the successful noise-aware methods. Where they have helped, the gain came
from changing what is acquired rather than from fitting the noise more accurately. Heteroscedastic
Bayesian optimisation beat both its constant-variance counterpart and random sampling by adding
acquisition rules that explicitly penalise aleatoric noise (Griffiths, Aldrick, Garcia-Ortegon,
Lalchand & Lee, 2022), and active label cleaning won under a fixed budget by re-annotating suspect
labels rather than acquiring new ones (Bernhardt et al., 2022). A survey covers the label-noise case
more broadly (Mots'oehli & Baek, 2023). This pattern is why H3 and H4 are separated, and why H4 is
stated as a null.

The gap is that this literature benchmarks active learning without testing its sensitivity to the
noise assumptions it rests on, and rarely reports the noise structure of the data used. This thesis
treats the noise model as the variable under study rather than as fixed background.

## 8. Methodology

The work is quantitative and computational, in two parts: a descriptive study of real experimental
data, followed by a controlled simulation study in which the ground truth is known. The first
determines which regions of the second are practically relevant.

No new data is collected. Three existing sources are used: a deterministic set of computed reaction
barriers as a noise-free base for constructed noise (Prasad et al., 2022, with a larger deterministic
set for scale); real high-throughput reaction data carrying genuine measurement noise (Zhong et al.,
2025); and a public experimental dataset for comparability (Perera et al., 2018).

The descriptive part estimates, from replicate measurements, how the variance of a measurement
depends on the reaction, how heavy the tails of the residuals are, and how strongly errors correlate
within an experimental batch. These three properties are the ways in which real noise departs from
the standard assumption, and they define what is varied in the second part. Replicates are required
for this; where they are unavailable the properties can be bounded but not measured, which is stated
as a limitation rather than worked around.

The controlled part is a factorial design. Noise with each of those three structures is constructed
on top of the deterministic dataset and swept through a range that includes the standard assumption
as a control, and crossed with the acquisition target — total predictive uncertainty, the reducible
component alone, or the irreducible component alone — and with the uncertainty estimator. Because
the noise is constructed, both of its components are known exactly, which also allows the estimators
themselves to be checked against the truth.

Each configuration is run as a repeated randomised simulation, with the initial labelled set drawn
independently for every strategy and every repeat so that the comparison between strategies is not
confounded with the variance of a single shared draw. At least twenty repeats per configuration are
planned, with the final number fixed by a power calculation on pilot runs.

The primary outcome is the difference in learning-curve area between an acquisition strategy and
random selection, reported with bootstrap confidence intervals over matched repeats. Sensitivity is
the change in that difference per unit change along each noise property, and is reported also where
it cannot be distinguished from zero. Where a change of sign is predicted, hypotheses are separated
by the sign of the interval rather than by significance alone. Final model error and the calibration
of the uncertainty estimates are recorded as secondary outcomes.

No human participants, personal data or animals are involved. All datasets are published and used
under their licences, and the computation reuses existing labels rather than generating new
calculations, so the energy cost is modest.

The main limitation is that constructed noise is a model of real noise and may not reproduce its
structure; this is mitigated by informing the constructions with the descriptive results and by
testing more than one form of each property. Findings will hold for one task family and one model
class, and no claim beyond that will be made.

## 9. Expected Results

- A sensitivity map showing the effect of each noise property on active-learning performance, with
  confidence intervals, including properties where the effect turns out to be negligible.
- A null result under noise of constant size (H1), showing where the problem is not.
- A curve describing how the advantage falls as noise structure varies, and a determination of
  whether it changes sign (H2) and where.
- A characterisation of the noise in real reaction data, apparently not previously reported, which
  establishes whether the regimes tested are practically relevant.
- A corrected baseline showing how much of an earlier null result came from batch selection rather
  than from the data. That null may reverse once the defect is removed; this is anticipated, and is
  not a failure of the study.

## 10. Expected Contribution

Academically, the work provides a systematic sensitivity analysis of active learning with respect to
its own noise assumptions, which is missing from a literature that reports outcomes without
reference to noise. The method transfers to other domains with noisy oracles.

Practically, it offers guidance on when active learning repays its overhead, based on a property of
the dataset that can be estimated in advance from replicate measurements. For a laboratory weighing
up a sequential experimental workflow, that turns a judgement call into a check.

Methodologically, it delivers two reusable corrections — diversity-aware batch selection, and
correct replication of the initial design — together with a measurement of how much each of them
changes the conclusion.

## 11. Preliminary Table of Contents and Timeline

| # | Chapter | Months |
|---|---|---|
| 1 | Introduction | 1 |
| 2 | Background and related work | 1–2 |
| 3 | Methods: testbeds, noise models, acquisition strategies, statistics | 2–3 |
| 4 | Results I: correcting the baseline | 3–4 |
| 5 | Results II: noise structure of real reaction data | 4 |
| 6 | Results III: sensitivity to each noise property | 4–5 |
| 7 | Results IV: the input-dependent case, and whether it can be fixed | 5–6 |
| 8 | Discussion, limitations, future work | 6 |
| 9 | Conclusion | 6 |

The chapters are ordered so that the uncertain work comes last, with three defensible results before
it. By month 3 the corrected baseline and the fixed statistical protocol are in place, and these
stand whatever follows. By month 4 the noise structure of real data is characterised; this is purely
descriptive, cannot fail, and sets the emphasis for the chapter after it. By month 5 the sensitivity
map is complete, and a factorial design always produces a result, including the useful finding that
active learning is robust to some properties. Month 6 covers the question of whether the problem can
be mitigated, which is the only genuinely uncertain part of the work.

## 12. Required Tools and Resources

- **Datasets:** all of those listed above are already accessible; nothing new needs to be acquired.
- **Software:** Python, with PyTorch or JAX, RDKit, scikit-learn and standard scientific libraries.
  An existing implementation of several uncertainty estimators and acquisition strategies is
  available as a starting point.
- **Compute:** cluster access with batch submission. The requirement is modest, since the work
  involves repeated training of small models rather than first-principles calculation. The account
  and group membership should be arranged at the start rather than when first needed.
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
Do not complete the list from memory or from search snippets — author lists in this area are often
garbled by secondary sources, and one attribution in an earlier draft was wrong until checked.
Verify each via Crossref (by DOI) or the arXiv API. Still to cover: a general active-learning survey;
theory on when adaptive sampling lowers label complexity; rates under noise conditions; Bayesian
active learning by disagreement; Monte-Carlo dropout and deep ensembles; the aleatoric/epistemic
split; robust regression under heavy tails; and the deterministic reaction dataset, cited to its own
paper.
