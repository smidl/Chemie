# Topic A — problem statement

**Date:** 2026-08-11 (rewritten) · A computer-science thesis. Chemistry is the testbed, not the
subject.

---

## 1. The abstract problem

We want to learn a function `f : X → Y` from labels that cost money. An **adaptive** sampler chooses
each query using everything seen so far; a **passive** sampler draws i.i.d. from the pool. The
promise of active learning is that adaptivity buys a lower label complexity for the same target
error.

That promise is **conditional**, and the theory is explicit about it. Adaptivity helps only when the
sampler's ranking of candidate points correlates with the **actual marginal value of labelling
them**. Write that value for a candidate `x`, given current state `S`:

```
V(x | S)  =  ΔU(x | S)        how much the label reduces REDUCIBLE uncertainty about f
           × A(x | S)         how much that reduction changes the DOWNSTREAM DECISION
           ÷ c(x)             what the label costs
```

An acquisition function is a *proxy* for `V`. Every failure of active learning is a failure of that
proxy, and the failures come in four structurally different kinds:

| | condition | fails when | nature |
|---|---|---|---|
| **C1 Estimability** | the proxy ranks `V` correctly | our uncertainty estimate is too poor to rank | statistical / algorithmic |
| **C2 Reducibility** | uncertainty is epistemic, i.e. labels can remove it | noise dominates; high-`σ` points are *noisy*, not *informative* | property of the data-generating process |
| **C3 Actionability** | reduced uncertainty changes the decision | the model is already good enough for the decision it feeds | property of the task |
| **C4 Batch additivity** | the value of a batch ≈ sum of point values | information across a batch is **submodular**, so greedy top-`k` buys `k` copies of one thing | property of the *objective*, not the data |

These are not competing explanations of one phenomenon. They are **different terms of the same
expression**, and a given task can fail any subset of them. C1 and C4 are about the algorithm; C2
and C3 are about the world.

**The theoretical spine already exists.** Classical results say adaptivity's advantage is governed
by problem-dependent quantities — the geometry of the hypothesis class under the data distribution
(the disagreement coefficient), and the noise regime (margin/noise-exponent conditions), with the
advantage collapsing to nothing in the agnostic high-noise limit. Batch information gain is
submodular, so greedy selection has known suboptimality. None of this is new theory.

**What is missing is the practical inverse.** These quantities are stated as *analysis* tools —
things you can bound if you already know the problem. Nobody routinely *estimates* them before
deciding whether to run active learning. Practice instead reports empirical wins on benchmarks whose
conditions were never checked, which is why the literature contains both confident successes and
confident failures on superficially similar tasks.

## 2. The question this thesis asks

> **Can C1–C4 be estimated *ex ante* — from unlabelled data plus a small pilot — accurately enough
> to predict whether adaptive sampling will beat i.i.d. sampling on a given task, and by how much?**

Three sub-questions, in increasing ambition:

1. **Decomposition.** Given a task where AL fails, can we attribute the failure to C1–C4? This
   requires interventions that vary one term while holding the others fixed.
2. **Prediction.** Can a cheap diagnostic, computed before spending the label budget, predict the
   sign — and ideally the size — of the AL-versus-random gap?
3. **Repair.** Where the binding constraint is C1 or C4 (algorithmic), does fixing it recover the
   gap? Where it is C2 or C3 (the world), is *no* acquisition rule going to help, and can we say so
   with confidence rather than by exhaustion?

A negative answer to (2) is itself a result: it would say the decision to run AL is not knowable in
advance, which is worth establishing rather than assuming either way.

## 3. Why this is not a chemistry project

The subject is sample-efficient learning. Chemistry supplies a testbed with three properties that
are hard to obtain otherwise, and each one makes a different condition bite:

- **Genuine, irreducible label noise** (wet-lab high-throughput measurements) — makes **C2**
  non-trivial. Synthetic benchmarks usually have noise that is either absent or artificially
  injected and therefore known.
- **Label costs spanning orders of magnitude** (seconds to hours per label, by method) — makes the
  `÷ c(x)` term real rather than notational.
- **A real downstream decision** (a search procedure consuming the model) — makes **C3** measurable
  rather than hypothetical. Most AL papers stop at held-out accuracy and so cannot see C3 at all.

DFT is not the subject. It is one of the label sources, and only in the extension.

## 4. Evidence we already hold, mapped onto the conditions

Assembled *after* the framing, and deliberately not treated as the starting point. All of it is
suggestive, none of it is decisive, and some of it is confounded.

**On C1 (estimability).** Predicted `σ` was nearly orthogonal to realised error on real HTE data —
Spearman **ρ = 0.042** (GP), **0.144–0.146** (ensembles). If that ranking is the proxy, it carries
almost no signal. *Confound:* one arm's estimator was MC-dropout, a weak posterior approximation, so
this may measure our implementation rather than the condition.

**On C2 (reducibility).** In the same data the structured signal was **aleatoric**, with the
epistemic component behaving like noise. If that holds, high-uncertainty points are the *least
reliably labelled* ones, and acquisition should be **worse** than random — a sharper prediction than
"no better", and one nobody has checked.

**On C3 (actionability).** A sister project refuted decision-aware training at scale and generalised
the reason as *regret-relevant sufficiency*: model quality stops mattering above a threshold set by
the downstream budget and search. Independently, our own comparison had the same shape — objective
*structure* mattered, uncertainty machinery did not.

**On C4 (batch additivity).** Our existing implementation selects by greedy top-`k` at **batch size
100**, with no diversity term. Under submodularity that is expected to be badly suboptimal.
This is an *instance* of C4, not evidence about it — it tells us our own prior negative may be
uninformative about C1–C3, because C4 was violated by construction. **The first job is therefore to
remove this confound, not to interpret it.**

**A measurement caveat that touches everything above.** The existing runs use **two seeds**. AL
curves are unusually exposed to initial-design pseudo-replication: if strategies share an initial
labelled set and few seeds exist, the between-strategy difference is confounded with the variance of
one draw. In the sister project this collapsed four headline results, one reversing sign. Nothing
above should be treated as established until it is re-run with the design varying independently
across strategy and repeat.

## 5. What the thesis would produce

- A **decomposition protocol**: interventions that isolate C1–C4 on a given task.
- An **ex-ante diagnostic** and its validation — the deliverable we would most value, and the
  question the sister project put to us and neither tree can answer.
- A **corrected empirical picture** for at least one real, noisy, decision-coupled task, replacing
  a currently underpowered and confounded negative.

---

*Reference list to be assembled at proposal stage. Per project rules, every citation must be
verified against Crossref/arXiv metadata before it is written down — the theoretical results named
in §1 are standard, but their attribution must not be reconstructed from memory.*
