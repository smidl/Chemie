# First run of the established protocol — autodE + ORCA on BH9 #93

> ## ⚠ THE NUMBERS BELOW ARE WITHDRAWN (2026-08-09)
>
> The ORCA job was launched into a working directory that the NWChem job was **still writing to**,
> under the same reaction name. Checked afterwards: **15 NWChem files were written after the ORCA
> job started**, and both runs used xtb as the low-level method — whose artifacts autodE does *not*
> method-tag, so the two jobs shared the conformer and low-level optimisation files.
>
> autodE tags high-level files by code (`_orca`, `_nwchem`), so direct reuse of a DFT energy is
> unlikely; but "unlikely" is not a measurement, and a shared low-level cache is enough to make the
> result unattributable to either code. **Nothing below may be quoted.** Rerunning in an isolated
> directory (`work_autode/orca_clean_93`, job `11322670`), with the script now refusing to start in
> a non-empty workdir.
>
> The qualitative outcomes survive independently of the numbers: the protocol *completes*, it
> *locates and frequency-verifies a saddle*, and it found *no conformers to sample* on two rigid
> reactants. Those do not depend on which code produced a given energy.
>
> Cause: I launched the second job while the first was still running, without checking. Same class
> of error as everything else catalogued this fortnight — a procedure that looked fine because
> nothing announced the collision.
>
> **Rerun in an isolated directory (job `11322670`) — the withdrawal was justified.**
>
> | | contaminated | isolated | BH9 ref |
> |---|---|---|---|
> | barrier | 9.58 | **11.03** | 16.98 |
> | reaction energy | −48.21 | **−49.01** | −42.48 |
> | TS imaginary freq | −363.80 | −363.94 | — |
> | wallclock | 85.5 min | 71.1 min | — |
>
> The barrier moved **1.45 kcal/mol**, so the shared low-level cache did real damage. The imaginary
> frequency is unchanged to 0.14 cm⁻¹ — same saddle, corrupted energies.
>
> Errors against BH9 at PBE0-D3BJ/def2-TZVP: barrier **−5.95**, reaction energy **−6.53**. BH9's own
> PBE0 figures for pericyclic reactions are barrier MAE 3.34 and RE MAE 5.52, so this is ~1.8× and
> ~1.2× the class mean — an ordinary functional error on one reaction, not a broken pipeline.

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

## A second, less obvious cache — directory isolation is not enough

autodE writes TS templates **into the installed package**, at
`autode/transition_states/lib/`, outside any working directory. Timestamps are unambiguous:

| file | written | by |
|---|---|---|
| `template0.txt` | 2026-08-08 18:37 | shipped with the install |
| `template1.txt` | 2026-08-08 20:05 | the **contaminated** run |
| `template2.txt` | 2026-08-09 10:26 | the **"clean"** rerun |

So the isolated rerun consumed a template the contaminated run had written — its TS is named
`..._template_...` rather than the adaptive-search name. The **energy remains attributable**: a
template supplies only a *guess* geometry, which was then constrained-optimised, TS-optimised and
frequency-verified at ORCA level. But **71.1 min is not a from-scratch cost** — that run had a head
start — and the earlier claim that isolating the directory had fixed the problem was incomplete.

Templates 1 and 2 were quarantined to `admissibility/ts_templates_quarantine/` and job `11323319`
ran from a genuinely empty state.

**Resolved — the barrier is reproducible, and the template affected only cost.**

| run | barrier | wallclock | TS imaginary freq | TS route |
|---|---|---|---|---|
| contaminated (shared workdir) | 9.58 | 85.5 min | −363.80 | adaptive |
| isolated workdir, template present | **11.03** | 71.1 min | −363.94 | template |
| from scratch, templates quarantined | **11.03** | **88.0 min** | −363.92 | adaptive |

The barrier reproduces **exactly** across the two clean runs, so 11.03 kcal/mol is attributable. The
imaginary frequency agrees to 0.02 cm⁻¹, and the TS name reverts to the adaptive-search form once no
template is available — confirming the middle run really was consuming one. The template bought
**17 minutes, about 19 %**, and changed nothing else, so the honest from-scratch cost of one 17-atom
reaction at this level is **88 minutes on a single core**.

Net: the withdrawal was justified — the shared working directory moved the barrier by 1.45 kcal/mol —
while the template leak cost only timing.

**This is itself a walkthrough finding.** Reproducing one number from an established tool took three
attempts, and two of the three traps were *invisible caches* — a shared working directory whose
low-level artifacts are not method-tagged, and a template library inside site-packages. Anyone
adopting autodE will hit both, and neither is mentioned in its paper.

## NWChem

The parallel NWChem run (`11321437`) **timed out at 6 h** on the same reaction, single core, without
finishing — against ORCA's 85 min. Not a like-for-like benchmark, since neither had real parallelism,
but enough to say ORCA is the practical default and NWChem is the cross-check, not the workhorse.
