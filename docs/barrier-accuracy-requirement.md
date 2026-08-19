# What barrier accuracy does the planner actually need?

**Date:** 2026-08-18 · `scripts/K1_perturb.py`, jobs `11367242` (ρ=0) and `11367273` (ρ=1) ·
Data: retro-fallback on the 190 hard targets, three feasibility models, 133–141 rankable targets each

> **Framing correction, 2026-08-19.** DFT is deterministic: the same geometry and settings give the
> same number every time. So a rung's error is **not noise** — it is a fixed function of the reaction.
> The experiment below draws errors from a distribution, which is the wrong picture of the mechanism,
> though not of the arithmetic.
>
> What the two columns really contrast is whether the error is **common to the steps of a route** or
> **varies between them** — a property of the error *function*, not of a noise process. On that
> reading the conclusion stands unchanged, and reads more cleanly: what matters is whether a
> functional is wrong in the same direction for every step of a route.
>
> What does not survive: the 20 repeats and the seed discipline are arithmetic, not statistics. They
> average over *possible reactions*, not over reruns, since a rerun would return the identical number.
> The flip rates should be read as expectations over which reactions a route happens to contain.
>
> This also exposes an axis the experiment ignored entirely — the **numerical parameters** of the
> calculation, which are deterministic and tunable. See `numerical-parameters.md`.

## The question

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

## Result — correlation beats accuracy, and not narrowly

Top-1 flip rate, `gp` arm (the other two agree within ~2 points):

| | **independent error (ρ=0)** | | | | **systematic error (ρ=1)** | | | |
|---|---|---|---|---|---|---|---|---|
| **w** | 0.84 | 3.80 | 4.73 | 16.70 | 0.84 | 3.80 | 4.73 | 16.70 |
| 0.593 | 91.0 % | 96.0 % | 96.3 % | 96.8 % | 10.4 % | 17.1 % | 17.4 % | 18.3 % |
| 2 | 65.5 % | 93.2 % | 94.6 % | 96.6 % | 6.2 % | 11.2 % | 12.3 % | 17.3 % |
| 5 | 36.5 % | 82.0 % | 87.1 % | 95.6 % | 5.6 % | 7.1 % | 8.4 % | 14.3 % |
| 10 | 20.7 % | 62.8 % | 70.4 % | 93.2 % | 5.6 % | 5.8 % | 6.2 % | 10.9 % |
| 20 | 14.4 % | 40.0 % | 46.8 % | 85.0 % | 5.6 % | 5.4 % | 5.8 % | 8.3 % |

**A 16.70 kcal/mol oracle with systematic error disturbs the route choice less than a 0.84 kcal/mol
oracle with independent error** — 8.3 % against 14.4 % at w=20, and 18.3 % against 91.0 % at Eyring.

Holding the map fixed at w=20: improving accuracy **20×**, from 16.70 to 0.84, buys 8.3 % → 5.6 %
under systematic error. Holding accuracy fixed at 0.84 and moving from systematic to independent
error costs 5.6 % → 14.4 %. **The correlation structure of the error matters more than its
magnitude.**

There is also a floor: under systematic error the flip rate stops improving at ~5.6 % however
accurate the oracle. That is the residual from a genuinely small 6.25 % median gap between the best
two routes — irreducible by any oracle.

## Which functionals have systematic error? BH9 already says

The correlation is not a free parameter — BH9's own Table V reports **both** MAE and mean error per
functional per reaction type, and `|ME|/MAE` is a direct proxy. For pericyclic reactions:

| functional | MAE | ME | \|ME\|/MAE | error is |
|---|---|---|---|---|
| **ωB97M-V** | **2.15** | **2.06** | **0.96** | highly systematic |
| PBE | 7.98 | −6.55 | 0.82 | systematic |
| PBE0 | 3.34 | −0.05 | **0.015** | essentially random |

**This inverts how the rung should be chosen.** PBE0 — autodE's default, and what we have been
running — is accurate but its error is near zero-mean, i.e. the bad case. ωB97M-V is both **more
accurate and far more systematic**, so it should be better on both axes. PBE is twice as inaccurate
as PBE0 yet 55× more systematic, and may well rank routes better despite being the worse oracle.

## What this changes

1. **Do not build active learning to reduce barrier error yet.** The experiment it would optimise
   shows accuracy is the second-order variable. An acquisition loop targeting MAE would spend
   expensive labels on the axis that matters least.
2. **Choose the functional by `|ME|/MAE`, not by MAE.** Concretely: switch autodE's high-level method
   from PBE0 to ωB97M-V and re-run the three walkthrough reactions. Cheap, and it tests the
   prediction directly.
3. **Measure our own error correlation.** ρ=0 and ρ=1 are the extremes; the real value is unmeasured.
   Our three PBE0 errors were −5.95, −2.98, −2.47 — all the same sign, suggesting more structure than
   BH9's class-wide ME of −0.05 implies, but n=3 cannot settle it.

## Limits

The map steepness `w` remains unknown and the answer depends on it — at Eyring nothing works, at
w=20 systematic error is tolerable. Establishing the barrier→feasibility map is therefore still the
prerequisite, and this experiment sharpens rather than removes that need. Per-step feasibility is
recovered as `feasibility^(1/n_rxn)`, i.e. assumed uniform across a route's steps. Top-1 flip is a
demanding criterion on a 6.25 % median gap; the top-10 Jaccard and Spearman columns in the raw output
are gentler and tell the same story.
