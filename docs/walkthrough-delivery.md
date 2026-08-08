# Delivery: three pairs, one at a time

**Date:** 2026-08-08 · **Set A only** (illustration; set B stays sealed per `walkthrough-protocol.md`)

One reaction per page, served in pairs so each failure sits next to a success that differs in as
little as possible. Where the pair is genuinely matched, the contrast identifies the cause; where it
is not, that is stated rather than dressed up.

## Pair 1 — cycloaddition with a strained partner · **matched**

| | reaction | atoms | ref | outcome |
|---|---|---|---|---|
| ✓ | **#107** 1-methylcyclopropene + methyl azide, [3+2] | 17 | 15.30 | runs to a barrier |
| ✗ | **#95** 3,6-dimethyltetrazine + benzyne, IEDDA | 24 | −1.34 | **stops at S1** |

The control this pair provides: *both* partners are strained — a cyclopropene double bond and a
benzyne triple bond — and both reactions are concerted cycloadditions forming two σ bonds. One maps
at confidence 0.839, the other at 0.330 with the ring-fusion carbons on the wrong atoms. **So strain
is not what breaks the mapper; the unusual valence state is.** That is a sharper statement than
either reaction gives alone, and it is the pair we would most like a second opinion on.

Bonus: #95's reference barrier is **−1.34 kcal/mol**, so had it mapped it would also have been the
submerged-barrier case. The page can say what the guard would have done without pretending we got
there.

## Pair 2 — Diels–Alder on a thiophene-oxide diene · **matched, both succeed**

| | reaction | atoms | ref | outcome |
|---|---|---|---|---|
| ✓ | **#93** thiophene-1,1-dioxide + ethylene | 17 | 16.98 | runs |
| ✓ | **#92** thiophene S-oxide + 2,3-dihydrofuran | 21 | 16.64 | runs |

Nearly the same reaction twice — same diene family, references within 0.34 kcal/mol of each other —
but 17 vs 21 atoms, and #92 produces four stereocentres where #93 produces two. This is the page
where cost scaling, conformer choice and endo/exo are visible **without** a failure to distract from
them. If our single-orientation placement is going to be criticised, it should be criticised here.

## Pair 3 — where the reaction lives · **not matched, and it cannot be**

| | reaction | atoms | ref | outcome |
|---|---|---|---|---|
| ✓ | **#436** CO₂ + thiazolium enol, nucleophilic addition | 27 | 7.18 | runs |
| ✗ | **#407** 2-pyridone + H₂O, water-assisted tautomerisation | 15 | 4.73 | **stops at S1** |

Different classes, so the contrast is weaker: #436 forms one heavy-atom bond and maps cleanly, while
#407's entire reaction is a proton relay that leaves the heavy skeleton untouched, so both the
mapper and our check see nothing.

**The matched control does not exist.** The whole neutral, multi-fragment, ≤ 30-atom BH9 pool
contains exactly **two** proton-transfer reactions — #407 and #408 — and #408 is in the sealed set B.
Even spending B would only give a second case of the same failure, not a success to contrast with.
Controlling this failure mode needs charged species, which our gas-phase pipeline excludes anyway.
That constraint is worth putting to the reviewer directly: *if we cannot construct a control for
hydrogen-mobile reactions from a coupled-cluster benchmark set, what would you use?*

## Order of service

Pair 2 first, then Pair 1, then Pair 3 — successes before failures, and the matched pair before the
unmatched one. Pair 2 is also the cheapest, so it is the page that gets full three-rung treatment
first.

Each page carries: the reaction drawn, the atom map drawn on the structures, per-fragment embedding
with the min interatomic distance from **both** RDKit and Open Babel, the placed complex with its
contact distances, endpoint energies and convergence, the separated-fragment reference, the NEB
band as an energy profile, the guard's verdict, and the barrier against BH9 — with wallclock at
every step and the level of theory named on every number.
