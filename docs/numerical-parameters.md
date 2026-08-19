# How much of our barrier is numerical settings?

**Date:** 2026-08-19 · job `11368429`, 7 min on 8 cores · `admissibility/numerics93/`

DFT is deterministic, so this needs no statistics — four settings, four numbers, and the differences
*are* the answer. Same three geometries (reaction 93's TS and both reactants, as optimised and
frequency-verified by autodE), same functional and basis, only the numerical parameters varied.

| setting | barrier | vs autodE's default |
|---|---|---|
| as autodE ran it — `PBE0 RIJCOSX D3BJ def2-TZVP`, ORCA defaults | 11.034 | — |
| `+ TightSCF` | 11.006 | **−0.028** |
| `+ DefGrid3` | 10.987 | **−0.047** |
| exact exchange (`RIJCOSX` removed) | 10.987 | **−0.047** |

**The entire numerical contribution is 0.047 kcal/mol.** SCF convergence accounts for 0.028 of it and
the integration grid for the remaining 0.019. Removing the chain-of-spheres approximation changes the
result by **0.000** — at `DefGrid3`, RIJCOSX is exact to three decimals for this system.

## What this settles

Against the errors that matter, this is nothing:

| source | magnitude | ratio |
|---|---|---|
| numerical settings | 0.047 | 1× |
| DLPNO-CCSD(T) residual vs BH9 | 0.84 | 18× |
| PBE0 method error | 3.80 | **81×** |

So **autodE's defaults are fine and there is no tightening to be done.** More usefully, it removes a
suspect: the damaging-versus-benign error pattern identified in `barrier-accuracy-requirement.md`
cannot be an artefact of our own configuration. Whatever structure our error has, it comes from the
functional and the basis, not from convergence thresholds, grids, or the COSX approximation.

That was worth ten minutes to establish rather than assume — and it was only measurable this cleanly
*because* the computation is deterministic. Had error genuinely been noise, separating a 0.047
kcal/mol effect would have required far more than four calculations.
