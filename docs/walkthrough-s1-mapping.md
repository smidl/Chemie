# Walkthrough S0–S1: structures and atom maps

**Date:** 2026-08-08 · **Scripts:** `G0_assemble.py` … `G4_hmap.py` ·
**Output:** `out/walkthrough_s1b.json` · **Logs:** `logs/asm-*`, `logs/map3-*`, `logs/hmap-*`

## Status

| # | reaction | atoms | ref (kcal/mol) | RXNMapper conf. | bonds formed/broken | H map |
|---|---|---|---|---|---|---|
| 107 | 1-methylcyclopropene + methyl azide, [3+2] | 17 | 15.30 | 0.839 | 2 / 0 ✓ | **complete** |
| 93 | thiophene-1,1-dioxide + ethylene, DA | 17 | 16.98 | 0.496 | 2 / 0 ✓ | **complete** |
| 92 | thiophene S-oxide + 2,3-dihydrofuran, DA | 21 | 16.64 | 0.913 | 2 / 0 ✓ | **complete** |
| 436 | CO₂ + thiazolium enol, nucleophilic addition | 27 | 7.18 | 0.773 | 1 / 0 ✓ | **complete** |
| 95 | dimethyltetrazine + benzyne, IEDDA | 24 | −1.34 | **0.330** | 2 / 0 ✓ | **WRONG — caught** |
| 407 | 2-pyridone + H₂O, tautomerisation | 15 | 4.73 | 0.968 | **0 / 0** ✗ | **needs hand map** |

## How the map was made, and how it is checked

BH9 does not supply the map: reactant and TS atom orderings differ in all six (same multiset,
different order — verified). Two attempts failed before the third worked, and both failures are
worth recording because they are the obvious things to try.

**MCS does not work.** `rdFMCS.FindMCS` returns a *connected* common substructure, which cannot
express two molecules fusing into one ring system. It covered 50–88 % of the heavy skeleton and
reported **0 bond changes** — the tell, since a reaction with no bond changes is not a reaction.
Run over explicit-hydrogen graphs it was worse still: up to 1.7 M degenerate embeddings.

**What works:** RXNMapper produces the heavy-atom map, and it is then checked against a quantity it
did not optimise — the number of heavy-atom bond changes the map implies, which is known a priori
per class (concerted cycloaddition: 2 formed, 0 broken; nucleophilic addition: 1 formed). Hydrogens
are then propagated to their parent heavy atom, which is determined when nothing is broken.

## Two failures the checks caught

**#95 — the mapper is chemically wrong, and H-propagation catches it.** Its map puts the *aromatic
CH* carbons at the ring-fusion positions and leaves hydrogens on C12/C13, the strained alkyne
carbons that actually form the new bonds. The heavy-atom bond-change check passes it (2 formed, 0
broken — right count, wrong atoms), so that check alone is not sufficient. The hydrogen map sets
then come out **different on the two sides**, which is impossible for a correct map, and that is
what flags it. RXNMapper's own confidence on this reaction was **0.330, the lowest of the six** —
so the two independent signals agree.

**#407 — both checks are blind.** A water-assisted tautomerisation moves only protons: no
heavy-atom bond changes at all, so the criterion reports 0 / 0 and cannot distinguish a correct map
from a null one. RXNMapper returned water as an unchanged spectator with confidence 0.968 — high,
and useless here, because the entire reaction lives in the hydrogens it does not map. This is the
unowned mapping gap in its smallest possible form: **15 atoms, and neither the mapper nor our
verification can see the reaction.**

Both need a hand map before S2. That is two of six, on reactions chosen for being ordinary.

## Incidental: the `removeHs` trap, again

The first H-propagation run reported all five COMPLETE with "atoms 8, 9, 11, 14". Those are heavy
atom counts — mapped explicit hydrogens survive `MolToSmiles` but are stripped on re-parse unless
`SmilesParserParams.removeHs = False`. The same trap turned a 13-atom system into 6 in July and
handed PySCF a 39-electron radical. The corrected run reports 17, 17, 21, 24, 27, matching BH9.

**Any verification of an atom map must re-parse with `removeHs = False`,** or it silently checks
only the heavy atoms and passes maps whose hydrogens are wrong — which is precisely how #95 would
have got through.
