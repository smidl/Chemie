# Master's thesis options — active learning (for Ayman)

**Date:** 2026-08-11 · Readiness assessed against: does the data exist, does a baseline exist, is
the question well-posed, and is it blocked on anyone else?

---

## A. When does active learning actually help? — **ready now**

**The question.** Uncertainty-guided acquisition is assumed to beat random. In this project it
repeatedly has not. Is that the *uncertainty estimator*, the *acquisition rule*, or the *task*?

**Why it is ready.** The testbed exists and runs. `/mnt/data/resynthesis/zhong-reactivity/`
reproduces Zhong et al., *Nat. Commun.* **16** (2025), "Towards global reaction feasibility and
robustness prediction with high throughput data and Bayesian deep learning" — binary reaction
feasibility on real wet-lab HTE data, with **five** uncertainty estimators already implemented (BNN
via SVI and NUTS, MC-dropout, deep ensemble, deep-kernel GP). On top of it, `zhong_al.py` already
implements **four acquisition strategies** — random, epistemic, predictive, aleatoric — producing F1
vs. labelled-budget curves from 100 to 2000 labels in batches of 100.

**The prior that makes it interesting.** Two independent negatives already exist here:

- our own uncertainty audit: predicted σ is essentially **orthogonal to error** (Spearman ρ 0.042
  for the GP, 0.144–0.146 for ensembles) on real noisy HTE data;
- the sister project (DecisionBO/PFN4BO) refuted the same thesis at scale, and contributed the
  "regret-relevant sufficiency" framing — a model influences the decision only up to a quality
  threshold, above which the outcome is set by budget and search.

**And the existing runs are inadmissible.** They use **two seeds**. Under our ADR 0004 that is not a
result — a shared design across instances silently reduces replication to the number of seed values,
and it collapsed four headline results in the sister project. So the first honest contribution is a
properly powered rerun (`run seed = base + s + 9973·i`), which is a week's work and immediately
worth more than what is there.

**Thesis shape.** (1) Power the existing comparison properly. (2) Decompose the failure — swap the
estimator with the acquisition held fixed, and vice versa, to separate "our σ is bad" from "the
acquisition is bad" from "the task is aleatoric-dominated and nothing can help". (3) Deliver an
**ex-ante diagnostic**: given a dataset and a model, predict whether AL will beat random *before*
spending the labels. That last item is the part the sister project explicitly asked us for and
nobody has.

**Risk.** It may confirm a negative. That is publishable when done properly — *"when does active
learning help in reaction property prediction, and how do you know in advance"* is a better paper
than another marginal win — but the student must be comfortable with it, and should be told at the
outset rather than discovering it in month five.

---

## B. Cost-aware / multi-fidelity active learning for the oracle ladder — **ready in weeks, most useful to us**

**The question.** We can evaluate a reaction at four wildly different costs. Given a fixed compute
budget, **which reactions get escalated, and to which rung?**

| rung | measured cost | measured accuracy |
|---|---|---|
| GFN2-xTB | seconds | — |
| AIMNet2 | **~43 s** endpoints | **MAE 4.76 kcal/mol** (n=100, exact geometries) |
| PBE0-D3BJ/def2-TZVP | **~71 min** (17 atoms, 1 core) | −5.95 vs reference on one reaction so far |
| DLPNO-CCSD(T) | hours | reference method |

**Why it is ready (nearly).** BH9 — 449 organic reactions with DLPNO-CCSD(T)/CBS references, nine
labelled classes, 57.5 % multi-fragment — is staged at
`/mnt/data/resynthesis/admissibility/data/BH9_SI/`. Transition1x gives 10 073 more. Every rung is
installed on RCI (xtb, AIMNet2, ORCA 6.1.1, NWChem 7.3.1, autodE 1.4.5). The one missing input is
per-rung error on BH9, which is the task just assigned to the physics-validation leaf — so this
becomes fully ready as that lands, and the two students would have a genuine interface.

**Thesis shape.** This is *multi-fidelity* active learning, a real ML topic with its own literature
(cost-aware acquisition, multi-fidelity BO). Deliverable: an escalation policy plus a measured
**error-versus-compute frontier**, against honest baselines — escalate at random, escalate by
predicted uncertainty, escalate by disagreement between rungs.

**Why we want it.** A retrosynthesis planner evaluates thousands of edges and can afford DFT on
almost none. The escalation policy *is* the product.

**Risk.** Depends on another student's output for the calibration data. Mitigable — he can develop
the policy on Transition1x, which needs nothing from anyone.

---

## C. Decision-focused active learning — **novel, highest risk**

**The question.** Acquire labels that change *the plan*, not labels that reduce prediction error.
Our own results say these are different: a rank-trained heuristic beat a value net, then lost to a
path-consistency-trained one; and model quality stopped mattering above a threshold.

**Why it is attractive.** It is the natural synthesis of this tree's two academic priorities, and it
is genuinely under-explored. **Why it is risky for a thesis:** it needs the planner in the loop, so
the student inherits an integration problem before he can run an experiment, and the sufficiency
result suggests the achievable effect may be small. Offer it as a stretch extension of A or B, not
as the primary topic.

---

## D. Active learning for the search heuristic — **not now**

Would overlap the owner's own line, and the evaluation protocol is currently unsettled — the
benchmark's OOD stratification was withdrawn on 2026-08-06 and its replacement does not exist yet.
Bad ground for a thesis that needs a stable metric.

---

## Recommendation

**A as the spine, B as the second half.** A is startable this week on existing code and data, gives
him a real result within a month (the powered rerun), and carries a question the field cares about.
B then turns the negative into something constructive and connects him to the physics leaf. If he
wants one topic rather than an arc, take **A alone** — it is self-contained and the diagnostic
deliverable is enough for a thesis.

**Before drafting:** he will need an RCI account **and membership of the `resynthesis` group**. The
previous student lost several weeks to exactly this — his account appeared the day he finished a
phase, and he is still not in the group. Worth starting that now rather than at the point he needs
it.
