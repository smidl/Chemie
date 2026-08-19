# Our angle — error structure vs magnitude for barrier oracles

Core: [[sota/oracle-error-structure-vs-magnitude]] · local, 2026-08-19

## Our question

We spent July and August validating a DFT barrier oracle to ±1 kcal/mol, then asked what accuracy the
*planner* actually needs. Perturbing real route sets by our measured rung errors gave the answer we
did not expect: **a 16.70 kcal/mol oracle with error common to a route's steps disturbs the chosen
route less than a 0.84 kcal/mol oracle whose error varies between them** — 8.3 % against 14.4 % top-1
flip rate. Details in `../barrier-accuracy-requirement.md`.

## The gap we exploit

The core survey finds the two halves of this established separately and never joined. That is our
opening, and it is narrow enough to state in one sentence:

> Choose the electronic-structure method for a *ranking* task by `|ME|/MAE`, not by MAE — because the
> task is ranking-and-selection, not estimation, and the benchmark already reports the statistic.

Concretely, from BH9's Table V on pericyclic reactions: ωB97M-V is 2.15/2.06 (ratio 0.96), PBE
7.98/−6.55 (0.82), and **PBE0 3.34/−0.05 (0.015)** — near-zero bias with substantial scatter, i.e.
the bad case, and it is autodE's default and what we have been running all week.

## Which subset matters, and why for us

- `gorder2019` is the formal home. Our ρ=1 arm *is* CRN; our ρ=0 arm is independent sampling. This
  converts our result from an oddity into an instance of a theorem.
- `kaplan2023` and `kanungo2024` tell us *why* a functional's error has structure — density- versus
  functional-driven decomposition, and cancellation between them. That is the mechanism that decides
  whether error is common across a route's steps.
- `prasad2022` supplies the numbers, already tabulated, for the criterion we propose.

## Our positioning, and the honest limits

The contribution is small and specific: **applying a known selection principle to a method choice
where nobody applies it**, with a measurement on real planner routes to show it bites. We are not
proposing new theory.

Three limits we should not paper over. `|ME|/MAE` measures correlation across reactions *within a
class*, not across the steps of one route — and a route mixes classes, so the proxy is indicative, not
a measurement. Our own error correlation is unmeasured: ρ=0 and ρ=1 are extremes, and our three PBE0
errors (−5.95, −2.98, −2.47) are all one sign, which hints at structure but at n=3 settles nothing.
And the whole result is conditional on the barrier→feasibility map, whose steepness is unknown; at the
Eyring limit no rung survives.

## Next action implied

Switch autodE's high-level method from PBE0 to ωB97M-V and re-run the three walkthrough reactions.
Cheap, and it tests the prediction directly.
