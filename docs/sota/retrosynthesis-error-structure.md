# Our angle — the mechanism behind a documented gap, and the first fitted ξ_f marginal

Core: [[sota/retrosynthesis-error-structure]] · local, 2026-08-28

## Verdict on novelty, stated before the enthusiasm

**The phenomenon is documented; the decomposition is not.** `hassen2022_retrosynthesis-gap` and
`torrenperaire2024_models-matter` (same group, workshop then Digital Discovery) already established
that single-step top-k does not predict multi-step solvability, with numbers — LocalRetro 80.6 % vs
AZF 50.6 % solvability under Retro*-extended, and "high solvability does not always imply a high number
of solved routes" (Chemformer 8.04 solved routes/molecule against MHNreact's 56.6). `maziarz2024_syntheseus`
reaches the same conclusion from the metrics side.

So **we cannot claim the gap.** What we can claim is a *mechanism* for part of it:

> Proposer error is a property of the **individual reaction**, not of the **route**
> (ICC ≈ 0.04–0.05 over routes; cross-model Pearson r = 0.35 with 2.17× shared-miss enrichment).
> A step-level average therefore *cannot* predict a route-level outcome — which is exactly what those
> papers observed and did not explain.

That is a real but modest contribution: an explanation for a known negative, measured on 5757 recorded
PaRoutes steps across two architecturally unrelated proposers agreeing to 0.1 pp on recall@20.

**Also occupied:** rank calibration. RetroRanker (2023), Retro-Rank-In (2025), and chemist-aligned
diverse ensembling (arXiv 2412.05269) are all in this space — the last being the nearest published
relative of our "disagreement carries signal" reading of r = 0.35. Do not present that as new.

## What appears genuinely unexamined — and it is the stronger result

`tripp2024_retrofallback` sets **both halves of ξ_f by hand**: the marginal at a constant 0.5 or
0.75 decaying with template rank (eq. 40), the correlation by an assumed Morgan-fingerprint kernel
(`K(r,r)=1`, `noise_var=1e-6`). Nothing is fitted, and no follow-up appears to have fitted it. We just
measured the curve it guesses at (`admissibility/scripts/E1_marginal.py`, from the D1/D2 runs):

| rank | empirical P(proposal is the recorded reaction) — AZF | ReactionT5 | Tripp 0.75/r^0.1 |
|---|---|---|---|
| 1 | 0.5595 | 0.6130 | 0.7500 |
| 2 | 0.1103 | 0.0815 | 0.6998 |
| 5 | 0.0149 | 0.0109 | 0.6385 |
| 10 | 0.0030 | 0.0038 | 0.5957 |
| 50 | 0.0002 | — | 0.5072 |

Fitted decay: **p ≈ 0.533 / r^2.152** (AZF) and **0.285 / r^1.825** (ReactionT5), against the assumed
**0.75 / r^0.100** — an exponent **18–22× steeper**. At rank 1 the assumption is only ~1.2–1.3× optimistic;
by rank 10 it is ~160–200× optimistic and by rank 50 ~2500×. **The assumed marginal is essentially
rank-independent (0.75 → 0.51 across 50 ranks) where the data falls three orders of magnitude.**

**Why this matters for the algorithm, not just the calibration.** Tripp's own explanation of
retro-fallback's advantage is that the reaction model "tends to output many similar reactions, which can
be used to form backup plans". Those backups are drawn from exactly the low-rank region the marginal
over-values. So an unfitted, near-flat marginal is what makes hedging look valuable.

## The caveat that must travel with this, and it is severe

Precision-against-the-record is a **lower bound on feasibility.** A rank-10 proposal that is not the
recorded reaction may be perfectly feasible — this is Maziarz's pitfall S1 (the dataset records one of
many valid routes), and the multi-modality result on our own side put the likelihood–exact-match gap at
18.5 pp. So the 2500× figure is *not* a claim that the marginal is wrong by 2500×; the truth lies
between our curve and something higher, and **only chemist labels can locate it.**

That makes this the sharpest available argument for the Němec conversation: our lower bound and a
published planner's assumption differ by orders of magnitude, and the quantity that separates them is
exactly what a synthetic chemist can supply. Same for `w` — see `../barrier-accuracy-requirement.md` §3.

## Positioning, and it is not sim2science

The obvious theoretical home (`sim2science`, our sister project) is a **BO/DFO benchmarking** paper.
Recasting an AND/OR-graph planning result in trust-region and regret-floor vocabulary would cost more
boilerplate than the shared abstraction is worth. **Owner's call, 2026-08-28: do not route this through
sim2science.** The natural venue is the one the gap literature itself uses — Digital Discovery, where
`torrenperaire2024_models-matter` and `maziarz2024_syntheseus`-shaped methodological work already lives.
sim2science can cite this as a native-simulator instance; we should not contort into its frame.

## Contribution as it currently stands, honestly ranked

1. **A fitted ξ_f marginal** for a published probabilistic planner, and the demonstration that the
   assumed one is near-flat where reality is steep. Needs the S1 caveat and, ideally, labels.
2. **The variance decomposition** — error is per-reaction, not per-route — as the mechanism for a
   documented gap. Model-independent across two architectures.
3. **Two by-products**: AZF/ReactionT5 single-step recall on PaRoutes reference steps, and the
   representability bounds (60.10 % of routes fully inside AZF top-50; 7.52 % of steps outside top-20
   for both models).
