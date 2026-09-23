# Appendix E — provenance and reproducibility

## Where the work lives
`/mnt/data/resynthesis/NemecChallenge` on RCI. Code is a working copy of
`aicenter/retrosyntesis`; the shared checkout was not modified. Local patches in
`patches/`.

## Environments
| env | contents | used for |
|---|---|---|
| `nemec` (conda, py3.10) | aizynthfinder 4.4.1, rdchiral 1.1.0, route_distances 1.2.4 | planning, scoring, diversity |
| `rfb` (conda, py3.11) | syntheseus 0.7.2, transformers 5.16.1 | ReactionT5 arm |

**The pipeline as committed was not runnable by the owner**: `script/run_p.sh`
sources `/home/moczyjor/.../venv_chimie`, unreadable outside that account. The
`nemec` env and `scripts/run_p.sh` replace it.

## Code fixes made during this work
| # | fix | file |
|---|---|---|
| 1 | route de-duplication keyed on the **molecule tree**, not template SMARTS — chemically distinct routes were being discarded as duplicates | `src/validation/validation_v.py` |
| 2 | stereo rung rewritten: it keyed on `template_smarts`, which only the RetroFallback planner emits, so under AiZynthFinder it checked **zero steps** and still reported "validated" | `src/validation/validation_rdchiral.py` |
| 3 | knowledge scoring applied at the policy **container**, not to the `uspto` policy object — previously actions from a second policy bypassed scoring entirely and kept raw priors | `src/planning/planning_aiZynthFinder.py` |
| 4 | `--policies`, `--seed`, `--time_limit`, `--knowledge_mode/weight` exposed | same |

Fixes 1 and 2 are also applied to repo `main` (uncommitted).

## Reproducibility caveats — read before quoting numbers
- **`--seed` has no effect, and the runs are nondeterministic anyway.** Two
  claims, measured separately on iteration-bounded runs (2026-09-04):

  | test | routes | shared | verdict |
  |---|---|---|---|
  | identical parameters, run twice (`uspto-s0-A` vs `-B`) | 867 / 861 | 578 | **differ** |
  | seed 0 vs seed 7 (`uspto-s0-A` vs `uspto-s7`) | 867 / 860 | 582 | differ, but no more than the same-seed rerun |

  So changing the seed changes nothing beyond ordinary run-to-run noise — AZF has
  no `random_seed` in its search config and its selection is UCB argmax — but the
  search is **not** reproducible either. Same inputs, same budget, ~67 % route
  overlap. The likely cause is thread-nondeterministic ONNX inference
  (`OMP_NUM_THREADS=4`): tiny floating-point differences in the priors flip
  argmax decisions and the trajectories diverge.

  **This corrects an earlier claim in this project's notes that "AiZynthFinder's
  MCTS is deterministic here."** That was inferred from the `ringbreaker`-only
  configuration returning identical sets across seeds; that search terminates
  after 5 routes, too early to diverge, and generalising from it was wrong. To get
  reproducible runs, pin threads to 1 and re-test.
- **The 63-route corpus in this report came from wall-clock-capped runs**
  (`--time_limit 600` against a 1000-iteration request), so each run stopped at a
  different iteration count depending on node load. Route *counts* from those runs
  are not reproducible; the routes themselves are real planner output against a
  real stock.
- **The cap was severe.** The same configuration run to its full 1000 iterations
  yields **860–867 routes**, against 10–24 under the 600 s cap. Every route count
  in the main report is therefore a floor, not a measurement, and the diversity
  and scoring analyses were run on the small truncated corpus.
- Iteration-bounded re-runs have now completed: AZF 860–867 routes per arm;
  **ReactionT5 solved MU1700 under both retro-star and breadth-first**, 400
  reaction-model calls, ~4.4 h each on CPU. Only one route is extracted per T5 run
  because our serialiser walks a single solved subtree — that is a limitation of
  our extractor, not of the search, and it means the T5 arm is not yet comparable
  on route *count*.
- Four experiments separating budget from policy-prior scaling (§7) were still
  running at the time of writing: jobs 11480257–11480260.
- **ReactionT5 GPU jobs failed**: the `rfb` torch build is CUDA 13.0, the cluster
  driver is 12.9. Rerun on CPU at ~35 s per reaction-model call.

## Branch warning
`main` and the branch deployed on RCI (`retropfn/active-xif`) disagree about which
validation rungs exist — `main` carries the DFT/NEB/MLIP/energy ladder, the branch
carries none of it. **Any statement about what the pipeline validates must name
the branch.** No physics rung was run for this report.

## Not included
ASKCOS (not installed), Chemformer/LocalRetro/MEGAN/GLN (no weights deployed),
reaction conditions (no capability), computed barriers (not run), any
experimental validation.
