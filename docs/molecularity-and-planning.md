# Does the missing association entropy change the planning?

**Date:** 2026-08-08 · **Follows:** `barrier-definition-and-guards.md` ·
**Script:** `F0_molec.py`, `logs/molec-11320536.log`

**Short answer: no. It changes the barrier oracle's contract, not the search.** Below is the sizing,
including one correction to how I first stated the concern.

## The concern, stated precisely

A barrier reported as an electronic energy omits the association entropy: roughly **+10–15 kcal/mol**
of ΔG‡ at 298 K / 1 M for a step where two species combine into one transition state, and ~0 for a
step where one species rearranges. If the steps being scored are of mixed molecularity, the omission
is not a constant — it is a class-dependent bias that can invert rankings between classes.

## Why it does not reach the planner

**Route score compounds multiplicatively, not additively.** Retro-fallback's route feasibility is a
*product of per-step probabilities*, not a sum of barriers. My earlier phrasing — "any route-level
score that sums these barriers" — describes a system we do not have. There is no additive barrier
sum anywhere in the search.

**Barriers enter as a ranking signal, not as a cost.** The mechanism-kernel result (ρ 0.585 against
structural fingerprints' 0.417) is a rank correlation, and ξ_f is a learned probability. A bias that
is constant within a class is absorbed by any monotone calibration; only a *cross-class* bias
matters, and only in proportion to how mixed the classes are.

## How mixed are they — and a caveat on my own number

Fragment count on the reactant side across all 1 939 253 USPTO records:

| fragments | share |
|---|---|
| 1 | 4.1 % |
| 2 | 26.8 % |
| 3 | 20.9 % |
| 4 or more | 48.3 % |

**This is not molecularity and must not be read as such.** USPTO reactant sides list reagents,
catalysts and solvents alongside the true reactants, so the 4+ bucket is mostly spectators, not
four-body collisions. The number is the right one for the *placement* problem — every fragment has
to be embedded — and the wrong one for the entropy question.

For molecularity the honest sample is the balance-repaired `specialty_11`, where the reactant list
is mechanistic: **8 bimolecular, 1 termolecular, 1 five-body, 1 unimolecular**. So of the order of
**one step in ten is unimolecular**, the rest bimolecular or higher.

## What that implies

The affected minority is small but the bias on it is **directional and chemically meaningful**.
Omitting the association entropy makes bimolecular steps look *better* than they are, so
intramolecular steps — cyclisations, rearrangements, ring closures — are ranked relatively *worse*.
Those are frequently the genuinely favourable steps in a synthesis, because intramolecularity buys
effective molarity. The bias therefore runs against exactly the class it should favour, on roughly
10 % of steps.

That is worth fixing and not worth re-planning around.

## Recommendation

1. **Do not change the planning.** Neither academic priority — uncertainty-aware planning, arbitrary
   conditioning — touches the barrier definition, and the search contains no additive barrier sum.
   Changing course here would be re-planning around a correction, not a finding.
2. **Change the oracle contract.** Every barrier this tree reports should carry its **molecularity**
   alongside the number, so the standard-state term can be applied or ablated after the fact. That
   costs a field, not a calculation.
3. **Report ΔG‡ where it is affordable.** Thermal and entropic corrections need frequencies at the
   endpoints and the highest image, which PySCF/pysisyphus already support. On the six walkthrough
   reactions this is affordable and belongs in the walkthrough as its own stage; at scale it is not,
   which is why (2) exists as the cheap fallback.
4. **Pre-register the null** (ADR 0004): applying a per-molecularity standard-state correction
   changes no downstream ranking we currently report. Then test it. The mechanism-kernel ρ = 0.585
   was measured on a set whose molecularity mix is not recorded — if that set is uniformly
   bimolecular, the result is untouched and we should say so; if it is mixed, it needs the check
   before being quoted again.

Item 4 is the only one with any chance of moving a published number, and it is a few lines of
analysis on data we already hold.
