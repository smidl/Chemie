# The DFT oracle works. What now?

**Date:** 2026-08-18 · Assessment against the V-arm ladder and Jindřich's `to_be_probed.md`.

## Where the oracle stands

Validated: three reactions, DLPNO-CCSD(T) single points on autodE/ORCA geometries land at **−0.73,
+0.92, −0.88** kcal/mol against BH9, mean absolute **0.84**, signs differing. Every TS confirmed by a
single imaginary mode. Cost 45–90 min per reaction at 17–21 atoms, plus ~11 min to rescore.

That was the goal set in July, and it is met. **The oracle is not the problem any more.**

## Are we ready to build active learning around it? — No, and the reason is not the oracle

An acquisition loop needs four things. We have three:

| | status |
|---|---|
| a validated expensive oracle | ✔ n=3, ±1 kcal/mol at the reference method |
| a cost model | ✔ measured, per reaction and per rescore |
| a cheaper rung with known error | ✔ AIMNet2 on BH9: 16.70 general, 4.728 routed |
| **a downstream decision the oracle changes** | **✘ missing** |

We can compute barriers well. We cannot yet say **what a barrier buys**. The link from a barrier to
a planning decision — through ξ_f, through route ranking — has never been established, and until it
is, an acquisition function has no objective to optimise. Acquiring labels to reduce barrier error
presumes barrier error is what limits the decision. Nobody has shown that.

This is the same gap that has recurred all year under different names: DecisionBO's **regret-relevant
sufficiency**, condition C3 in the thesis framing, our own finding that objective *structure* beat
uncertainty machinery. Building an AL loop now would be optimising an oracle against no requirement.

**The next experiment is not a method. It is a requirement.** Take existing route sets, perturb the
barriers by ±1, ±3, ±8 kcal/mol, and measure when the route ranking changes. That gives the accuracy
the planner actually needs. It is cheap — no new chemistry, existing data — and it determines
everything downstream:

- if ranking is stable to ±8, the DFT rung is **already over-engineered** and the cheap rungs suffice;
- if it turns on ±1, then DFT is necessary and the acquisition question becomes real;
- either answer is publishable, and either answer redirects the ladder.

## Unifying with other methods

The ladder is currently RDKit/SynRBL → ReactionT5 → GFN2-xTB → AIMNet2 → DFT → CCSD(T), but each rung
was measured on a **different set with a different definition**. Jindřich's BH9 work is the first
common yardstick — all 449 reactions, separated-reactant referencing, molecularity recorded.

Unification means finishing that: every rung on BH9, same definition, same accounting. xTB has never
been measured there. That is a small, bounded job and it belongs with him.

## Do we have enough methods? — Yes; too many, and that is the risk

His `to_be_probed.md` is a good piece of work — it records negatives (Gaussian, TURBOMOLE: credible
but overlapping) rather than only candidates. Assessed against our objectives:

| candidate | aligned? |
|---|---|
| **RGD1** (dataset, 176 992 reactions) | **yes, most of all** — and it is not a method. It ships TSs, barriers, endpoint geometries, frequencies **and atom mappings**, which is exactly what his BH9 Step 2 is blocked on, and it supports separating mechanism, geometry, conformer and barrier tests |
| **ML-FSM**, **React-OT** | yes *if* throughput is the constraint — both are cheap TS generation feeding DFT refinement rather than replacing it. React-OT reports ~0.39 s per TS |
| **YARP** | aligned with a *different* objective — open-ended mechanism/product discovery, i.e. the unowned completion layer, not validation |
| UMA/MACE, Sella, MAPLE, DeePEST-OS | not yet — alternatives to rungs that already work, or integration platforms |

**The binding constraint is not method availability.** It is that we cannot say what accuracy the
decision needs, so any new rung is unfalsifiable shopping. Adding ML-FSM would make TS search
cheaper; we do not know whether TS search cost is what limits us.

## Recommendation

1. **Do not start AL around the oracle yet.** Run the barrier-perturbation sensitivity test first —
   it costs no chemistry and it decides whether the loop is worth building.
2. **Adopt RGD1** from his list, as a dataset rather than a method. It unblocks Step 2 and gives the
   mechanism/geometry/conformer/barrier decomposition its own testbed.
3. **Finish the yardstick** — xTB on BH9, same definition as the rest. Bounded, and his.
4. **Defer everything else** until (1) returns a requirement. Then the choice among ML-FSM, React-OT
   and the MLIP backends becomes an engineering decision with a target, instead of a preference.
