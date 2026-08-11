# Thesis Proposal — proposed content

*Structured to the SW-1 template (Version 14.0, 23.07.2026). Section numbering follows the template
exactly. Background and reasoning behind these choices are in the companion files in this folder:
`thesis-A-scope.md` (what is in and out), `thesis-A-problem-statement.md` (the abstract framing),
`thesis-A-testbed-choice.md` (datasets and competitors), `thesis-A-relation-to-sisters.md`
(positioning). Target length 8–10 pages.*

---

## 1. Working Title

**The Effect of Noise-Model Assumptions on the Quality of Active Learning: A Sensitivity Study on
Chemical Reaction Data**

*Alternatives:* "How Much Does the Noise Model Matter in Active Learning?"; "Noise-Model
Mis-specification and the Failure of Uncertainty-Guided Acquisition".

## 2. Abstract (150–250 words)

Active learning aims to reduce the number of labels a model needs by choosing which examples to
label rather than sampling at random. Reported results in chemistry and molecular property
prediction are inconsistent: some studies find clear gains, others find performance indistinguishable
from random selection, and no organising explanation is established.

Almost every active-learning method rests on an assumption about how labels are corrupted — the
*noise model*. That assumption is rarely examined and is almost always the simplest one:
independent, identically distributed, Gaussian noise of constant magnitude. Real experimental
measurements violate all three parts of it.

This thesis asks how much that matters. It systematically varies the *true* noise structure — its
dependence on the input, its tail behaviour, and its correlation between measurements — while
holding the learner's assumed noise model fixed, and measures the resulting change in
active-learning performance relative to random sampling. One specific prediction is examined in
detail: that input-dependent noise can lead uncertainty-guided acquisition to select the least
reliably measured examples, and therefore to perform *worse* than random.

The study also characterises the noise structure of real high-throughput chemistry datasets from
replicate measurements. The expected contribution is a sensitivity map showing which noise-model
assumptions materially affect active learning and which do not, together with guidance on when the
method should be expected to help.

## 3. Introduction

**Background.** Supervised learning needs labels, and in the natural sciences labels are expensive:
a single experimental measurement can cost hours of laboratory time and material, and a single
first-principles calculation can cost hours of computation. Active learning (AL) addresses this by
letting the model choose what to label — typically selecting where its own predictive uncertainty is
highest.

**The overlooked assumption.** Predictive uncertainty is not a raw observation — it is produced by a
model that assumes something about how observations are corrupted. The near-universal default is
noise that is independent between measurements, identically distributed, Gaussian, and of constant
magnitude across the input space. Experimental chemistry data satisfies none of these: measurement
reliability varies with the reaction, occasional gross errors occur, and measurements sharing a
plate or batch share systematic error.

**Why it matters academically.** The theoretical picture is well developed and conditional: the
benefit of adaptivity depends on properties of the problem, including the noise regime, and in the
high-noise limit it is known to vanish. The empirical picture, by contrast, is reported largely as unconditional wins or losses.
Recent benchmark work finds active learning improving one metric across all evaluated slices while
improving another in only a subset, which indicates the question "does active learning work" is
under-specified as usually posed.

**Why it matters practically.** Running AL is not free — it requires uncertainty estimates,
retraining between rounds, and a sequential experimental workflow. A laboratory or computational
campaign that adopts it on faith may spend that overhead for no benefit. A criterion for deciding in
advance is directly useful.

**Structure.** Section 4 states the gap; Section 5 the objectives; Section 6 the questions and
hypotheses; Section 7 the literature; Section 8 the method; Sections 9–10 expected results and
contribution; Sections 11–13 plan, resources and references.

## 4. Problem Statement

**What is not yet known.** It is not known which departures from the standard noise assumption
materially degrade active learning, by how much, or whether any of them can reverse its advantage
outright. Nor is it established what noise structure real chemical reaction datasets actually have.

**Why the gap is important.** The literature is split. Some studies report clear gains from
uncertainty-based acquisition; others report results indistinguishable from random on comparable
tasks. Without an organising variable, each new dataset is an independent gamble, and negative
results are difficult to interpret — a failure may reflect the estimator, the acquisition rule, the
batch construction, or the task itself.

**Who is affected.** Any group spending a constrained budget on expensive labels: experimental
chemistry and materials laboratories, groups running first-principles calculations, and more broadly
any active-learning practitioner working with noisy measurements.

**Consequences of not addressing it.** Budgets are spent on machinery that cannot help; genuine
negative results remain unpublishable because they cannot be distinguished from implementation
error; and the field continues to accumulate mutually contradictory benchmark results.

## 5. Research Objectives

1. **To correct** two identified defects in the existing active-learning implementation available to
   this project — batch selection without a diversity term, and insufficient replication of the
   initial labelled set — so that subsequent comparisons are interpretable.
2. **To characterise** the noise structure of real high-throughput chemical reaction datasets from
   replicate measurements: its dependence on the input, its tail behaviour, and its correlation
   within experimental batches.
3. **To measure** the sensitivity of active-learning performance to controlled departures from the
   standard noise assumption, using constructed noise on a deterministic dataset where both the
   signal and the noise are known exactly.
4. **To test** in detail the specific prediction that input-dependent noise can invert the advantage
   of uncertainty-guided acquisition, and to determine whether restricting acquisition to the
   reducible component of uncertainty prevents it.

## 6. Research Questions and Hypotheses

**RQ1.** Which departures from the standard i.i.d. constant-variance Gaussian noise assumption
materially affect the performance of active learning relative to random sampling, and which do not?

**RQ2.** What noise structure do real high-throughput chemical reaction datasets exhibit?

**RQ3.** Under which of these departures, if any, does uncertainty-guided acquisition become *worse*
than random rather than merely equivalent to it?

Hypotheses are grouped by axis of mis-specification. Each carries a stated prior expectation, so the
study is confirmatory rather than exploratory.

**Axis A — variance structure (constant vs input-dependent).**
- **H1 (control).** Under constant-variance noise, performance relative to random is unaffected in
  ranking terms; any degradation reflects the lowered attainable error ceiling rather than the
  acquisition rule, and disappears when measured relative to that ceiling.
- **H2.** Under input-dependent noise the advantage decreases monotonically with R, the ratio of
  irreducible to reducible variation across the candidate pool.
- **H3.** Above a determinable value of R the advantage **changes sign**, because acquisition then
  preferentially selects the most poorly measured examples.
- **H4.** Restricting acquisition to the estimated *reducible* component prevents the inversion, to
  the extent that the decomposition is accurate.

**Axis B — tail behaviour (Gaussian vs heavy-tailed).**
- **H5.** Under heavy-tailed noise, acquisition by predictive uncertainty preferentially selects
  outliers, degrading performance at a rate governed by the contamination fraction rather than by
  the nominal variance.

**Axis C — dependence (independent vs correlated within batches).**
- **H6.** When measurements sharing an experimental batch share error, the information gained from a
  batch of queries is systematically overestimated, and the effect compounds with the
  batch-selection defect identified in Objective 1.

**Axis D — the estimator (pre-registered null).**
- **H7.** Improving the *estimator* alone — for example replacing a constant-variance Gaussian
  process with one modelling input-dependent noise — while leaving the acquisition rule unchanged,
  does **not** materially change the outcome. This is registered as a null in advance: prior work in
  this group and in a parallel project both found that better noise modelling did not improve
  downstream decisions, and the published successes in this area instead came from changing *what is
  acquired* rather than how it is modelled. A positive result would contradict that prior and would
  be reported as such.

## 7. Preliminary Literature Review

**Key theories.** Classical active-learning theory characterises when adaptive sampling improves on
passive sampling in terms of problem-dependent quantities — the geometry of the hypothesis class
under the data distribution, and the noise regime — with the advantage collapsing in the agnostic
high-noise limit. Batch acquisition is governed by the submodularity of information: the value of a
set of queries is generally less than the sum of the values of its members, so greedy selection of
the *k* individually highest-scoring points is known to be suboptimal (Kirsch, van Amersfoort & Gal,
2019). The decomposition of predictive uncertainty into an *aleatoric* component, arising from noise
in the data-generating process, and an *epistemic* component, arising from limited data, is the
conceptual basis of this thesis: only the epistemic component is reducible by labelling.

**Key findings.** Uncertainty estimation for molecular property prediction has been benchmarked
systematically, with substantial variation in the reliability of different scalable methods (Scalia,
Grambow, Pernici, Li & Green, 2020). Recent evaluation of active-learning pipelines for molecular
property prediction under distribution shift reports that the best acquisition strategy outperformed
random on the area under the learning curve in all fourteen dataset–representation slices examined,
but on the final precision–recall metric in only nine — evidence that the outcome is
metric-dependent (Yin, Gao, Panapitiya & Saldanha, 2026). Bayesian deep learning with several
uncertainty estimators has been applied to reaction feasibility prediction on experimental
high-throughput data (Zhong et al., 2025), providing the experimental testbed used here.

**A pattern in the positive results.** Where noise-aware methods *have* demonstrably helped, the
improvement came from changing **what is acquired or optimised**, not from fitting noise more
accurately. Heteroscedastic Bayesian optimisation improved on both homoscedastic Bayesian
optimisation and random sampling by introducing acquisition heuristics that explicitly penalise
aleatoric noise (Griffiths, Aldrick, Garcia-Ortegon, Lalchand & Lee, 2022); active label cleaning
improved dataset quality under a fixed budget by re-annotating suspect labels rather than acquiring
new ones (Bernhardt et al., 2022). A survey of active learning specifically under label noise
(Mots'oehli & Baek, 2023) organises the adjacent literature. This pattern motivates separating the
acquisition target (Axis A) from the estimator (Axis D), and registering the latter as a null.

**Identified gap.** The literature benchmarks active learning; it does not characterise its
sensitivity to the noise assumptions it rests on, and it rarely reports the noise structure of the
datasets used. No work located to date provides
a criterion, computable before labelling, for deciding whether active learning will outperform
random selection on a given task. Noise is widely acknowledged as a factor but is rarely varied
systematically, in part because most benchmark datasets have unknown noise levels.

**Fit.** This thesis treats noise as the independent variable rather than a nuisance, and reports a
threshold rather than a win or a loss.

## 8. Methodology

**Research design.** Quantitative and computational, in two parts: a *descriptive* analysis of real
experimental data, and a *controlled simulation study* with known ground truth. The first determines
which regions of the second are practically relevant.

**Part 1 — descriptive.** Estimate the noise structure of the experimental datasets from replicate
measurements: the dependence of variance on the input, the tail behaviour of residuals, and the
correlation of error within experimental batches. This requires replicate wells; where absent, the
structure can be bounded but not measured, and that limitation is reported explicitly.

**Part 2 — controlled.** A factorial design crossing the *true* noise structure (Axes A–C, each
swept across a range that includes the standard assumption as a control) with the acquisition target
(total predictive uncertainty, reducible component only, irreducible component only) and the
uncertainty estimator. Because the noise is constructed on a deterministic base, both components are
known exactly, which additionally permits validating the estimators themselves.

**Sampling strategy.** Repeated randomised active-learning simulations. Each configuration —
acquisition target × noise structure × R × estimator × repeat — is run with the initial labelled set drawn
independently across both strategy and repeat, to avoid confounding the strategy comparison with the
variance of a shared initial draw. A minimum of 20 repeats per configuration, with the number fixed
by a power calculation performed on pilot runs before the main study.

**Data analysis.** The primary outcome is the difference in learning-curve area between an
acquisition strategy and random selection, with bootstrap confidence intervals over matched repeats.
Sensitivity is reported as the change in that difference per unit change along each noise axis —
including axes where it is indistinguishable from zero, which are reported as such. Where a sign
change is predicted, hypotheses are distinguished by the sign of the interval rather than by
significance alone. Secondary outcomes: final model error, and calibration of the uncertainty
estimates.

**Ethical considerations.** No human participants, no personal data, no animal subjects. All
datasets are published and used under their stated licences. Computation is on institutional
resources; energy use is modest, as the study reuses existing labels rather than generating new
calculations.

**Limitations.** Constructed noise is a model of real noise and may not reproduce its structure;
this is mitigated by informing the constructions with Part 1 and by testing more than one form per
axis. Results are established for one task family and one model class, and no claim of generality
beyond them will be made. Estimating noise structure on real data requires **replicate
measurements**; without them Part 1 yields bounds rather than estimates. Findings are established for one task family and one model class, and generalisation
beyond them is a claim the thesis will not make. Access to the experimental datasets is already in
place.

## 9. Expected Results

- A **sensitivity map**: for each axis of noise-model mis-specification, the magnitude of its effect
  on active-learning performance with confidence intervals — **including axes where the effect is
  negligible**, which are as informative as the ones where it is not.
- A **null under constant-variance noise** (H1), localising where the problem is not.
- A **dose–response curve** for input-dependent noise, and a determination of whether an inversion
  occurs (H3) and where.
- A **characterisation of the noise structure of real reaction data** — to our knowledge not
  previously reported — establishing whether the regimes examined are practically relevant.
- A **corrected baseline** quantifying how much of a previously observed null result is attributable
  to batch-selection design rather than to the data. It is entirely possible that this negative
  reverses once the defect is removed; that outcome is anticipated and is not a failure of the study.

## 10. Expected Contribution

**Academic.** A systematic sensitivity analysis of active learning with respect to the noise
assumptions it rests on — currently absent from a literature that reports outcomes without reference
to noise structure. The methodology transfers to other domains with noisy oracles.

**Practical.** Guidance on when active learning is worth its overhead, grounded in a property of the
dataset that can be estimated in advance from replicate measurements. For a laboratory deciding
whether to adopt a sequential experimental workflow, this converts a matter of faith into a check.

**Methodological.** Two concrete, reusable corrections — diversity-aware batch selection and correct
replication of the initial design — with a demonstration of how much each changes the conclusion.

## 11. Preliminary Table of Contents and Timeline

| # | Chapter | Months |
|---|---|---|
| 1 | Introduction | 1 |
| 2 | Background and Related Work | 1–2 |
| 3 | Methods: testbeds, noise models, acquisition strategies, statistical protocol | 2–3 |
| 4 | Results I: correcting the baseline (batch selection, replication) | 3–4 |
| 5 | Results II: noise structure of real reaction data | 4 |
| 6 | Results III: sensitivity of active learning to each noise axis | 4–5 |
| 7 | Results IV: the input-dependent case in detail, and whether it can be mitigated | 5–6 |
| 8 | Discussion, limitations, future work | 6 |
| 9 | Conclusion | 6 |

**Risk structure.** The chapters are deliberately ordered so the uncertain work comes last and three
independent defensible results precede it.

- *Month 3* — corrected baseline and fixed statistical protocol. A guaranteed result irrespective of
  everything after it.
- *Month 4* — noise structure of real data. Purely descriptive; it cannot fail, and it determines
  which regimes in Chapter 6 deserve emphasis.
- *Month 5* — the sensitivity map. A factorial simulation always yields a result, including the
  informative outcome that active learning is *robust* to some axes.
- *Month 6* — the mitigation question, the only genuinely uncertain element.

## 12. Required Tools and Resources

- **Datasets:** BH9 reference barriers; a large deterministic computed-reaction dataset; acid–amine
  experimental screening data; Suzuki coupling screening data. All already available to the group;
  no new acquisition needed.
- **Software:** Python; PyTorch or JAX; RDKit for molecular representations; scikit-learn; standard
  scientific and statistical libraries. Existing group code implementing five uncertainty estimators
  and four acquisition strategies serves as the starting point.
- **Compute:** access to the institutional cluster (RCI) with SLURM batch submission. Requirements
  are modest — repeated training of small models, not first-principles calculation. **Account and
  group membership must be arranged at the start of the project rather than when first needed.**
- **Supervision:** access to the group's prior results and to the parallel projects whose
  methodological standards this work adopts.

## 13. Preliminary References

*Verified against Crossref or arXiv metadata. APA style.*

1. Kirsch, A., van Amersfoort, J., & Gal, Y. (2019). *BatchBALD: Efficient and diverse batch
   acquisition for deep Bayesian active learning*. arXiv:1906.08158.
2. Perera, D., Tucker, J. W., Brahmbhatt, S., Helal, C. J., Chong, A., Farrell, W., Richardson, P.,
   & Sach, N. W. (2018). A platform for automated nanomole-scale reaction screening and micromole-
   scale synthesis in flow. *Science, 359*(6374), 429–434. https://doi.org/10.1126/science.aap9112
3. Prasad, V. K., Pei, Z., Edelmann, S., Otero-de-la-Roza, A., & DiLabio, G. A. (2022). BH9, a new
   comprehensive benchmark data set for barrier heights and reaction energies. *Journal of Chemical
   Theory and Computation, 18*(1), 151–166. https://doi.org/10.1021/acs.jctc.1c00694
4. Scalia, G., Grambow, C. A., Pernici, B., Li, Y.-P., & Green, W. H. (2020). Evaluating scalable
   uncertainty estimation methods for deep learning-based molecular property prediction. *Journal of
   Chemical Information and Modeling, 60*(6), 2697–2717.
   https://doi.org/10.1021/acs.jcim.9b00975
5. Bernhardt, M., Castro, D. C., Tanno, R., Schwaighofer, A., Tezcan, K. C., Monteiro, M., et al.
   (2022). Active label cleaning for improved dataset quality under resource constraints. *Nature
   Communications, 13*. https://doi.org/10.1038/s41467-022-28818-3
6. Griffiths, R.-R., Aldrick, A. A., Garcia-Ortegon, M., Lalchand, V., & Lee, A. A. (2022).
   Achieving robustness to aleatoric uncertainty with heteroscedastic Bayesian optimisation.
   *Machine Learning: Science and Technology, 3*(1), 015004.
   https://doi.org/10.1088/2632-2153/ac298c
7. Mots'oehli, M., & Baek, K. (2023). *Deep active learning in the presence of label noise: A
   survey*. arXiv:2302.11075.
8. Yin, T., Gao, P., Panapitiya, G., & Saldanha, E. G. (2026). Out-of-distribution evaluation of
   active learning pipelines for molecular property prediction. *RSC Advances, 16*, 5281–5295.
   https://doi.org/10.1039/d5ra08055j
9. Zhong, H., Liu, Y., Sun, H., Liu, Y., Zhang, R., Li, B., Yang, Y., & Huang, Y. (2025). Towards
   global reaction feasibility and robustness prediction with high-throughput data and Bayesian deep
   learning. *Nature Communications, 16*. https://doi.org/10.1038/s41467-025-59812-0

**Still to be added — 3 to 9 further sources, to be located and verified before submission.**
The template asks for 10–20; the nine above are the ones whose metadata has been confirmed against
an authoritative source. Do **not** fill the remainder from memory or from search-result snippets —
author lists in this area are routinely garbled by secondary sources. Verify each through Crossref
(by DOI) or the arXiv API before writing it down. Topics still to cover:

- a general survey of active learning;
- the theory of when adaptive sampling improves label complexity (disagreement-based analysis);
- rates of active learning under noise conditions;
- Bayesian active learning by disagreement (the acquisition function BatchBALD extends);
- Monte-Carlo dropout, and deep ensembles, as uncertainty estimators;
- the decomposition of predictive uncertainty into aleatoric and epistemic components;
- one or two of the specific studies reporting active learning to be indistinguishable from random
  on molecular tasks, cited directly rather than through another paper's related-work section;
- the deterministic reaction dataset used as the noise-free base, cited to its own publication.
