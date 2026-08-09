# First run of the established protocol — autodE + ORCA on BH9 #93

**Date:** 2026-08-09 · **Job:** `adeorca-11321451` · **Work dir:**
`/mnt/data/resynthesis/admissibility/work_autode/bh9_93_da`

Reaction: thiophene-1,1-dioxide + ethylene, Diels–Alder, 17 atoms.
BH9 reference: forward barrier **16.98**, reaction energy **−42.48** kcal/mol
(DLPNO-CCSD(T)/CBS at CAM-B3LYP-D3(BJ)/6-311++G\*\*).

## It completed

| | |
|---|---|
| wallclock | **85.5 min**, single core |
| barrier | **9.58** kcal/mol (reference 16.98 → **−7.40**) |
| reaction energy | **−48.21** kcal/mol (reference −42.48 → **−5.73**) |
| TS | found, `TS_TwHjni_ll_ad_3-8_6-7` |
| **imaginary frequencies** | **exactly one, −363.8 cm⁻¹** |
| conformers found | reactants [1, 1], products [1] |

The single imaginary mode is the thing our own pipeline never establishes. It is what makes this a
*verified saddle* rather than the highest point of a coarse band, and we got it for free by using
the published tool.

## Correction to what was reported earlier

I said autodE's ORCA defaults were "PBE0-D3BJ/def2-SVP optimisations and DLPNO-CCSD(T)/def2-TZVP
single points". **The single points are not coupled cluster.** Read from the generated inputs:

```
optimisation : ! LooseOpt PBE0 RIJCOSX D3BJ def2-SVP def2/J
frequency    : ! Freq    PBE0 RIJCOSX D3BJ def2-SVP def2/J
single point : ! SP      PBE0 RIJCOSX D3BJ def2-TZVP def2/J
```

So this is **PBE0-D3BJ/def2-TZVP // PBE0-D3BJ/def2-SVP** throughout. I asserted the CCSD(T) part
without checking it, and the whole comparison below depends on the difference.

## Is −7.40 kcal/mol acceptable?

Against BH9's own assessment of PBE0 on **type II (pericyclic)** reactions — barrier-height
MAE **3.34**, ME −0.05 kcal/mol — our error is roughly **2.2× the class mean**, and one-sided.
The reaction-energy error, −5.73 against a PBE0 type-II RE MAE of **5.52**, sits right at the mean.

That is not alarming for a single reaction (an MAE is a mean; individual errors run to 2–3×), and
the basis is def2-TZVP rather than the def2-QZVPP those MAEs were measured at. But it is a real gap
and it has an obvious next step: ORCA gives us **DLPNO-CCSD(T)**, the exact method BH9's references
are built on, so the same TS can be re-scored at the reference level. If the error collapses, it was
the functional; if it persists, the TS or the geometry differs from BH9's.

## What this run cannot show

**Conformer sampling found nothing to sample** — one conformer per species. Ethylene and
thiophene-1,1-dioxide are rigid, so gap B2 is untested here. Reaction #93 was chosen as the
*cheapest* case and that is exactly why it cannot demonstrate the sampling question. The flexible
member of set A is **#436** (CO₂ + thiazolium enol, 27 atoms) — the only one with real
conformational freedom, and the one whose BH9 reference geometry needed a full conformer search.
That is where B2 has to be exercised.

## NWChem

The parallel NWChem run (`11321437`) **timed out at 6 h** on the same reaction, single core, without
finishing — against ORCA's 85 min. Not a like-for-like benchmark, since neither had real parallelism,
but enough to say ORCA is the practical default and NWChem is the cross-check, not the workhorse.
