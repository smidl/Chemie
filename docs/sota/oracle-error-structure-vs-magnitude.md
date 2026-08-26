# Our angle — error structure vs magnitude for barrier oracles

> **CORRECTED 2026-08-26 — the worked example below is inverted by our own measurement.**
> The "next action implied" at the foot of this page (ωB97M-V on the three walkthrough reactions)
> ran as job `11381115` and returned: ωB97M-V errors −1.56 / +1.32 / −0.54, i.e. **MAE 1.14 but
> |ME|/MAE 0.23** — signs vary. On the same geometries PBE0 is **3.80 / 1.00**, perfectly
> one-signed. So on the criterion this page proposes, **PBE0 is the best of the three and ωB97M-V
> is the scatter case** — the reverse of the BH9 Table V prediction used below.
> Likely mechanism: accuracy and systematicity are not independent axes, because removing
> systematic error is what makes a method accurate; a high |ME|/MAE is the signature of a large
> uncorrected bias. **What survives:** the perturbation result (8.3 % vs 14.4 %) and the framing
> that error *structure* dominates error *magnitude*. **What does not:** reading |ME|/MAE off a
> published benchmark table as an actionable method-selection rule. Full record and limits:
> `../wb97mv-rescore.md`. Do not pitch this angle externally in its current form.

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

## Next action implied — RUN, AND IT FAILED (2026-08-26)

~~Switch autodE's high-level method from PBE0 to ωB97M-V and re-run the three walkthrough
reactions.~~ Done, job `11381115`. It tested the prediction directly and the prediction lost: see
the correction banner at the top and `../wb97mv-rescore.md`.

**The real next action** is no longer cheap. Measuring our own error correlation needs barriers
across several reaction families on shared geometries at n ≫ 3. At 45–90 min per reaction that is a
campaign, not a run — which is the argument for adopting **RGD1** (176 992 reactions shipping TSs,
barriers, endpoint geometries *and* atom mappings) instead of generating it. Until that exists this
angle has a measured result (8.3 % vs 14.4 %) and no validated selection rule.
