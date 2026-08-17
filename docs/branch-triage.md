# retrosyntesis — branch triage after the departures

**Date:** 2026-08-17 · 24 remote branches assessed against `origin/main`.

## Summary

| verdict | branches | action |
|---|---|---|
| **merge now** | 1 | `18-handover` — Robin's completed integration, never merged |
| salvage selectively | 2 | cherry-pick, discard the rest |
| already in main (0 commits ahead) | 14 | delete; nothing is lost |
| superseded | 6 | tag, then delete |
| **rebuild from scratch** | **0** | nothing here is worth reimplementing |

## Merge now — `18-handover`

Robin's last commit, **2026-08-07**, `be97b69`:
*"fix(dft-neb): fragment-wise endpoint construction + non-bonded clash guard for specialty_11"*.
**1392 insertions across 8 files**, and it **merges cleanly** into current main (0 conflicts).

| file | lines | what it is |
|---|---|---|
| `src/validation/reaction_complex.py` | 304 | the July handover module, brought into `src/` |
| `src/validation/validation_dft_neb.py` | +225 / −18 | **the integration itself** |
| `src/oracle_benchmark/specialty11_kinetics_runner.py` | 319 | runner for the 11-reaction specialty set |
| `src/oracle_benchmark/data/specialty_11.py` | 93 | the dataset |
| `tests/test_reaction_complex.py` | 166 | tests |
| `tests/test_dft_neb_guard.py` | 104 | tests |
| 2 shell scripts | 199 | GPU runner, verification |

His edits to `reaction_complex.py` are **48 lines, almost all docstring** — rewriting the module's
framing for its new home and pointing at the real integration points rather than at a handover note.
The logic is unchanged. His commit message also records what he deliberately left out, as belonging
to an unfinished AIMNet2 migration and "not committable as-is".

This is the July diagnosis actually landing in the codebase, with tests. It is the single highest-value
artifact left behind, and it was one merge away from main when he stopped.

**Known caveat:** the integrated pipeline was reported failing at `failed_geometry_optimization` after
this commit. Merging brings in working, tested code with a known *next* bug — still worth having.

## Salvage selectively

**`feature/FlowER_Model_Implementation`** (3 commits, 46 files). The FlowER benchmark itself is
superseded — FlowER's embedding was measured **not barrier-relevant** (ρ 0.24–0.28, below structural
fingerprints) and the line was closed. But the branch also carries `extraction_book_synthesis/`
(green-routes dataset and analysis), which is independent data work. Cherry-pick that; drop the rest.

**`feature/retro-fallback`** (3 commits, 911 files). Mechanism-GP scale-up and route comparison. The
route-level result is already flagged as **confounded** — fixed absolute threshold against differing
per-arm score distributions, plus route-length compounding — and was sent back for a
calibration-matched rerun, so the *results* should not be merged. The harness (`_run_arm.py`,
`_compare_routes.py`, `compare_fm.py`) may be worth keeping, but **check for duplication first**: copies
of `_run_arm.py` and `_compare_routes.py` already exist under `retro-pfn` on RCI.

## Already in main — delete

Fourteen branches have **0 commits ahead** of main: `feature/knowledge-planner-integration`,
`…-retroXpert`, `feature/phase1-paroutes-benchmark`, `feat/oracle-and-route-benchmarks`,
`feature/s3-rxnscribe-extraction`, `feature/MEEA_KeeA_exploration`, `feature/budget-non-binding`,
`feat/rxnscribe-integration`, `feature/generative-model`, `10-validation-upgrade`,
`feature/metrics-audit`, `17-validation_filter`, `feat/ood_correction`, `coord-channel`.

They are ancestors of main. Deleting them loses nothing and removes 14 of 24 entries.

## Superseded — tag, then delete

`feature/phase2-validation_approach` (1521 files, mostly vendored MolScribe egg-info, June),
`feature/Knowledge-api` (May, retroXpert reports for three drugs), `feature/phase2-USPTO`,
`feature/multi-search-algorithms`, `feature/retrostar-run` (May–June benchmark runs, superseded by
the 190-hard-target work now on main), `feature/integration-syntheseus` (1 commit, 6 files).

Tag each as `archive/<name>` before deleting, so the commits stay reachable without cluttering the
branch list.

## Nothing warrants a rebuild

The one genuinely valuable branch is a clean one-commit merge. Everything else is either already in
main, superseded by a later result, or invalidated by a known confound. There is no case where
reimplementing would cost less than merging, because there is no case where merging is hard.
