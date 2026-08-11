# What kind of noise, precisely

**Date:** 2026-08-11 · Sharpens `thesis-A-scope.md`, which said "label noise" where it should have
said something much more specific.

## Homoscedastic noise is not the problem, and saying so matters

Under constant noise variance σ² across the input space, the model's total predictive variance at a
point is

```
Var_total(x) = Var_epistemic(x) + σ²
```

and σ² is a **constant offset**. Adding a constant does not change an ordering. So acquisition by
total predictive uncertainty still ranks points by their *epistemic* variance, which is exactly what
it is supposed to do. A GP with a learned homoscedastic noise term handles this cleanly by
construction, and this is the regime where the standard machinery is well behaved.

Homoscedastic noise does have an effect, but a different one: it lowers the **ceiling**. With a high
noise floor the model saturates early, every strategy converges to the same attainable error, and
the active-learning advantage shrinks because there is less total learnable signal — not because the
ranking failed. That is a *sufficiency* effect (C3), not an *estimability* effect (C1), and it
should be reported as such rather than conflated with what follows.

**So "how much noise" is the wrong independent variable.** A threshold on scalar noise magnitude
would be measuring the sufficiency ceiling and mislabelling it.

## The problem is heteroscedasticity, and it is a ranking inversion

Under noise that varies with the input, `σ²(x)`:

```
Var_total(x) = Var_epistemic(x) + σ²(x)
```

Now the two terms compete for control of the ordering. Define the quantity the thesis is actually
about:

```
        range of σ²(x) over the pool
  R  =  ─────────────────────────────
        range of Var_epistemic(x) over the pool
```

- **R ≪ 1** — epistemic variation dominates; ranking by total uncertainty ≈ ranking by epistemic;
  acquisition behaves as intended.
- **R ≫ 1** — the aleatoric term dominates; ranking by total uncertainty is **ranking by
  noisiness**. The sampler then preferentially buys the *least informative* labels, and should be
  **worse than random**, not merely equal to it.

This is a much sharper claim than a noise threshold: it predicts an **inversion**, with a location
(R ≈ 1), and it explains why the published literature is split without anyone having to be wrong.
Tasks whose noise happens to be near-uniform show gains; tasks with strongly varying measurement
reliability show nulls or reversals.

## The moderator: can the model decompose, and does acquisition use the right part?

Heteroscedasticity is only fatal if the acquisition function cannot see past it. Three cases, all
already implemented in the group's testbed as separate strategies:

| acquisition on | under homoscedastic noise | under heteroscedastic noise |
|---|---|---|
| **predictive / total** | fine — constant offset | **fails; predicted to invert above R ≈ 1** |
| **epistemic only** | fine | **fine, *if* the decomposition is accurate** |
| **aleatoric only** | ≈ random | **actively harmful — a designed negative control** |

So the experiment is a **2 × 3 factorial**, not a single dose–response curve: noise structure
(homo- / heteroscedastic, with R swept) × acquisition target (predictive / epistemic / aleatoric).
The aleatoric arm is not a curiosity — it is the positive control for the failure mechanism. If
"acquire the noisiest points" does *not* underperform random when R is large, the proposed mechanism
is wrong and we would know it immediately.

**And the estimator is no longer a robustness check — it is part of the mechanism.** A GP with a
homoscedastic noise term is **mis-specified** under `σ²(x)`: it has nowhere to put the varying noise
except into the kernel, contaminating the epistemic estimate it is supposed to supply. A model with
an explicit input-dependent noise head, or any estimator that separates the two components, should
not fail the same way. That converts "does the estimator matter" from a vague robustness question
into a specific, falsifiable prediction about mis-specification.

## What this connects to in the group's own results

Our own audit found predicted σ nearly orthogonal to error (ρ 0.042 GP, 0.144–0.146 ensembles) on
real HTE data, and separately that **the structured signal was aleatoric while the epistemic
component behaved like noise**. Read through the framing above, those are not two findings but one:
they are the signature of **large R with a homoscedastic-noise estimator**.

The sister project's boundary test was explicitly aimed at the heteroscedastic regime, where gains
were predicted — and that is where we measured σ ⊥ error, with the caveat that one arm's epistemic
estimator was MC-dropout, a weak approximation. Under the framing above, a weak epistemic estimator
and a large R are *confounded*: both produce an uninformative ranking. **Separating them is a
contribution the sister project cannot make**, because its problems are deterministic and R is
undefined there.

There is also recent work on prior-fitted networks that decouple epistemic and aleatoric components;
whether such a model raises the R at which acquisition inverts is a natural extension, and the
reference must be located and verified before it is cited.

## Consequences for the proposal

- **Independent variable:** not noise magnitude but **R**, the ratio of aleatoric to epistemic
  dynamic range across the pool — swept by constructing `σ²(x)` with controlled input dependence.
- **Primary hypothesis:** the advantage of predictive-uncertainty acquisition over random decreases
  with R and **changes sign** near R ≈ 1; epistemic-only acquisition does not, to the extent the
  decomposition is accurate.
- **Homoscedastic arm:** retained as a control, with the expectation of **no ranking effect** — and
  any effect there is attributed to the sufficiency ceiling, not to acquisition.
- **Real-data question, sharpened:** not "how noisy is this dataset" but **"is its noise input-
  dependent, what is its R, and can our estimators recover the epistemic part?"** Estimating `σ²(x)`
  requires replicates, so the replicate check is no longer a detail — it is the measurement the
  real-data validation depends on.
