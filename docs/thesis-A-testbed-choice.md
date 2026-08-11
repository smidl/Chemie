# Topic A — choosing the testbed, and who we would be competing with

**Date:** 2026-08-11 · Companion to `thesis-A-problem-statement.md`

## The selection criterion

A testbed is interesting here **iff it makes one of C1–C4 measurable, or varies it while holding the
others fixed.** "Chemically important" is not the criterion; a dataset everyone cares about that
cannot separate the conditions is worth less to this thesis than a dull one that can.

Two conditions are properties of the world and therefore *belong to the dataset choice*:

- **C2 reducibility** — needs a task with **real, quantifiable label noise**. Estimating the
  aleatoric floor requires **replicate measurements**; without them, "how much of the uncertainty is
  irreducible" is unanswerable and C2 stays a hypothesis forever.
- **C3 actionability** — needs a **real downstream decision** consuming the model, not held-out
  accuracy.

C1 and C4 are algorithmic and travel with the code, so any dataset supports them.

## What we hold, assessed

| testbed | C2 noise | C3 decision | cost spread | status |
|---|---|---|---|---|
| **Chemlex acid–amine wetlab HTE** (`data/wetlab/`) | **real, irreducible** | none | uniform | working; 5 uncertainty estimators, 4 acquisitions |
| **Suzuki HTE, 10-fold** (`data/public/`, + DRFP features) | real | none | uniform | working; a public benchmark others use |
| **BH9 / Transition1x computed barriers** | **≈ zero** (deterministic given method) | none | **orders of magnitude** | staged; rungs installed |
| **Planner-coupled feasibility** (ξ_f + retro-fallback) | inherited | **yes — a real search consumes it** | high | labels are the blocker |

## The recommended design: a matched pair, differing in one condition

The single most informative thing available to us is not a better dataset — it is a **contrast**.

> Run the **identical** AL protocol on **wet-lab HTE** (high aleatoric noise) and on **computed
> barriers** (near-zero aleatoric noise), same task family, same models, same acquisitions.

That isolates **C2 by construction**. If AL fails on both, reducibility is not the explanation and
attention moves to C1/C4. If AL works on the computed task and fails on the wet-lab one, C2 is
identified — and that is a clean, quotable result that the mixed literature currently cannot
produce, because nobody runs one protocol across a noise contrast.

The computed side also carries the **cost spread** (seconds to hours per label), so the `÷ c(x)`
term becomes real rather than notational — which is exactly where topic B would attach later.

**Third arm, if time allows:** the planner-coupled task, the only one that can see C3 at all. Most
AL papers stop at held-out accuracy and are therefore structurally blind to it.

**One thing to check in week one:** whether the Chemlex wet-lab data contains **replicates**. If it
does, the aleatoric floor is directly estimable and C2 becomes a measured quantity rather than an
inferred one. If it does not, that is a reason to prefer a different HTE set — several public ones
carry replicate wells — and it changes the dataset decision, so it should be settled before anything
is built.

## Who we would be competing with

**The closest published work.** Yin, Gao, Panapitiya & Saldanha, *"Out-of-distribution evaluation of
active learning pipelines for molecular property prediction"*, **RSC Advances (2026)**, DOI
`10.1039/d5ra08055j` — metadata verified via Europe PMC. Solvation energy, evidential deep learning
for uncertainty, AL evaluated on OOD data drawn from PubChem. They occupy *AL under distribution
shift*.

Their most useful result for us is incidental: across 14 dataset–representation slices, the best
acquisition beat random on **AULC in all of them but on final PR-AUC in only 9**. **The metric
decides the answer.** That is direct evidence that "does AL work" is under-specified without stating
conditions, which is precisely our framing — and it is a gap they identify without filling.

**The state of the field, in one line.** Reported results are genuinely split: evidential deep
learning on QM9 and random-forest uncertainty on eMolecules are reported as clear wins; Bayesian
semi-supervised learning across six datasets and a pKa study are reported as indistinguishable from
random. *(These attributions come from the related-work of the paper above and must be verified
against Crossref before appearing in the proposal.)* A split literature with no organising principle
is the market opportunity.

**Adjacent groups, by condition.** Uncertainty-quantification benchmarking for molecular property
prediction (Coley group and others) owns **C1**. Batch acquisition and submodular selection —
BatchBALD and successors — owns **C4**. Classical AL theory owns the analysis of **C2/C3** but as
bounds, not estimators. Ligand-binding-affinity AL benchmarking is an adjacent, crowded application.

**Where the space is empty.** Everyone benchmarks; nobody *predicts*. We could not find work that,
given a dataset and a model, tells you **before spending the budget** whether AL will beat random.
That is the thesis's differentiator, and the reason it should not be pitched as another benchmark —
that market is full.

## What this implies for the pitch

Do **not** promise "AL improves reaction prediction". Promise **conditions and a decision rule**,
demonstrated on a noise contrast that the existing literature does not run. The chemistry earns its
place by supplying real noise, real cost spread and a real decision — three things the crowded
benchmark papers mostly lack.
