# Topic A — what we currently understand about the problem

**Date:** 2026-08-11 · Background for the thesis proposal. Measured claims carry their numbers;
everything else is labelled as hypothesis.

## The practical decision

Labels are expensive. A wet-lab reaction feasibility measurement costs real time and material; a
DFT barrier costs hours. So: **given a budget of N labels, which N do you acquire?** The standard
answer is to acquire where the model is most uncertain, on the reasoning that those points are the
most informative.

In this project that answer has not worked, twice, in different settings. The thesis is to find out
why, and to produce something that tells you in advance.

## What we have measured

**1. Predicted uncertainty is nearly orthogonal to actual error.** On real noisy HTE data, Spearman
ρ between predicted σ and realised error was **0.042** for a GP and **0.144–0.146** for ensembles.
Acquisition by uncertainty presumes that ranking is informative. At ρ ≈ 0.04 it carries almost no
signal, so "acquire the most uncertain" is close to "acquire arbitrarily".

*Caveat we must not drop:* one arm's epistemic estimator was MC-dropout, which is a weak
approximation. So this measures *our estimators*, not uncertainty in principle.

**2. The signal that exists is aleatoric, not epistemic.** In our data the epistemic component
behaved like noise while the aleatoric component carried structure. This matters more than it
sounds: if uncertainty is dominated by *irreducible* noise, then acquiring high-uncertainty points
means preferentially acquiring **the points whose labels are least reliable**. That is not merely
uninformative — it can be worse than random, because the budget buys noisy labels.

**3. The same thesis was refuted independently at scale.** The sister project (DecisionBO / PFN4BO)
tested decision-aware training across a much larger sweep and found no benefit, then generalised the
reason as **regret-relevant sufficiency**: a model influences the downstream decision only up to a
quality threshold, above which the outcome is set by the acquisition rule, the search and the
budget. Every published success they could find sat *below* such a threshold. Applied here: if the
model is already good enough for the decision being made, better labels cannot show a benefit no
matter how well you choose them.

**4. Our own decision-focused results have the same shape.** A rank-trained search heuristic beat a
vanilla value network (99.2 vs 97.5) and then lost by 8–11 points to one trained on path
consistency. What mattered was the *structure of the objective*, not the uncertainty machinery
around it.

## Four candidate explanations, and how to tell them apart

This is the core of the thesis: they are separable by experiment, and nobody here has separated
them.

**H1 — the estimator is bad.** σ is uninformative because MC-dropout and small ensembles are poor
posterior approximations. *Test:* hold the acquisition rule fixed and swap the estimator across the
five already implemented in the testbed (BNN-SVI, BNN-NUTS, MC-dropout, deep ensemble, deep-kernel
GP). If AL improves with a better estimator, H1 is live.

**H2 — the task is aleatoric-dominated.** No estimator can help because the uncertainty is
irreducible. *Test:* decompose predicted uncertainty into aleatoric and epistemic parts and measure
what fraction of total variance is reducible; then check whether acquisition on the *epistemic
component alone* beats acquisition on total uncertainty. The testbed already has an aleatoric
acquisition arm, which under H2 should be **worse** than random rather than merely equal.

**H3 — batch redundancy, and this one is a concrete flaw in our current code.** `zhong_al.py`
selects with `np.argsort(-eu)[:k]` — pure greedy top-k — with **batch size 100**. Greedy top-k with
no diversity term picks 100 mutually near-duplicate points, so a batch of 100 may carry the
information of a handful. This is a well-known failure mode with a well-known family of fixes
(BatchBALD, clustering the uncertain pool, determinantal selection). *Test:* re-run with a
diversity-aware batch rule at the same budget. **If this alone recovers the gap, our "AL doesn't
work here" conclusion was never about uncertainty at all.** It is the cheapest hypothesis to test
and should be tested first.

**H4 — sufficiency.** The model is already above the threshold where labels change the decision.
*Test:* sweep model capacity and training-set size, and plot the AL-versus-random gap against a
quality proxy. Under H4 the gap decays monotonically as quality rises, and any AL benefit is
confined to the low-quality regime.

These are not mutually exclusive, and the interesting outcome is a decomposition rather than a
winner.

## What we have not measured

- Whether **calibration** (as opposed to ranking) matters — we tested ρ between σ and error, not
  whether the estimators are calibrated.
- Whether the failure is **specific to this dataset**: binary feasibility on HTE data, with class
  balance we have not characterised.
- Whether **cold-start** matters: all curves begin at 100 labels; behaviour below that is unknown.
- Whether the metric choice (**F1**) hides the effect — AL might improve calibration or tail
  performance while leaving F1 flat.

## A methodological trap the thesis must avoid

Active-learning curves are unusually vulnerable to **initial-design pseudo-replication**. If every
strategy starts from the same initial labelled set, and only a few seed values exist, then the
difference between strategies is confounded with the variance of that one initial draw. The sister
project found this collapsed **four** of their headline results at p ≲ 0.003, one reversing sign.

The existing runs here use **two seeds**. Under ADR 0004 that is not a result. The correct
construction is `run seed = base + s + 9973·i` so the design varies independently across strategy
and repeat, with enough repeats to separate the two. Powering this properly is the first task and is
worth doing even before any new idea is introduced — it may change the sign of what is currently
believed.

## Why this makes a good thesis

The question — *when does active learning help, and can you tell in advance?* — is one the field
asks and answers mostly with anecdote. Here it comes with a working testbed, five uncertainty
estimators, four acquisition rules, real experimental data, two independent prior negatives to
explain, and a concrete suspicion (H3) that the negatives may be an artefact of a fixable
implementation choice.

The deliverable we would most value is the **ex-ante diagnostic**: given a dataset and a model,
predict whether uncertainty-guided acquisition will beat random *before* spending the labels. That
is the question the sister project asked us and that nobody in either tree can currently answer.
