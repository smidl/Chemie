# Walkthrough results — set A, PBE0-D3BJ/def2-TZVP via autodE + ORCA

**Date:** 2026-08-13 · Jobs `11323319`, `11345121`, `11345122`, rescore `11344983` ·
Work dirs under `/mnt/data/resynthesis/admissibility/work_autode/`

## Where the four mapped reactions stand

| # | reaction | atoms | barrier | BH9 ref | error | TS imag. freq | cost |
|---|---|---|---|---|---|---|---|
| 93 | thiophene-1,1-dioxide + ethylene | 17 | 11.03 | 16.98 | **−5.95** | −363.9 | 88 min, 1 core |
| 92 | thiophene S-oxide + 2,3-dihydrofuran | 21 | 13.66 | 16.64 | **−2.98** | −398.7 | 53 min, 8 cores |
| 107 | 1-methylcyclopropene + methyl azide | 17 | 12.83 | 15.30 | **−2.47** | −425.9 | 45 min, 8 cores |
| 436 | CO₂ + thiazolium enol | 27 | **refused** | 7.18 | — | — | 36 min, 8 cores |

Every completed run located a transition state and verified it with **exactly one imaginary mode**.
Reaction 436 did not complete, for a reason worth its own section below.

**These errors are normal.** BH9's own assessment of PBE0 on pericyclic reactions gives a
barrier-height MAE of **3.34 kcal/mol**. Reactions 92 and 107 sit at −2.98 and −2.47, i.e. right at
that mean; 93 at −5.95 is the outlier at about 1.8×. So the pipeline is reproducing published
reference barriers to within the expected error of the functional it is using.

## The geometry is right — the error is the functional

The obvious worry about −5.95 was that autodE had found a *different saddle* from the one BH9
characterised. That is now excluded. Single points at BH9's own method — DLPNO-CCSD(T)/def2-TZVP —
were run on the geometries autodE optimised and frequency-verified, with no re-optimisation:

| reaction | PBE0/def2-TZVP | error | **DLPNO-CCSD(T)/def2-TZVP** | **error** |
|---|---|---|---|---|
| 93 | 11.03 | −5.95 | 16.25 | **−0.73** |
| 92 | 13.66 | −2.98 | 17.56 | **+0.92** |
| 107 | 12.83 | −2.47 | 14.42 | **−0.88** |
| **mean \|error\|** | | **3.80** | | **0.84** |

All three land within **±1 kcal/mol** of the BH9 reference at coupled cluster, and the signs differ
(−, +, −), so this is scatter at roughly the level of basis-set incompleteness — def2-TZVP against
BH9's CBS extrapolation — not a systematic offset. Rescoring costs about 11 min per reaction on
8 cores and cuts the mean absolute error **4.5×**.

Changing only the level of theory removes essentially the whole error, on every reaction tested.

**This is the single most important result so far, and it now rests on three reactions rather than
one.** The fragment-embedding, placement, TS-search and verification chain produces essentially the
correct transition state; the visible PBE0 error is a level-of-theory choice we control, not a defect
in the procedure. Cheap enough to run for every reaction.

## How the reaction is written down matters more than which functional is used

Reaction 92 was first run with the stereochemistry stripped from the product SMILES, because that is
what bond perception emitted. Rerunning with BH9's stereochemistry restored:

| input product SMILES | barrier | error | product conformers |
|---|---|---|---|
| `[O-][S+]1C2C=CC1C1OCCC12` (no stereo) | 5.09 | −11.55 | 5 |
| `[O-][S@+]1[C@@H]2C=C[C@H]1[C@H]1OCC[C@H]12` | **13.66** | **−2.98** | 2 |

**Dropping stereochemistry cost 8.57 kcal/mol** — larger than the entire functional error, and larger
than the difference between PBE0 and coupled cluster on reaction 93.

The mechanism is not subtle once seen. For a Diels–Alder, the product stereochemistry *is* the
endo/exo distinction. With it removed, the search is free to converge on whichever diastereomeric
transition state is lowest, which need not be the one the reference characterises. The conformer
count corroborates it: 5 product conformers without stereochemistry, 2 with, because the constraint
removes the alternatives.

This matters well beyond our pipeline. A retrosynthesis planner emits unmapped, frequently
stereochemistry-free SMILES. Feeding that to any barrier oracle invites an 8.5 kcal/mol error that no
choice of functional, basis set or convergence threshold will recover — and nothing in the output
announces it. The barrier looks fine; it is simply a barrier for a different reaction.

## Reaction 436 refuses to run, and it is right to

The only type-IX case in set A, and the only one with real conformational freedom, stops with
`NoConformers` after 36 minutes. The cause is not conformer *generation* — 8, 8 and 27 candidate
structures were produced — but autodE's `prune_diff_graph`, which discards any conformer whose
connectivity changes during optimisation. Every one changed.

Measuring the optimised product geometries directly:

| conformer | CO₂-unit C–O | nearest C–C | verdict |
|---|---|---|---|
| conf0 | 1.158 / 1.162 Å | 3.024 Å | dissociated |
| conf1 | 1.160 / 1.161 Å | 3.070 Å | dissociated |
| conf3 | 1.159 / 1.161 Å | 3.400 Å | dissociated |

A C–O bond of 1.16 Å is **free CO₂**; a bound carboxylate would be near 1.25 Å. A C–C bond is 1.54 Å,
and these are 3.0–3.4 Å apart. **The product expels CO₂ during optimisation in all three cases.**

That is correct chemistry, not a defect. The product is a thiazolium-carboxylate **zwitterion**, and a
zwitterion is generally not a minimum in the gas phase — BH9's reverse barrier of 9.50 kcal/mol says
the adduct sits in a shallow well, and without solvent it slides out of it. BH9 flags this directly:
its charged types are strongly solvent-stabilised and it "experienced difficulties finding some of
these TSs".

**Two things follow, and they point in opposite directions.**

The good one: autodE **refused to produce a number** rather than reporting a barrier for a product
that does not exist at this level of theory. That is the behaviour our own pipeline failed to show in
July, when a corrupt endpoint yielded a confident 434 kcal/mol. A tool that stops is worth more than
one that answers.

The bad one: **no case in set A now exercises conformational sampling.** Reactions 93, 92 and 107
found 1, 2 and 1 conformers respectively — they are rigid. 436 was the only flexible member and it
cannot be run gas-phase. So the sampling question raised as gap B2 remains untested, and testing it
requires either implicit solvation or a different reaction. This is not a gap in the plan; it is the
plan meeting the boundary that BH9 itself identified — the reaction classes closest to our specialty
chemistry are exactly the ones a gas-phase pipeline cannot attempt.

## Cost, now that parallelism is fixed

`ade.Config.n_cores` defaults from `SLURM_CPUS_PER_TASK`, which the MPI-compatible allocation shape
(`--ntasks=N --cpus-per-task=1`) sets to **1**. Every run before this point was therefore silently
single-core. Set explicitly to 8:

- 17 atoms: 88 min on 1 core → 45 min on 8 (reaction 107)
- 21 atoms: 53 min on 8 cores — *faster than the smaller reaction had been serially*

## Environment traps, for the reviewer

Five, none of them chemistry, all of which cost a job or a wrong number:

1. **Shared working directory.** Two autodE runs in one directory traded xtb artifacts, which are not
   method-tagged. Moved a barrier by **1.45 kcal/mol**.
2. **TS template cache inside `site-packages`.** Persists across working directories; affected timing
   only, but invalidated a cost measurement.
3. **`n_cores` silently 1.** No warning; a run simply takes five times longer.
4. **ORCA refuses parallel runs invoked via `PATH`** — it must be called by full pathname.
5. **`module` undefined in some batch shells**, so `mpirun` never appears and ORCA aborts at startup.
   Fixed by sourcing `/etc/profile.d/lmod.sh` explicitly.
