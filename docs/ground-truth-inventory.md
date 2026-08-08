# Ground truth for the barrier pipeline — what we have, and the hole in the middle

**Date:** 2026-08-08 · **Scripts:** `/mnt/data/resynthesis/admissibility/scripts/D0_select.py`,
`D1_frag.py` · **Logs:** `logs/select-11320369.log`, `logs/frag-11320374.log` ·
**Index:** `out/t1x_index.json`, `out/t1x_fragments.json`

## The two sets we hold

| | Transition1x | specialty_11 |
|---|---|---|
| n | 10 073 reactions | 11 reaction steps |
| reference barrier | **yes** — ships the wB97X/6-31G(d) path, so max(E) − E_endpoint is a true reference | **none** — the `reference` field holds `xtb_dE_kcal: null` |
| size | 4–23 atoms, median **14** | specialty-scale, ionic in places |
| elements | **CHNO only** (171 formulae) | plus Cl, quaternary N, carboxylates |
| charge | neutral, gas phase | some steps need solvation; `solvation_required` is a field |
| provenance | curated TS dataset | real planner output on an industrial HCN target set, balance-repaired and machine-verified |

Barrier distribution in Transition1x, after correcting the units — **the file is in eV, not Hartree**,
the same trap that made July's reference barriers 27× too large: p05 **9.5**, median **53.2**,
p95 **143.7** kcal/mol.

## The hole: our reference set cannot test the thing that broke

The July failure was **multi-fragment endpoint construction**. Transition1x scored 450/450 and that
was read as the pipeline being sound. Checking connectivity by covalent-radius overlap on every
reactant frame in the file:

| fragment count of the T1x reactant geometry | share |
|---|---|
| 1 fragment | **99.9 %** (10 060) |
| 2 fragments | 0.1 % (13) |

Against **92.6 %** multi-fragment for real USPTO reactant sides.

So Transition1x is **structurally incapable** of exercising the failure mode. Its reactions are one
connected supersystem given as a single atom set with pre-aligned geometries; there is nothing to
place. The 450/450 was never evidence about the path that broke — it was a clean score on the one
part of the problem that was never at risk.

This is the same shape as the OOD finding a week earlier: a benchmark that was internally sound and
measured something other than what it was credited with.

## Consequences for "what is the best computational route"

The two sets are **disjoint in exactly the wrong way**:

- where we have ground truth (T1x), the hard step — fragment placement — does not occur, and
  accuracy of a rung can be scored honestly;
- where the hard step occurs (specialty, USPTO), we have **no reference barrier at all**, so a rung
  can only be scored against another rung.

Any statement of the form "level *L* is the best accuracy/cost tradeoff" therefore rests on a
transfer from a domain that excludes the failure to a domain where it dominates. That transfer is
an assumption, not a measurement — and it is precisely the transferability question that the
physics track was asked to open.

## What closing this requires

1. **A golden set with genuine references in our own domain.** Roughly 6–8 multi-fragment,
   specialty-like reactions with barriers that are either (a) literature/experimental values, or
   (b) computed once at a high level with real convergence and treated as the reference. Neither
   exists today. This is the single largest gap.
2. **Atom maps for that set.** `build_endpoints` requires a map number on every atom including
   hydrogens and refuses to guess. For 6–8 reactions, hand-mapping is feasible *and* auditable — a
   reviewing chemist can check the mapping, which a mapper's output does not invite.
3. **Cross-rung comparison done on the same surface.** The 12.5 % spurious-rejection rate measured
   in July came from mixing one rung's geometry with another rung's energy; the ladder mixes levels
   by construction, so each rung must re-optimise.

Until (1) exists, the walkthrough can show a chemist *everything the pipeline does and every number
it produces* — which is enough to have the method criticised — but it cannot rank the rungs on
accuracy in our own domain. Those are different deliverables and should not be conflated.
