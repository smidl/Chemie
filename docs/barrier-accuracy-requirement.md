# What barrier accuracy does the planner actually need?

**Experiment:** 2026-08-18 · `scripts/K1_perturb.py`, jobs `11367242` (ρ=0) and `11367273` (ρ=1) ·
Data: retro-fallback on the 190 hard targets, three feasibility models, 133–141 rankable targets each
**Rewritten 2026-08-28**, when ρ stopped being a free parameter. Audit trail of what was withdrawn is
at the foot of the page — nothing here is silently edited.

## Answer, up front

**ρ ≈ 0, measured, model-independently. So barrier accuracy is the first-order variable and the
oracle ladder matters.**

This document originally read the opposite way. The experiment sweeps a parameter ρ — whether the
oracle's error is *common to the steps of a route* or *varies between them* — and found that the
correlated case is far more forgiving. What it could not do was say which case we live in. That was
settled on 2026-08-27/28 by measuring the error structure of the estimator that is actually in the
planning loop (`retro-pfn/path-correlation/`): **ICC ≈ 0.04–0.05 over routes, for two architecturally
unrelated proposers.** Independent, not common. So the ρ = 0 column is the live one.

## The question and the method

We validated the DFT oracle to ±1 kcal/mol without ever establishing what a barrier *buys*. This
measures the requirement: perturb each step's barrier by a rung's **measured** error, recompute route
feasibility, and ask whether the route you would act on changes.

Perturbations are our own numbers — 0.84 (DLPNO rescore, n=3), 3.80 (PBE0, n=3), 4.73 and 16.70
(AIMNet2 routed and general, 449 BH9 reactions). The barrier→feasibility map is unknown, so its
**steepness** `w` is swept: `ξ = sigmoid(−(B−B₀)/w)`, `B₀` = 12.84, BH9's median forward barrier.
Eyring is the `w → RT` limit (0.593 kcal/mol at 298 K).

Reported as the **top-1 flip rate**: how often the best route changes. Not a tie artifact — the
median top-1/top-2 gap is **6.25 %**, the top-100 spread 52 %, and the median count of routes exactly
tied with the best is **1**.

> **Framing correction, 2026-08-19 (still stands).** DFT is deterministic: the same geometry and
> settings give the same number every time. So a rung's error is **not noise** — it is a fixed function
> of the reaction. The experiment draws errors from a distribution, which is the wrong picture of the
> mechanism though not of the arithmetic. What the two columns really contrast is whether the error is
> **common to the steps of a route** or **varies between them** — a property of the error *function*.
> Consequently the 20 repeats are arithmetic, not statistics: they average over *possible reactions*,
> not over reruns. Read the flip rates as expectations over which reactions a route happens to contain.
> This also exposed an axis the experiment ignored — the **numerical parameters** of the calculation,
> since measured at 0.047 kcal/mol total and closed (`numerical-parameters.md`).

## Result

Top-1 flip rate, `gp` arm (the other two agree within ~2 points). **The left half is the applicable
half.**

| | **independent error (ρ=0) — MEASURED REGIME** | | | | systematic error (ρ=1) — not our regime | | | |
|---|---|---|---|---|---|---|---|---|
| **w** | 0.84 | 3.80 | 4.73 | 16.70 | 0.84 | 3.80 | 4.73 | 16.70 |
| 0.593 | 91.0 % | 96.0 % | 96.3 % | 96.8 % | 10.4 % | 17.1 % | 17.4 % | 18.3 % |
| 2 | 65.5 % | 93.2 % | 94.6 % | 96.6 % | 6.2 % | 11.2 % | 12.3 % | 17.3 % |
| 5 | 36.5 % | 82.0 % | 87.1 % | 95.6 % | 5.6 % | 7.1 % | 8.4 % | 14.3 % |
| 10 | 20.7 % | 62.8 % | 70.4 % | 93.2 % | 5.6 % | 5.8 % | 6.2 % | 10.9 % |
| 20 | **14.4 %** | **40.0 %** | **46.8 %** | **85.0 %** | 5.6 % | 5.4 % | 5.8 % | 8.3 % |

**In the measured regime, accuracy dominates.** At w = 20, moving from a 16.70 kcal/mol rung to a
0.84 kcal/mol rung takes the top-1 flip rate from **85.0 % to 14.4 %** — a 6× reduction in how often
you act on the wrong route. Even the intermediate rungs matter: AIMNet2-routed (4.73) sits at 46.8 %,
PBE0 (3.80) at 40.0 %.

The ρ = 1 column is retained because it is the correct contrast and it is what makes the result
interpretable: had error been route-common, a 20× accuracy gain would have bought only 8.3 % → 5.6 %
and the ladder would have been over-engineered. It is not the regime we are in.

There is also a floor, and it survives regardless: under systematic error the flip rate stops
improving at ~5.6 % however accurate the oracle — the residual of a genuinely small 6.25 % median gap
between the best two routes, irreducible by any oracle.

## What this changes

1. **Build the accuracy ladder, and active acquisition around it, on the original terms.** Accuracy is
   first-order in the measured regime, so an acquisition loop that spends expensive labels to reduce
   barrier error is optimising the axis that matters. This *reinstates* the orchestrator's
   active-acquisition thesis, which the 2026-08-26 reading had suspended.
2. **Adopt ωB97M-V as the working rung on cost-accuracy grounds.** MAE **1.14** at ~4.3 min/reaction
   against DLPNO's 0.84 at ~17 min (`wb97mv-rescore.md`) — a near-DLPNO rung at ~4× less compute. Not
   on error-structure grounds; see the audit trail.
3. **The remaining unknown is `w`, not ρ.** The answer still depends on the barrier→feasibility map's
   steepness: at the Eyring limit no rung survives (91–97 % flip across the board), at w = 20 accuracy
   buys a great deal. Establishing `w` is now the single prerequisite this experiment cannot supply,
   and it is a question for a **synthetic chemist** — what computed barrier makes a practitioner
   abandon a step — not for more compute.
4. **Route-level error structure is a live research direction, not a nuisance parameter.** ρ ≈ 0 is
   itself a finding: per-step difficulty is real and partly model-independent (cross-model Pearson
   r = 0.35, 2.17× shared-miss enrichment) yet does **not** aggregate into a route-level factor. See
   `retro-pfn/path-correlation/`.

## Limits

`w` remains unknown and the conclusion is conditional on it, as above. Per-step feasibility is
recovered as `feasibility^(1/n_rxn)`, i.e. assumed uniform across a route's steps. Top-1 flip is a
demanding criterion on a 6.25 % median gap; the top-10 Jaccard and Spearman columns in the raw output
are gentler and tell the same story. And the ρ measurement is of the **expansion policy's** error, not
the barrier oracle's — the policy was chosen because it is in the loop on every node while the oracle
is not in the loop at all, but the substitution is an assumption. The one hint about the oracle points
the same way: PBE0's error was one-signed within a *single* reaction family (3 pericyclics), and a
route mixes families.

---

## Audit trail — what this page used to claim

Kept per this tree's convention that corrections are dated rather than silent.

**WITHDRAWN 2026-08-28 — "correlation beats accuracy, and not narrowly", and item 1 "do not build
active learning to reduce barrier error yet".** Both were correct readings of the ρ = 1 column and
wrong about which column applies. ρ was an unmeasured free parameter presented as if the forgiving
case were the default. Measurement (`retro-pfn/path-correlation/README.md`; jobs `11422415`,
`11422605`): ICC over routes = 0.0421 (AZF log-rank), 0.0530 (ReactionT5 log-rank), 0.0323 / 0.0413
(miss), with within-route step pairs differing 97–98 % as much as random cross-route pairs, on 5757
recorded PaRoutes steps and two architecturally unrelated proposers matching to 0.1 pp on recall@20.
The general claim that error *structure* can outweigh *magnitude* is sound and remains the reason the
experiment was worth running; the claim that it does so **for us** does not survive.

**WITHDRAWN 2026-08-26 — "choose the functional by `|ME|/MAE`, not by MAE".** The test it proposed
(ωB97M-V single points on the three validated geometries, job `11381115`) inverted the prediction:
ωB97M-V measured MAE 1.14 with |ME|/MAE **0.23**, PBE0 3.80 with **1.00**, DLPNO 0.84 with 0.27 — so
PBE0, predicted "essentially random" from BH9 Table V, was the only one-signed rung. Reading |ME|/MAE
off a published table does not predict our own measurement on the same reaction class. Likely
mechanism: accuracy and systematicity are not independent axes, because a high ratio is the signature
of a large uncorrected bias. Full record in `wb97mv-rescore.md`.

The BH9 Table V figures the withdrawn criterion rested on, retained so the reasoning is auditable —
pericyclic subset: ωB97M-V 2.15 / 2.06 / 0.96 · PBE 7.98 / −6.55 / 0.82 · PBE0 3.34 / −0.05 / 0.015
(MAE / ME / |ME|÷MAE).
