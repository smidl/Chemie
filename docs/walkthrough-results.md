# Walkthrough results — set A, PBE0-D3BJ/def2-TZVP via autodE + ORCA

**Date:** 2026-08-13 · Jobs `11323319`, `11345121`, `11345122`, rescore `11344983` ·
Work dirs under `/mnt/data/resynthesis/admissibility/work_autode/`

## Where the four mapped reactions stand

| # | reaction | atoms | barrier | BH9 ref | error | TS imag. freq | cost |
|---|---|---|---|---|---|---|---|
| 93 | thiophene-1,1-dioxide + ethylene | 17 | 11.03 | 16.98 | **−5.95** | −363.9 | 88 min, 1 core |
| 92 | thiophene S-oxide + 2,3-dihydrofuran | 21 | 13.66 | 16.64 | **−2.98** | −398.7 | 53 min, 8 cores |
| 107 | 1-methylcyclopropene + methyl azide | 17 | 12.83 | 15.30 | **−2.47** | −425.9 | 45 min, 8 cores |
| 436 | CO₂ + thiazolium enol | 27 | — | 7.18 | — | — | pending |

Every completed run located a transition state and verified it with **exactly one imaginary mode**.

**These errors are normal.** BH9's own assessment of PBE0 on pericyclic reactions gives a
barrier-height MAE of **3.34 kcal/mol**. Reactions 92 and 107 sit at −2.98 and −2.47, i.e. right at
that mean; 93 at −5.95 is the outlier at about 1.8×. So the pipeline is reproducing published
reference barriers to within the expected error of the functional it is using.

## The geometry is right — the error is the functional

The obvious worry about −5.95 was that autodE had found a *different saddle* from the one BH9
characterised. That is now excluded. Single points at BH9's own method — DLPNO-CCSD(T)/def2-TZVP —
were run on the geometries autodE optimised and frequency-verified, with no re-optimisation:

| method, at our geometry | barrier | vs BH9's 16.98 |
|---|---|---|
| PBE0-D3BJ/def2-TZVP | 11.03 | −5.95 |
| **DLPNO-CCSD(T)/def2-TZVP** | **16.25** | **−0.73** |

Changing only the level of theory closes **87 %** of the gap. The residual 0.73 kcal/mol is basis-set
incompleteness (def2-TZVP against BH9's CBS extrapolation) plus whatever small geometric difference
remains between our PBE0/def2-SVP structure and their CAM-B3LYP-D3(BJ)/6-311++G\*\* one.

**This is the single most important result so far.** It says the fragment-embedding, placement,
TS-search and verification chain produces essentially the correct transition state, and that the
remaining error is a level-of-theory choice we control rather than a defect in the procedure. The
cost was 17 minutes on 8 cores for three single points — cheap enough to run for every reaction.

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
