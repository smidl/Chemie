# ωB97M-V rescore of the three validated geometries — and the prediction it breaks

**Date:** 2026-08-26 · **Job:** `11381115` (`wb97mv`), COMPLETED 2026-08-21T00:41:36, 12:49 elapsed
**Log:** `/mnt/data/resynthesis/admissibility/logs/wb97mv-11381115.log`
**Outputs:** `/mnt/data/resynthesis/admissibility/wb97mv/` (9 single points: r93, r92, r107 × {TS, r0, r1})

```
! SP wB97M-V def2-TZVP def2/J RIJCOSX TightSCF DefGrid3
```
Single points on the **same** autodE/ORCA PBE0/def2-SVP geometries used for the PBE0 and
DLPNO numbers, so the three rungs are directly comparable and geometry is held fixed.

> **Recording note.** The job finished four minutes after the 2026-08-21 deep status was
> committed (00:41:36 vs 00:37:42), so that status records it as "pending confirmation".
> It was not pending; it was unread for five days.

## The numbers

| reaction | ωB97M-V | BH9 ref | error |
|---|---|---|---|
| r93 (thiophene-1,1-dioxide + ethylene) | 15.42 | 16.98 | **−1.56** |
| r92 (thiophene S-oxide + 2,3-dihydrofuran) | 17.96 | 16.64 | **+1.32** |
| r107 (1-methylcyclopropene + methyl azide) | 14.76 | 15.30 | **−0.54** |

Three rungs on identical geometries, n=3:

| rung | errors | MAE | ME | \|ME\|/MAE |
|---|---|---|---|---|
| PBE0/def2-TZVP (autodE default) | −5.95, −2.98, −2.47 | 3.80 | −3.80 | **1.00** |
| ωB97M-V/def2-TZVP | −1.56, +1.32, −0.54 | **1.14** | −0.26 | **0.23** |
| DLPNO-CCSD(T)/def2-TZVP | −0.73, +0.92, −0.88 | 0.84 | −0.23 | 0.27 |

## What it confirms

**A cheap near-DLPNO rung exists.** ωB97M-V reaches MAE 1.14 in ~4.3 min per reaction
(9 single points in 12:49) against DLPNO's recorded 17 min for three single points, i.e.
**~4× cheaper at 1.4× the error**. That is a real addition to the cost ladder independent of
everything below.

**The geometry is right, and this is the second independent confirmation.** ωB97M-V and DLPNO
are single points on PBE0/def2-SVP geometries and both give small, sign-varying errors. A
systematically bad saddle would depress *every* method evaluated on it. It does not. So PBE0's
one-signed −3.80 is the functional's own error on this family, not a pipeline artifact.

## What it breaks

`docs/barrier-accuracy-requirement.md` §"Which functionals have systematic error" and
`docs/sota/oracle-error-structure-vs-magnitude.md` both take BH9 Table V's pericyclic row as the
actionable criterion, predicting ωB97M-V would be **both more accurate and far more systematic**
(|ME|/MAE 0.96) while PBE0 would be "essentially random" (0.015). This run was the stated test of
that prediction.

**Half held; half inverted.**

| | BH9 Table V (pericyclic) predicts | we measure (n=3) |
|---|---|---|
| ωB97M-V accuracy | better than PBE0 | ✔ 1.14 vs 3.80 |
| ωB97M-V \|ME\|/MAE | 0.96 — highly systematic | ✘ **0.23 — signs vary** |
| PBE0 \|ME\|/MAE | 0.015 — essentially random | ✘ **1.00 — perfectly one-signed** |

On the criterion those documents propose, PBE0 is the **best** of the three and ωB97M-V is the
scatter case. The recommendation "switch autodE's high-level method from PBE0 to ωB97M-V" is
therefore **not supported by its own test** — on accuracy yes, on error structure the opposite.

## The likely mechanism, and why it matters more than the n=3

Accuracy and systematicity may not be independent axes. Removing systematic error is largely
*what makes* a method accurate, so a high |ME|/MAE is the signature of a **large uncorrected
bias**. PBE0 underestimates pericyclic barriers, consistently, and that is exactly why it is both
inaccurate and one-signed. ωB97M-V and DLPNO have removed most of that bias, and what remains is
small residual scatter around zero.

If that holds generally, the two axes trade off and cannot be jointly optimised — which is what
`barrier-accuracy-requirement.md` item 2 assumed they could be. Item 1 ("do not build active
learning to reduce barrier error yet") rests on the same framing and should be re-derived rather
than inherited.

## Honest limits — this does not settle it either

- **n=3.** |ME|/MAE = 1.00 at n=3 means only "all three the same sign", roughly a 1-in-4
  coincidence under symmetric independent errors. Suggestive, not established.
- **One reaction family.** All three are pericyclic. The quantity that matters for route ranking
  is error correlation across *the steps of one route*, which mixes families. Unmeasured.
- **A real tension with BH9 remains.** Our PBE0 MAE (3.80) matches BH9's pericyclic 3.34 fine, but
  our ME (−3.80) is nowhere near BH9's −0.05. Either these three are unlucky, or BH9's pericyclic
  class is heterogeneous enough that ME cancels *across* sub-types while staying one-signed
  *within* them. The second reading would strengthen the underlying correlation argument while
  killing the practice of reading |ME|/MAE off Table V — which is the part the criterion depends on.

## Consequence

The perturbation result underneath (8.3 % vs 14.4 % top-1 flip) is arithmetic on real route sets
and **survives** — error structure does dominate error magnitude. What does not survive is the
cheap, actionable route from that insight to a functional choice via a published table.

Measuring our own error correlation properly needs barriers across several families on shared
geometries at n ≫ 3 — a campaign at 45–90 min per reaction, which is the argument for adopting
**RGD1** (ships TSs, barriers, endpoint geometries and atom mappings for 176 992 reactions) rather
than generating it ourselves. See `strategy-after-dft.md` §Recommendation 2.

**Withheld from `briefing` until n improves.** Per ADR 0004 the correlation claim was already being
held back pending this confirmation; it did not arrive.
