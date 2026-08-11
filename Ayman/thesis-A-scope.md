# Topic A — scoping down to an actual master's thesis

**Date:** 2026-08-11 · Supersedes the scope implied by `thesis-A-problem-statement.md` and
`thesis-A-testbed-choice.md`. Those describe a programme; this describes a thesis.

## The honest problem with the previous framing

C1–C4 across two testbeds, plus an ex-ante diagnostic, plus a planner arm, is roughly **18 months**
of work: removing the batch confound (2–4 wk), powering the study (1–2 wk), five estimators × four
acquisitions (4–6 wk), an aleatoric/epistemic decomposition (3–4 wk), a second testbed pipeline
(6–8 wk), a capacity sweep (3–4 wk), and then an open-ended research contribution on top. That is
not a master's thesis. It is also the classic way a good student ends up with six half-finished
threads and no defensible result.

C1–C4 stays as the **framing** — it is what makes the work legible and positions it against the
sisters. But a thesis should attack **one** term of it.

## Which term, and why C2

**C2 reducibility**, for three reasons:

1. **It is the term the theory says is decisive.** Adaptivity's advantage collapses in the high-noise
   limit. If noise is what kills AL, nothing algorithmic rescues it — so C2 dominates C1 and C4
   whenever it binds.
2. **It is the term our sisters structurally cannot study.** DecisionBO's simulators and Planning's
   benchmarks are deterministic. This is the contribution only Chemie can make.
3. **It can be made a *continuous* variable, cheaply.**

That third point is what makes the thesis feasible, and I had missed it. The noise contrast does
**not** require building a computed-barrier pipeline. BH9 is *a table of 449 reference barriers* and
Transition1x *a table of 10 073* — as AL testbeds they are ordinary regression datasets requiring
**no quantum chemistry at all**. So:

> Take a deterministic dataset. **Inject label noise at controlled levels σ.** Measure the
> AL-versus-random gap as a function of σ. Find where it vanishes. Then check whether real wet-lab
> HTE sits above or below that threshold.

A dose–response curve, not a binary contrast — and dose–response is what makes a *diagnostic*
possible at all, because the deliverable becomes "estimate your noise, compare to the threshold".

## The thesis, scoped

**Core — must be finished, and is finishable.**

1. **Remove the C4 confound.** Replace greedy top-`k` with a diversity-aware batch rule at the same
   budget. This is a *prerequisite fix*, not a research question: until it is done, no comparison in
   this testbed means anything.
2. **Power the comparison properly.** Design varying independently across strategy and repeat, per
   ADR 0004. The current two-seed runs are inadmissible.
3. **The noise dose–response.** On a deterministic dataset with injected noise at controlled levels,
   measure the AL-versus-random gap as a function of σ, and locate the level at which it vanishes.
4. **Validate on real data.** Estimate the noise level of a real wet-lab HTE set and check whether
   the observed AL behaviour matches what the threshold predicts.

That is one dataset family, one axis, one deliverable: **a noise threshold for when active learning
stops beating random, calibrated on synthetic noise and tested on real noise.**

**Stretch — only if the core lands early.**

5. Does the threshold move with the uncertainty estimator? (C1, a robustness check on the core
   result — *not* a separate study of estimators.)
6. Does it move with model capacity? (C3, borrowing DecisionBO's existing sweep protocol rather
   than designing one.)

**Explicitly out of scope**, and to be written into the proposal so it is not re-negotiated in month
six: planner coupling, cost-aware/multi-fidelity acquisition, any new chemistry pipeline, and the
general ex-ante diagnostic across arbitrary tasks. Topic B exists for the cost dimension; the
diagnostic beyond noise is a PhD, not this.

## The fallback, stated now

If the threshold turns out not to be sharp — if the gap decays so gradually that no usable
threshold exists — **items 1 and 2 alone are already a defensible thesis**: a corrected, properly
powered empirical result replacing an underpowered and confounded negative, on a real dataset, with
the confound identified and removed. That is a real contribution and it is guaranteed by month three.

A thesis should have its floor established before it starts. This one does.

## What to tell Ayman in the first meeting

- The framing is C1–C4, and he should understand all four, because they are what makes the work
  legible and connect it to two sister projects.
- He will **work on C2 only**. The others appear as a fixed confound (C4), a robustness check (C1),
  and future work (C3).
- The likely honest outcome is a threshold and a negative-leaning story, not "AL improves chemistry".
- The floor is guaranteed and the ceiling is a genuinely publishable diagnostic.
