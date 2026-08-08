# Which level of theory — the published answer, and what it says about our choices

**Date:** 2026-08-08 · **Source:** Prasad, Pei, Edelmann, Otero-de-la-Roza & DiLabio, *BH9, a New
Comprehensive Benchmark Data Set for Barrier Heights and Reaction Energies*, **J. Chem. Theory
Comput. 18(1), 151–166 (2022)**, DOI `10.1021/acs.jctc.1c00694` — metadata verified against
Crossref. **A correction exists** and revises reference values: DOI `10.1021/acs.jctc.2c00362`,
JCTC 18(6), 4041–4044 (2022). Postprint archived at `~/agents/library/prasad2022_bh9.pdf`.

Part of the "best computational route" question does not need us to run anything. BH9 is 449
organic reactions with **DLPNO-CCSD(T)/CBS** references across nine reaction types, reactant and TS
sizes **11–71 atoms** — closer to our specialty scale than Transition1x's 4–23 — and it includes the
two classes our specialty set is made of: **VIII nucleophilic substitution** and **IX nucleophilic
addition**. `spec01_cyanohydrin` is a type IX reaction.

## Barrier-height MAE, def2-QZVPP, kcal/mol (their Table V)

| functional | total | VIII (SN) | IX (addition) |
|---|---|---|---|
| ωB97M-V | **2.08** | 2.20 | 0.99 |
| ωB97XD | **2.10** | 2.99 | 1.21 |
| MN15 | 2.18 | 2.75 | 1.07 |
| M05-2X | 2.21 | 2.97 | 1.06 |
| M06-2X | 2.27 | 3.14 | 1.13 |
| CAM-B3LYP-XDM | 2.37 | 2.13 | 1.19 |
| PBE0-XDM | 2.85 | 1.52 | 2.13 |
| PBE0 | 3.00 | 3.85 | 1.62 |
| B3LYP | 5.37 | 3.58 | 4.10 |
| TPSS | 6.19 | 4.04 | 4.44 |
| **PBE** | **6.68** | 4.04 | 4.77 |
| BLYP | 7.62 | 4.00 | 5.73 |
| PBE-XDM | 8.12 | 6.32 | 5.57 |

## Three things this says about us

**1. Our production functional is a good choice; our *validated contract* is not.** Production is
wB97X/6-31G(d) — the ωB97X family sits at the top of the table (2.08–2.10). But the two numbers we
treat as the reproduction contract, 27.57 and 111.03 kcal/mol, are **PBE/3-21g**, and PBE is third
from the bottom at **6.68 kcal/mol MAE with ME −5.78** — a large and *systematic* underestimate of
barriers, before accounting for 3-21g being far below the def2-QZVPP these numbers were measured at.
The contract is still valid as a *reproduction* check (does the integration return the same number),
but it must never be read as chemistry, and the July README's "indicative" is too generous.

**2. Dispersion correction is not free — it inverts by functional class.** XDM *improves* every
hybrid (PBE0 3.00 → 2.85; CAM-B3LYP 4.43 → 2.37) and *degrades* every GGA (PBE 6.68 → **8.12**;
BLYP 7.62 → 8.66). The mechanism is in the paper: GGAs already underestimate barriers through
delocalization error, and dispersion lowers them further. Anyone adding a `-D3`/`-XDM` flag to a PBE
rung expecting an improvement will make it worse. Our cost ladder mixes functional classes by
construction, so this is a live trap.

**3. It gives the cheap rung a target.** For our two reaction classes, the best hybrids reach
**1–3 kcal/mol** against coupled-cluster. Any lower rung we propose — GFN2-xTB, an MLIP, a learned
gate — has to be argued against that, not against PBE/3-21g.

## What this does *not* settle

BH9 measures **energy at a given geometry**. Every number above presumes a correct transition state
was already located. Our failure was upstream of that — building a physically valid endpoint at all —
and no functional choice repairs a reactant geometry with two carbons 0.142 Å apart. The two
questions are independent, and only the second is ours.

BH9 also notes that its charged types (VII, VIII, IX) are strongly solvent-stabilised, and that some
barriers are even negative in the gas phase because solvent stabilises reactants more than the TS.
Several `specialty_11` steps carry `solvation_required: true` against a gas-phase pipeline. That is
a modelling gap of the same size as the functional choice, and it is not currently on anyone's list.

## Outstanding

The per-reaction data — the 449 reactions with individual reference barriers — is in the ACS
Supporting Information, which is free but Cloudflare-blocks automated download. Queued in
`~/agents/library/paywalled.md` for manual retrieval. **Use the corrected values**
(`10.1021/acs.jctc.2c00362`), not the original SI, if both are present.
