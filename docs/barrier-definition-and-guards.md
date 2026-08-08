# Which barrier, and when to refuse one

**Date:** 2026-08-08 · **Implements:** `retrosyntesis/coordination/handover/reaction_complex.py`
(+4 tests, 15/15 pass) · **Evidence:** `out/endpoint_test.json`, `out/dft_confirm*.json`,
BH9 SI (`10.1021/acs.jctc.1c00694`)

## 1. Allowing negative barriers without weakening the other checks

**Yes — because the discriminator was never magnitude, it was cause.**

The tempting fix is a threshold: reject below −150 kcal/mol, accept above. That does not work. Our
own artefacts and real chemistry overlap:

| source | gap (HEI − endpoint_max), kcal/mol |
|---|---|
| corrupt endpoints, whole-molecule embedding | −46 677, −46 606, −46 059, −10 494 |
| **artefacts in the moderate range** | **−106.9, −38.0, −12.4** |
| real submerged barriers in BH9 | −1 to **−67.7** (19 of 449 = 4.2 %) |

A threshold anywhere in the overlap misclassifies one side or the other.

But sorting the same records by *cause* separates them completely:

| arm | endpoints | negative gaps |
|---|---|---|
| `D_ff_endpoints` | force-field, not optimised at the band's level | **3 of 3** |
| `A_supplied` | DFT geometry, **xTB band** — different surface | 1 of 4 |
| `E_fix_optimised_endpoints` | optimised at the band's own level | **0 of 4** |
| all same-surface optimised arms, pooled | | **0 of 12** |

Every negative gap we have ever recorded traces to one thing: **an endpoint that is not a converged
minimum of the band's own surface.** That is not a proxy for the artefact, it *is* the artefact —
and it is a condition we already compute rather than something new to measure.

So the guard now takes `endpoints_are_same_surface_minima`, passed `True` only when both endpoints
were optimised to convergence with the calculator the band used. Under that condition a submerged
HEI returns the new status **`SUBMERGED_BARRIER`** with a number; otherwise it stays
`NON_MONOTONIC_PATH` with none. A magnitude backstop still rejects gaps beyond
`BARRIER_MAX_PLAUSIBLE` regardless, since nothing chemical reaches −10 000 kcal/mol.

Nothing else weakens: the clash, plausibility-band and convergence checks are untouched, and on our
existing evidence **0 of 12 correctly-built runs would change status**. The change can only convert
refusals into numbers on runs that already pass every other check.

## 2. Which barrier retrosynthesis actually needs

**They are exactly translatable, and the separated-reactant one is both the reproducible number and
the needed one. Report that; keep the other two as diagnostics.**

$$\Delta E^\ddagger_\text{sep} = \Delta E^\ddagger_\text{complex} + E_\text{bind},
\qquad E_\text{bind} = E(\text{complex}) - \textstyle\sum E(\text{isolated fragments}) \le 0$$

One extra calculation per reaction — each fragment optimised in isolation at the same level. Cheap,
because the fragments are small.

**Why the complex-referenced barrier is not reproducible.** `build_endpoints` constructs the
pre-reaction complex by placing fragments at a target contact distance, with a seed and a retry
loop. A different orientation gives a different well depth, and therefore a different
$\Delta E^\ddagger_\text{complex}$ *for identical chemistry*. The number would depend on our own
random seed. The separated fragments have no such freedom — each is a uniquely defined optimised
minimum. This is a prediction the walkthrough can test directly by re-running S3 at several seeds
and reporting the spread of both quantities; I expect the complex barrier to move by
kcal/mol-scale and the separated barrier not to move at all.

**Why it is also the one the chemistry wants.** Transition-state theory for a bimolecular step
references the separated reactants at standard state. The encounter complex is a transient at
synthetic concentrations, not a populated intermediate, so a barrier measured from it does not
enter the rate expression. It is also what BH9 and the literature report, so it is the only one
comparable to anything outside this tree.

**And the complex-referenced barrier actively distorts ranking.** Since
$\Delta E^\ddagger_\text{complex} = \Delta E^\ddagger_\text{sep} + |E_\text{bind}|$, the penalty is
largest where the pre-complex binds most strongly — hydrogen-bonded and ionic pairs, which are
disproportionately the *facile* steps. Using it as a feasibility score would systematically
disfavour the reactions we most want the planner to find. For a ranking heuristic that is worse than
a constant offset would be.

## What neither number is

Both are **electronic energies**. Neither contains ZPE, thermal corrections, or entropy. For a
bimolecular step the association entropy costs roughly 10–15 kcal/mol of $\Delta G^\ddagger$ at
298 K and 1 M, and neither quantity carries it.

Within one class this is near-constant, so ranking survives. **Across molecularity it does not** —
and retrosynthetic routes mix unimolecular and bimolecular steps by construction. Any route-level
score that sums these barriers is comparing quantities that differ by a term it never computed. That
is a limitation of the whole oracle ladder, not of this choice between two definitions, and it is
currently unrecorded anywhere else.

## What changed in code

`classify_neb_result` gains two optional arguments and one status:

```python
classify_neb_result(image_energies, e_reactant, e_product, image_min_distances, converged,
                    endpoints_are_same_surface_minima=None,   # gate for SUBMERGED_BARRIER
                    e_separated=None)                          # reference the barrier to fragments
```

Both default to the previous behaviour, so existing callers are unaffected. Four tests added
covering the submerged case, the unverified case, the catastrophic-gap case, and the exact
translation between the two references. 15/15 pass.
