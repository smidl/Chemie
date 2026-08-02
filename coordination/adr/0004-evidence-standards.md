# ADR 0004 — Evidence standards for this tree

Date: 2026-08-02 · Status: accepted · Owners: vsmidl

## Context

Two things forced this. First, an internal audit (2026-07-30) found that of roughly nine standing
negative results, only two or three would survive review: the rest were single-setup, n=2, or
confounded. In one week, four separate "findings" of mine dissolved under a cheap control — three
mechanistic hypotheses for a NEB failure, and both of my challenges to the Draslovka diagnosis. In
every case the control cost minutes and the wrong story was already written down.

Second, the sibling tree `~/zcu/PFN4BOrevisited/DecisionBO` has been down this road further and has
paid for the lessons. Their founding thesis — train the surrogate for the decision rather than the
likelihood — was refuted on its own turf, and the refutation produced a reusable standard. Rather
than invent our own, we adopt theirs with attribution.

## Decision

The following are binding for any result this tree records, publishes, or acts on.

**1. Mechanism first; downstream is confirmation.** Lead with a low-variance mechanism metric,
measured **in the decision-relevant region and off it**. Treat the downstream outcome (solve rate,
route quality, regret) as noisy confirmation, not as the primary signal. **Always pair an off-region
parity guard** so a gain cannot be bought by wrecking global fit. *(DecisionBO ADR-0002; it is the
design our mechanism-kernel null lacked, and it names our failure: "acquisition insensitivity" —
surrogates that rank candidates alike pick the same points and yield null downstream deltas.)*

**2. A negative requires a passing positive control in the same run.** A run whose control fails
cannot distinguish "the input is bad" from "the instrument cannot handle this input". We shipped a
0-of-11 result whose designated control had failed, and it was wrong.

**3. Report the tool's state, not just its verdict.** Statuses must separate *tool failed* from
*hypothesis false* — `OK` / `OK_BUT_UNCONVERGED` / `CLASHED_INPUT` / `IMPLAUSIBLE_OUTPUT` /
`INDETERMINATE`. A diagnostic that cannot fail safe manufactures negatives.

**4. Seeds: `run seed = base + s + 9973·i`.** A run seed shared across problem instances silently
reduces design replication to the number of seed values. This collapsed **four** DecisionBO headline
results at p ≲ 0.003, one reversing sign. **n ≥ 32 paired with a Wilcoxon test is not sufficient if
the design is shared.** The flaw also *suppresses* power, so it cuts both ways.

**5. Never accept a training-objective result at pilot scale.** DecisionBO's ranking-loss advantage
was +0.097 at low capacity, +0.028 at pilot, **−0.007 at convergence**. Sweep capacity before
believing an objective comparison. Their generalisation — *regret-relevant sufficiency*: a model
influences the decision only up to a quality threshold, above which the outcome is set by the
acquisition, the search and the budget.

**6. Random is the bar, not a formality.** MALIBO scored *below* random on the only discriminating
task in their panel, and random arm-mixing beat every engineered fixed arm.

**7. Carry the dumb classical baseline.** Py-BOBYQA beat their entire GP stack by ~16× geometric mean
on deterministic problems. Our analogue is SAScore and any well-tuned classical planner.

**8. Reproduction gate.** No external method enters a head-to-head until our run reproduces *that
paper's* headline number on *that paper's* benchmark. "Could not reproduce" is a recorded outcome,
never a silent strawman. This caught an inversion in their tree that was their adaptation's artifact,
not the method's.

**9. Pre-register where the lever must NOT pay.** Designate cells in which no gain is possible; a
gain there is a red flag, not a bonus.

**10. Guardrail: keep refuted hypotheses as baselines.** No "the learned thing is needed" claim is
admissible until it beats the strong simple alternatives on the same problem. **Binding here: no
learned-`h` claim until it beats SAScore *and* MEEA\*-PC.**

**11. A negative is scoped to its implementation** unless a second, differently-built arm agrees.
Our epistemic-MCTS negative tested one crude σ-bonus, not the hypothesis; we then read it as general.

## Why

These are cheap and they caught real errors. The pattern across both trees is that single-instance
evidence reliably produces confident wrong stories, and that the controls which catch them —
decoys, positive controls, capacity sweeps, a random arm — cost minutes against days of wasted
compute. In this tree, 81 minutes of DFT went into inputs that a two-line distance check would have
rejected, and 13 hours went into confirming what a 4-minute proxy had already shown.

## Consequences

- Existing results are **not** grandfathered. Two are already flagged for re-checking under §4 and
  §5: retro-planning's L\* verdict-flip (published in the briefing) and the rank-vs-value comparison.
- Claims already published outward must be scoped to what the evidence supports, not to what we
  believed when we wrote them.
- Attribution: standards 1 and 4–10 are adopted from DecisionBO's ADRs 0002/0003/0005/0009 and its
  results log. Where we cite them as motivation we cite them as *their* finding, not ours.
