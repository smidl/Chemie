# Thesis Proposal — proposed content

*Structured to the SW-1 template (Version 14.0, 23.07.2026). Section numbering follows the template
exactly. Background and reasoning behind these choices are in the companion files in this folder:
`thesis-A-scope.md` (what is in and out), `thesis-A-problem-statement.md` (the abstract framing),
`thesis-A-testbed-choice.md` (datasets and competitors), `thesis-A-relation-to-sisters.md`
(positioning). Target length 8–10 pages.*

---

## 1. Working Title

**When Does Uncertainty-Guided Acquisition Invert? Heteroscedastic Label Noise as the Controlling
Variable in Active Learning**

*Alternatives:* "A Noise Threshold for Active Learning: Calibrating When Adaptive Sampling Beats
Random Sampling"; "The Price of Noise in Active Learning: Locating the Point Where Uncertainty-Based
Acquisition Fails".

## 2. Abstract (150–250 words)

Active learning promises to reduce the number of labels needed to train a model by choosing which
examples to label rather than sampling them at random. In practice the promise is unreliable:
published results on chemically motivated prediction tasks are split between clear improvements and
outcomes indistinguishable from random selection, with no established explanation for the
difference.

This thesis investigates one candidate explanation, stated precisely. Uniform (homoscedastic) noise
is *not* expected to be the problem: it enters predictive uncertainty as a constant offset and
therefore leaves the ranking of candidates unchanged. The problem is **input-dependent
(heteroscedastic) noise**, where measurement reliability varies across the input space. There, total
predictive uncertainty mixes a reducible component with an irreducible one, and once the irreducible
component varies more widely than the reducible one, acquiring "the most uncertain" example means
acquiring **the most poorly measured** one — so the strategy should perform *worse* than random, not
merely no better.

The study constructs noise with controlled input dependence on a deterministic reaction-property
dataset, sweeps the ratio R of aleatoric to epistemic variation, and measures where the advantage of
uncertainty-guided acquisition changes sign. It then asks whether real high-throughput experimental
chemistry data exhibits such input-dependent noise, and whether standard uncertainty estimators can
recover the reducible component from it.

Two known methodological defects in existing implementations are corrected first: greedy batch
selection without a diversity term, and insufficient replication of the initial labelled set. The
expected contribution is a quantitative, transferable criterion for deciding whether active learning
is worth running on a given task before the label budget is spent.

## 3. Introduction

**Background.** Supervised learning needs labels, and in the natural sciences labels are expensive:
a single experimental measurement can cost hours of laboratory time and material, and a single
first-principles calculation can cost hours of computation. Active learning (AL) addresses this by
letting the model choose what to label — typically selecting where its own predictive uncertainty is
highest.

**Why it matters academically.** The theoretical picture is well developed and conditional: the
benefit of adaptivity depends on properties of the problem, and in the high-noise limit it is known
to vanish. The empirical picture, by contrast, is reported largely as unconditional wins or losses.
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

**What is not yet known.** It is not known at what degree of *input-dependent* noise
uncertainty-guided acquisition ceases to outperform random selection — nor whether it merely
degrades to random or actively inverts — and whether that point can be identified from data before
committing a label budget. Noise magnitude alone is the wrong variable: uniform noise raises the
attainable error floor without disturbing the ranking that acquisition depends on.

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

1. **To correct** two identified methodological defects in the existing active-learning
   implementation — batch selection without a diversity term, and insufficient replication of the
   initial labelled set — so that subsequent comparisons are interpretable.
2. **To measure** the performance gap between uncertainty-guided and random acquisition as a
   function of the ratio R between input-dependent (aleatoric) and reducible (epistemic) variation,
   on a deterministic dataset with constructed noise.
3. **To identify** the value of R at which that gap becomes indistinguishable from zero and,
   separately, at which it changes sign — distinguishing degradation from inversion.
4. **To determine** whether acquisition restricted to the estimated *reducible* component is immune
   to that inversion, and how the immunity depends on the uncertainty estimator's ability to
   separate the two components.
5. **To evaluate** whether real high-throughput experimental data exhibits input-dependent noise, to
   estimate its R from replicate measurements, and to test whether its observed behaviour matches
   the controlled prediction.

## 6. Research Questions and Hypotheses

**RQ1.** How does the *structure* of label noise — uniform versus input-dependent — influence the
advantage of uncertainty-guided acquisition over random acquisition?

**RQ2.** Can acquisition be made robust to input-dependent noise by targeting the estimated
reducible component of uncertainty, and what does that require of the uncertainty estimator?

**RQ3.** Do real high-throughput chemistry datasets fall in the regime where uncertainty-guided
acquisition is expected to fail, and can that be established before labelling?

- **H1 (control).** Under **homoscedastic** noise the advantage of uncertainty-guided acquisition
  over random is **unaffected in ranking terms**; any reduction observed is attributable to the
  lowered error ceiling rather than to acquisition, and disappears when performance is measured
  relative to the attainable floor.
- **H2.** Under **heteroscedastic** noise the advantage decreases monotonically with R, the ratio of
  aleatoric to epistemic dynamic range.
- **H3.** Above approximately R = 1 the advantage **changes sign**: acquisition by total predictive
  uncertainty performs *worse* than random, because it preferentially selects the least reliably
  measured examples.
- **H4.** Acquisition restricted to the **estimated epistemic component** does not invert, to the
  extent that the estimator separates the components accurately.
- **H5 (mechanism control).** Acquisition by the **aleatoric** component alone underperforms random
  at large R. If it does not, the proposed mechanism is falsified.
- **H6.** An estimator assuming homoscedastic noise (a standard GP) is **mis-specified** under
  input-dependent noise and inverts at a lower R than an estimator with an input-dependent noise
  model.
- **H7.** Replacing greedy top-*k* batch selection with a diversity-aware rule increases the measured
  advantage at low R, and does not rescue it at high R.

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

**Identified gap.** The literature benchmarks; it does not predict. No work located to date provides
a criterion, computable before labelling, for deciding whether active learning will outperform
random selection on a given task. Noise is widely acknowledged as a factor but is rarely varied
systematically, in part because most benchmark datasets have unknown noise levels.

**Fit.** This thesis treats noise as the independent variable rather than a nuisance, and reports a
threshold rather than a win or a loss.

## 8. Methodology

**Research design.** Quantitative, experimental, computational. A controlled simulation study
(injected noise, known ground truth) followed by an observational validation on real experimental
data.

**Data collection.** No new data is generated. Three existing sources:

- a **deterministic** reference dataset of computed reaction barriers, used as the noise-free base
  onto which controlled noise is injected (BH9, 449 reactions with high-level reference values —
  Prasad et al., 2022; and a larger deterministic set for scale);
- a **real experimental** high-throughput dataset with genuine measurement noise (acid–amine
  coupling data from Zhong et al., 2025);
- a **public experimental** dataset for external comparability (Suzuki coupling reaction screening —
  Perera et al., 2018).

**Design.** A **2 × 3 factorial** with a swept covariate: noise structure (homoscedastic control
versus heteroscedastic, with R swept across roughly two orders of magnitude) × acquisition target
(total predictive / epistemic-only / aleatoric-only), repeated across uncertainty estimators that
differ in whether they model input-dependent noise. Heteroscedastic noise is constructed by making
σ²(x) a controlled function of position in the representation space, so that R is set by design and
known exactly.

**Sampling strategy.** Repeated randomised active-learning simulations. Each configuration —
acquisition target × noise structure × R × estimator × repeat — is run with the initial labelled set drawn
independently across both strategy and repeat, to avoid confounding the strategy comparison with the
variance of a shared initial draw. A minimum of 20 repeats per configuration, with the number fixed
by a power calculation performed on pilot runs before the main study.

**Data analysis.** The primary outcome is the difference in learning-curve area between an
acquisition strategy and random selection, reported with bootstrap confidence intervals. Paired
comparisons across matched repeats; the threshold is estimated as the noise level at which the
confidence interval for that difference first includes zero. Secondary outcomes are the final-model
error and the calibration of the uncertainty estimates. Hypotheses H2 and H3 are distinguished by
the sign of the interval, not merely by significance.

**Ethical considerations.** No human participants, no personal data, no animal subjects. All
datasets are published and used under their stated licences. Computation is on institutional
resources; energy use is modest, as the study reuses existing labels rather than generating new
calculations.

**Limitations.** Constructed noise is a model of real noise. Real measurement error may be
systematic rather than random, or its input dependence may follow structure not captured by the
constructed σ²(x); this is addressed by testing more than one form of input dependence and by the
real-data validation step. Estimating R on real data requires **replicate measurements**; if the
available experimental data lacks replicates, R can only be bounded rather than measured, and the
validation becomes correspondingly weaker. Findings are established for one task family and one model class, and generalisation
beyond them is a claim the thesis will not make. Access to the experimental datasets is already in
place.

## 9. Expected Results

- **No ranking effect under homoscedastic noise** (H1) — a null result, and an important one,
  because it localises the problem and rules out the interpretation that "noise breaks active
  learning" in general.
- A **monotonic decay with R** under heteroscedastic noise (H2), reported as a dose–response curve.
- A **sign change** near R ≈ 1 (H3), locating an inversion rather than merely a vanishing advantage
  — a sharper and more actionable result than "no better than random".
- Evidence on whether **epistemic-only acquisition is immune** (H4), and on how much of that
  immunity survives real, imperfect uncertainty decomposition.
- A **corrected baseline**: quantification of how much of a previously observed null result is
  attributable to greedy batch selection rather than to the data (H4). It is entirely possible that
  the existing negative result reverses once this defect is removed; that outcome is anticipated and
  is not a failure of the study.
- Placement of at least one real experimental dataset relative to the threshold, indicating whether
  active learning should be expected to help on it.

## 10. Expected Contribution

**Academic.** A quantitative link between an established theoretical prediction — that adaptivity's
advantage degrades with noise — and a measurable property of real datasets, in a field where the
empirical literature is currently split without an organising variable. The dose–response
methodology is transferable to other conditions under which active learning may fail.

**Practical.** A decision rule for practitioners: estimate the noise level of your task, compare it
to the threshold, and decide whether to invest in an active-learning workflow. For laboratories and
computational campaigns operating under a fixed budget, this converts a matter of faith into a
calculation.

**Methodological.** Two concrete, reusable corrections — diversity-aware batch selection and correct
replication of the initial design — with a demonstration of how much each changes the conclusion.

## 11. Preliminary Table of Contents and Timeline

| # | Chapter | Months |
|---|---|---|
| 1 | Introduction | 1 |
| 2 | Background and Related Work | 1–2 |
| 3 | Methods: testbeds, noise models, acquisition strategies, statistical protocol | 2–3 |
| 4 | Results I: correcting the baseline (batch selection, replication) | 3–4 |
| 5 | Results II: the noise dose–response and the threshold | 4–5 |
| 6 | Results III: validation on real experimental data | 5–6 |
| 7 | Discussion, limitations, future work | 6 |
| 8 | Conclusion | 6 |

**Milestones.** End of month 3: corrected baseline reproduced and the statistical protocol fixed —
this is the point at which the thesis has a guaranteed defensible result regardless of what follows.
End of month 5: threshold determined. End of month 6: real-data validation and writing complete.

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
5. Yin, T., Gao, P., Panapitiya, G., & Saldanha, E. G. (2026). Out-of-distribution evaluation of
   active learning pipelines for molecular property prediction. *RSC Advances, 16*, 5281–5295.
   https://doi.org/10.1039/d5ra08055j
6. Zhong, H., Liu, Y., Sun, H., Liu, Y., Zhang, R., Li, B., Yang, Y., & Huang, Y. (2025). Towards
   global reaction feasibility and robustness prediction with high-throughput data and Bayesian deep
   learning. *Nature Communications, 16*. https://doi.org/10.1038/s41467-025-59812-0

**Still to be added — 6 to 12 further sources, to be located and verified before submission.**
The template asks for 10–20; the six above are the ones whose metadata has been confirmed against an
authoritative source. Do **not** fill the remainder from memory or from search-result snippets —
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
