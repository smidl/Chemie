# Draslovka experiments — isolated demo-prep line

Self-contained record of the "what can our current pipeline do on Draslovka products"
probes. **Isolated from the research tree on purpose** — this is partner-demo prep, not
a coord node (yet). Nothing here should be read as a research result about L\*/ξ_f.

## Where things live
- **Scripts:** `scripts/` (mirror of the RCI copies).
- **Results (JSON):** `results/`.
- **RCI home:** `/mnt/data/resynthesis/draslovka/` (`scripts/`, `out/`, `logs/`, `data/`).
  The **search** drivers import the SEEA_star harness (`Cluster_sampling`, `valueNet`,
  `saved_model/{best_epoch,lstar_broad}.pt`) and must run *from*
  `/mnt/data/resynthesis/repro/SEEA_star/Retrosynthesis/`. The **feasibility** scorers need
  only the ReactionT5 venv (`/mnt/data/resynthesis/rxnt5_venv`, `HF_HOME=/mnt/data/resynthesis/hf_cache`).
- **Targets (6, canonicalized):** `data/draslovka.pkl` — acetone cyanohydrin, MMA, phenytoin,
  5,5-dimethylhydantoin, EDTA, chlormequat. (5/6 are already purchasable commodities in eMolecules.)

## Experiments
| # | script | question | key result |
|---|---|---|---|
| 1a | `draslovka_eval.py` | route to each product (target removed from stock), standard value net vs L\* | all 6 solved in **1 step** (commodity stock) — route existence is trivial & undifferentiating |
| 1b | `draslovka_feasibility.py` | forward round-trip feasibility of the 6 proposed steps | **catches the MMA hallucination**; but **false-neg on chlormequat** (quaternary salt, OOD for ReactionT5) and **false-pos on EDTA** (trivial protonation passes) |
| 2 | `draslovka_deep.py` | force multi-step routes from bulk/platform feedstock (HCN, acetone, cyanide, urea, benzil…) | 6/6 solved; **L\* more search-efficient on EDTA (21 vs 49 expansions)** but not uniformly (hydantoin: 5 vs 4 steps). Multi-step routes are **chemically unsound** (EDTA via acetate alkylation = wrong; hydantoin roundabout) |
| 3 | `draslovka_feas_deep.py` | audit every step of the multi-step routes | *(capstone — see RESULTS.md)* |

## Honest bottom line (for the pitch, evidenced on their molecules)
1. Route *existence* is not the problem — their products are commodities, and forced-deep
   routes are chemically unsound (errors compound with depth).
2. A feasibility layer catches gross hallucinations (MMA) — the core value.
3. A **generic** feasibility model misjudges their specialty chemistry (chlormequat) → the
   deliverable must be a **tuned, multi-signal** feasibility layer; **their data closes the gap.**
4. L\* buys search efficiency (EDTA 21 vs 49) but is a modest, non-uniform improvement — don't oversell.

## Reproduce
```
# search (from the harness dir):
cd /mnt/data/resynthesis/repro/SEEA_star/Retrosynthesis && sbatch <this>/scripts/draslovka.sbatch
# feasibility (from the isolated home):
cd /mnt/data/resynthesis/draslovka && sbatch scripts/feas_deep.sbatch
```
