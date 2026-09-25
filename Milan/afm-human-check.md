# Does AFM's own scoring agree with the chemist?

Short summary of the check in `experiments/human_plausibility/` (full detail,
caveats and code pointers there).

## Question

AFM's mechanisms are meant to be human-readable, not just correct products. A
prior check showed the four-move alphabet can *represent* 96.68% of RMechDB's
curated chemist mechanisms — but that's a property of the alphabet, not the
trained model. This asks the sharper question: when the model draws its own
candidate mechanisms for a reaction, does it actually *prefer* the chemist's
mechanism, or merely find it reachable?

## Data

- **RMechDB** (Baldi & Van Vranken, UC Irvine; CC-BY-NC-ND): 5,426 curated
  literature radical elementary steps with chemist-drawn curly arrows.
- Restricted to the **2,057 "exact arrow match" reactions** — where the
  chemist's arrows translate unambiguously into one specific alphabet move
  sequence. The other 60.8% of decomposable steps are chemically equivalent
  but drawn differently, with no single canonical sequence to call "the
  chemist's mechanism," so they're excluded rather than guessed at.
- Model: `afm_nano` checkpoint — the AFM architecture at the smallest width
  in the paper's own comparison-table ladder (1.2M params), never trained on
  RMechDB's radical chemistry specifically.

## Algorithm

1. For each reaction, take the chemist's move sequence (already computed by
   `analysis/rmechdb_arrows.py`) and score it under the trained model,
   teacher-forced — i.e. sum the model's own log-probability at each step of
   the chemist's actual path, rather than letting the model choose.
2. Separately, sample 200 mechanisms the model would generate on its own for
   the same reactant, and collapse them to distinct mechanisms by score.
3. Rank the chemist's mechanism among those distinct candidates (1st = the
   model's own best guess; last = its own worst), broken down by how many
   distinct mechanisms the model actually produced — a fair rank out of 2 is a
   different claim than a fair rank out of 11.

## Result (2026-09-17)

| distinct mechanisms the model drew | # reactions | human ranks 1st | human ranks last |
|---|---|---|---|
| 1 (no real choice — not a test) | 1,433 (70%) | trivial | trivial |
| 2 | 275 | 97.1% | 2.9% |
| 3 | 81 | 91.4% | 0.0% |
| 4 | 64 | 92.2% | 1.6% |
| 5 | 35 | 85.7% | 0.0% |
| 6–10 | 92 | 92.4% | 0.0% |
| 11+ | 77 | 76.6% | 0.0% |

Across the **624 reactions where the model genuinely had a choice**: it ranks
the chemist's mechanism as its own single best guess **92.0%** of the time,
and dead last only **1.4%** of the time. The top-1 rate declines as the number
of real alternatives grows (97% at 2 choices → 77% at 11+), which is the shape
a real effect should have — not a flat 100% (over-fit metric) or a flat ~50%
(no signal).

## Headline caveat

`nano` is the smallest width in the paper's own ladder and was never trained
on this (radical) chemistry, so this is a lower bound on what a full-scale,
in-distribution checkpoint would show, not the ceiling. RMechDB itself is a
curated notational choice, not a physical ground truth. Full caveats in
`experiments/human_plausibility/README.md`.

## Scope of the result above, sharpened (2026-09-18)

The rank test was run on the exact-match set, which is **single-move**
(one homolysis or one colligation). `problem02-termination.md` shows that is
precisely the sector the released checkpoint knows: on the multi-move
RMechDB steps (`multistep.json`, 2,814 reactions, 78% of them one-radical
propagation steps) the model reaches the chemist's product in **0.6%** of
chains, because after the first homolysis it terminates (p(Stop) = 0.995) —
the FlowER corpus's odd-parity chemistry is one Pd–P move deep (main.tex
2784–2797). So the honest statement of the released-checkpoint result is:
*agreement with the chemist is near-exact on the one-move radical sector and
zero one move beyond it.* Both halves belong in the write-up.

## Track 2 — fine-tune on RMechDB, score on a held-out split (in progress)

Question: can the approach learn chemist-like *multi-move* radical mechanisms
from a few thousand examples, keeping the guarantees and the readable
intermediates? This changes the claim from "the paper's model agrees with
chemists" to "the approach does", so it is reported separately and only on
data the fine-tune never saw.

- **Data**: `experiments/finetune/make_rmechdb_flower_split.py` converts
  every alphabet-expressible RMechDB step (`targets.json` + `multistep.json`)
  to FlowER's own format: reactant with every hydrogen an explicit mapped
  atom, product *constructed* by applying the chemist's moves and written
  back with the repo's `product_mapped_smiles_from_be`, round-trip checked
  (46 of 4,871 dropped for mismatch, 463 exact duplicates removed). 4,362
  steps in 3,950 reactant groups; split **80/10/10 by reactant group**
  (3,485 / 444 / 433), so a reactant with several recorded products never
  straddles train and test. Class mix per split in `data/rmechdb_ft/manifest.json`
  (train: abstraction 1,149, recombine 935, homolyze 664, addition 421,
  retroaddition 197, resonance 119; 1,566 one-move, 1,747 two-move, 172 longer).
- **Code**: `filter-only` lineage (its generalised `_radical_moves` is what
  makes two-single-electron-move steps *usable* training targets; `master`
  would drop every propagation step), plus one additive option in
  `train.py`, `init_weights=<ckpt>`: weights only, fresh optimizer and
  schedule (the existing `load_from` resumes the original run's optimizer,
  cosine schedule and epoch counter, which is wrong for adapting to a small
  new corpus). Commit `ea6c2af`.
- **Runs** (bayes, 3× RTX 3070, `sbatch`): (A) fine-tune from the released
  `afm_nano` on RMechDB only; (B) the same with a 20k-step FlowER replay
  mixed into training, to measure forgetting; (C) `nano` from scratch on
  RMechDB only, the control for "does pre-training on FlowER help at all".
  Effective batch 96 (24 × 4 accumulation), lr 5e-5 for A/B, short warmup,
  early stopping on RMechDB validation loss.
- **Scoring**: `instrumented_rollout.py --flower_txt test.txt` +
  `analyze_accuracy_txt.py` + `analyze_parity.py --mapped` +
  `teacher_forced_test.py` on **`test.txt` only** (433 steps, 3 chains each),
  the released checkpoint scored identically on the same 433; `eval.py` on
  FlowER's test split for A/B/C to report what was forgotten.

### Track 2 result (2026-09-18; runs of ≤40 epochs, minutes each on one RTX 3070)

Exact canonical match of the emitted state to the chemist's product, held-out
`test.txt`:

| checkpoint | chain match | any of 3 | stuck | abstraction (1 radical, n=102) | addition (1 rad., 54) | retroaddition (1 rad., 28) | resonance (1 rad., 13) | recombine (2 rad., 83) | homolyze (0 rad., 56) |
|---|---|---|---|---|---|---|---|---|---|
| released `afm_nano` | 45.4% | 45.7% | 21.6% | **0.0%** | 0.0% | 0.0% | 0.0% | 99.6% | 97.6% |
| A: fine-tune, RMechDB only | 84.1% | 90.5% | 0.8% | 85.3% | 46.3% | 69.0% | 74.4% | 99.2% | 96.4% |
| B: fine-tune + 20k FlowER replay | **86.5%** | **91.2%** | 0.5% | **89.9%** | 50.0% | 71.4% | **87.2%** | 98.4% | 98.2% |
| C: from scratch, RMechDB only | 82.2% | 89.8% | 0.2% | 84.0% | 43.2% | 63.1% | 48.7% | 100.0% | 95.8% |

The released model is exact on the one-move sector and zero one move beyond
it, as `problem02-termination.md` predicted. Three to four thousand chemist
steps move the multi-move classes from 0% to 70–90%; pre-training on FlowER
buys 2–4 points overall and most where data is scarcest (resonance: 87% with
replay vs 49% from scratch). `addition` (radical + alkene) stays the weakest
class at ~50% — worth a look at *which* alkene carbon the model attacks
(regiochemistry), since the chemist's product is one of two.

**The mechanism moved exactly where the diagnosis said it would.**
Teacher-forced on the test split's two-move `abstraction` routes, after the
chemist's own homolysis: released p(Stop) = 1.000, p(colligation) = 0.000;
fine-tuned (B) p(Stop) = 0.044, p(colligation) = 0.887, whole route 0.70
(median 0.96). The parity table (`analyze_parity.py --mapped`) shows the
same: at a state with two fresh radicals plus the reactant's own (i.e. right
after the first homolysis) the released model chose `Stop` 100% of the time
(94/94), the fine-tuned models 4–7%; at the propagation-product signature
(one fresh radical, the reactant's healed) all four models stop at 90–99%.

**Readability improved, not degraded.** On the same test chains, the
fraction of intermediate states that are molecules (in the Sector) went
from 11.9% (released, wandering) to **81.0%** (B), reconstruct 14% → 81%,
force-field converge 14% → 80%; emitted finals 100% in Sector for every
checkpoint (Proposition 2). A fine-tuned chain reads "break C–H, form O–H,
stop" — the chemist's arrows, in order.

Still to add: `eval.py` of A/B/C on FlowER's own test split (what the
fine-tune cost on the original task), and the regiochemistry check on
`addition`.


---

## SUPERSEDED 2026-09-21 — see `handover-readability-appendix.md` §4.1

The canonical rerun this file was about had **already been done** on 20 Sep and is
written up, correctly, in `handover-readability-appendix.md`. That document is
authoritative for these numbers; this file is the earlier, narrower experiment.

**What changed.** `targets.json` was regenerated with the **same-electron-flow**
gate (bond-to-bond arrows canonicalised through their shared atom) instead of the
old exact-as-drawn gate: **2,057 → 4,301** reactions, of which **2,244 are
multi-move**. The 92.0 % here is reproduced exactly on its own set and is **not
wrong — it is narrow**: it covered only the one-move sector, which
`problem02-termination.md` shows is the sector the released checkpoint already
knows.

| chemist's route | model | steps | drew ≥2 mechanisms | ranks first |
|---|---|---|---|---|
| one move | released `M0` | 2,057 | 129 | 88.4 % |
| **two or more** | released `M0` | 2,244 | 1,811 | **0.0 %** |
| one move | fine-tuned `M_B`, **held-out only** | 200 | 35 | 94.3 % |
| **two or more** | fine-tuned `M_B`, **held-out only** | 230 | 165 | **63.0 %** |

The released model ranks the chemist's multi-move mechanism first **zero times in
1,811**. Not rarely: never. Three to four thousand chemist steps take that to
63 % on data the fine-tune never saw.

> **⚠ A trap I fell into on 2026-09-21, recorded so nobody repeats it.** Scoring
> `M_B` on all 4,301 gives 76.4 % overall and 71.2 % multi-move. **Those numbers
> are inadmissible**: `M_B` trained on 3,929 of the 4,301, so they are largely a
> measurement on training data. `M_B` may only be scored on `D_test` — 430 steps,
> 395 reactants — which the handover does and which gives 63.0 %. The scored
> artefacts in `results/scores_canonical_ft_mixed.jsonl` cover all 4,301, so the
> restriction has to be applied at analysis time; nothing in the file enforces it.
