# The walkthrough set — six reactions, and two problems found while choosing them

**Date:** 2026-08-08 · **Source:** BH9 Supporting Information, `ct1c00694_si_001.zip`, archived at
`~/agents/library/paywall/` and staged on RCI at
`/mnt/data/resynthesis/admissibility/data/BH9_SI/` · **Scripts:** `E0_pick.py`, `E1_detail.py` ·
**Index:** `out/bh9_index.json`

## Why BH9 and not Transition1x

| | Transition1x | BH9 |
|---|---|---|
| multi-fragment reactant side | **0.1 %** | **57.5 %** (258/449) |
| reference | wB97X/6-31G(d) path | **DLPNO-CCSD(T)/CBS** |
| size | 4–23 atoms | 11–71 atoms |

BH9 exercises the failure mode; Transition1x cannot. That alone settles the choice.

## The six

Selected from the neutral, closed-shell, multi-fragment pool (18 reactions at ≤ 30 atoms). SMILES
derived from BH9's own geometries by bond perception, so they can be checked against the structures.
Reference is the **forward** barrier in kcal/mol.

| # | BH9 id | class | reaction | atoms | ref |
|---|---|---|---|---|---|
| 1 | 407 | proton transfer (VII) | 2-pyridone + H₂O — water-assisted tautomerisation | 15 | **4.73** |
| 2 | 107 | [3+2] cycloaddition (II) | 1-methylcyclopropene + methyl azide | 17 | **15.30** |
| 3 | 93 | Diels–Alder (II) | thiophene-1,1-dioxide + ethylene | 17 | **16.98** |
| 4 | 92 | Diels–Alder (II) | thiophene S-oxide + 2,3-dihydrofuran | 21 | **16.64** |
| 5 | 95 | inverse-electron-demand DA (II) | 3,6-dimethyl-1,2,4,5-tetrazine + benzyne | 24 | **−1.34** |
| 6 | 436 | nucleophilic addition (IX) | CO₂ + a thiazolium enol | 27 | **7.18** |

Rationale, since the choice is a judgement a reviewer may want to overturn:

- **None is the first example in any textbook.** No butadiene + ethylene, no CH₃Cl + Cl⁻. Substituted
  and heteroatom-bearing variants of well-taught classes, which is what was asked for.
- **Spans 15 → 27 atoms**, so cost scaling is visible rather than asserted.
- **Spans −1.34 → 16.98 kcal/mol**, including a submerged barrier (see below).
- **Pericyclic is the hardest class for DFT** — BH9's own Table V gives PBE a 7.98 kcal/mol MAE on
  type II against 6.68 overall, because delocalization error overstabilises the TS. Four of the six
  are the stress case on purpose.
- **#436 is type IX**, the class `spec01_cyanohydrin` belongs to, so one case connects to the
  specialty set.

**What we could not get.** Zero neutral small reactions exist in types VIII/IX: of BH9's 41
reactions in our two specialty classes, **36 are charged** and the median is 27 atoms. BH9 says why —
those species are strongly solvent-stabilised, and it had difficulty locating their TSs. So the
classes closest to our actual chemistry are precisely the ones a gas-phase pipeline cannot honestly
attempt. That is a finding, not a gap in the selection.

## Two problems found while selecting

### 1. Our guard would reject a real reaction

`classify_neb_result` refuses to return a number when `hei < endpoint_max`, calling it
`NON_MONOTONIC_PATH` and telling the caller to suspect the endpoints. But **19 of BH9's 449 forward
barriers (4.2 %) are negative** — down to −67.71 kcal/mol — and the paper is explicit that these are
real, not artefacts. Submerged barriers happen when a pre-reaction complex is more stable than the
TS relative to separated reactants.

The guard was calibrated on a corrupt-endpoint failure and generalised into a claim about the
chemistry it was told not to make. At a 4.2 % base rate it is a small effect, but it is a **false
negative by construction**, and it is the same error class as everything else found this fortnight:
a check that is correct about its own criterion and wrong about what it is credited with detecting.

### 2. Our barrier and BH9's barrier are not the same quantity

BH9 defines the barrier as **E(TS) − E(separated reactants)**. Our NEB defines it as
**E(highest image) − E(reactant endpoint)**, and `build_endpoints` deliberately constructs that
endpoint as a **pre-reaction complex with fragments at ~2.5 Å contact**. Those differ by the
complexation energy — for a hydrogen-bonded or dispersion-bound pair, several kcal/mol, and largest
for exactly the cases where the reference is smallest.

So the comparison needs one extra calculation per reaction: the separated-fragment energy at the
same level, which is cheap. Without it every number would carry an unquantified offset in a
consistent direction, and the walkthrough would look like a systematic accuracy problem when it is a
definitional one. This is the kind of thing the reviewing chemist should not have to find.

## Stages to be recorded, per reaction, per rung

S0 reaction and depiction · S1 atom map · S2 per-fragment embed (RDKit **and** Open Babel — they
differ 2.6× in clash rate) · S3 complex placement with contact distances · S4 endpoint optimisation
· **S4b separated-fragment reference energy** (added per problem 2) · S5 IDPP interpolation ·
S6 NEB · S7 guard status · S8 barrier vs BH9 reference, with wallclock at every stage.

Rungs: GFN2-xTB → PBE/3-21g → wB97X/6-31G(d), each re-optimising its own endpoints, since mixing
surfaces produced 12.5 % spurious rejections in July.
