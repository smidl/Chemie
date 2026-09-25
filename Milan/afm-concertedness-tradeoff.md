# The concertedness axis: what the released checkpoints actually do

Measured 2026-09-22, eval only, no retraining. Released `nano` checkpoints of
the three flow models (same body, same featurisation, same width — the
elementary event is the only variable). Data: FlowER's own test split, cut into
strata by how many moves a step needs.

## 1. The axis, and why it was built

Two results of the paper meet on one quantity, the number of matrix positions a
step couples:

* Theorem 1 and the path-variance appendix: the entrywise bridge's electron
  count has variance `κ(1−κ)·Σ_e w_e² Δ_e²`, linear in the number of changed
  positions. A six-position step gives σ ≈ 2.4 electrons at κ = ½.
* The jam appendix: a pericyclic step is jammed *as arrows* and is dissolved by
  the alphabet's split of the migration.

Predicted: the AFM-minus-entrywise gap grows with `Σ w²Δ²`, largest on the
concerted steps. **Refuted below.** The gap runs the other way.

## 2. Strata (`analysis/concertedness.py`, model-free)

Every alphabet move changes exactly one off-diagonal entry by one, so the
minimal move count is `m = Σ_{i<j}|ΔB_ij|`, read straight off the two matrices.
The changed bonds form a graph on atoms; its components are the walks of the
decomposition appendix, and a component with no diagonal change at any of its
atoms and all degrees two is a **cycle** — the pericyclic case.

| | train (every 5th step, ×5 ≈ full) | test (all) |
|---|---|---|
| non-identity steps | 317,222 (≈1.59 M) | 179,679 |
| ≥3 moves | 27.6% (≈438,000) | 27.8% |
| ≥6 moves | 9.5% (≈151,000) | 9.8% |
| cyclic component | 7.5% (≈120,000) | 7.7% |
| … six-bond cycles | ≈71,600 | 8,277 |
| cycles alternating break/form | **100%** | **100%** |
| odd parity (single-electron) | 2.46% | 2.54% |

Three things worth the paper: the cycle rate independently reproduces the
paper's own "a twentieth of non-identity steps"; every one of 37,834 cyclic
components alternates, which verifies the walk theory on the whole corpus
rather than arguing it; and `Σ w²Δ²` is a chemical classifier with no chemistry
in it — 16 for a two-move polar step (76% of the corpus), **24 for a six-bond
cycle**, which is the paper's own worked example.

Strata files: `test_m1` 14,617 · `test_m2` 115,098 · `test_m3to5` 32,391 ·
`test_m6plus` 17,573 · `test_cyclic` 13,892.

## 3. Accuracy: the gap runs the other way

Top-1 step accuracy, identical 6,000 steps per stratum, sampling + frequency
(the protocol every model can fill).

| stratum | AFM | Discrete FlowER | continuous FlowER | AFM − DFE | ceiling |
|---|---|---|---|---|---|
| m1 (8% of test) | **0.8635** | 0.8418 | 0.7820 | **+2.2** | 0.956 |
| m2 (64%) | **0.8502** | 0.8308 | 0.8172 | **+1.9** | 0.986 |
| m3–5 (18%) | 0.8518 | **0.8663** | 0.8120 | −1.5 | 0.968 |
| m6+ (10%) | 0.7782 | **0.8700** | 0.7817 | **−9.2** | 0.987 |
| cyclic (7.7%) | 0.9310 | **0.9520** | 0.8927 | −2.1 | 0.989 |

Validity and electron/atom/proton conservation are **1.0000 for AFM on every
stratum**, including the most concerted; Discrete FlowER runs 0.95–0.98 validity
and 0.93–0.96 electron conservation, continuous FlowER 0.75–0.80. Theorem 1's
cost is real and is visible — in conservation, not in accuracy.

## 4. It is not the decoder

AFM under all three regimes it can fill:

| stratum | sample/freq | beam/score | beam/marginal | beam top-3 | beam top-10 |
|---|---|---|---|---|---|
| m1 | 0.8635 | **0.8867** | 0.8235 | 0.9985 | 0.9992 |
| m2 | 0.8502 | 0.8535 | 0.8492 | 0.9820 | 0.9975 |
| m3–5 | 0.8518 | 0.8363 | **0.8765** | 0.9493 | 0.9570 |
| m6+ | 0.7782 | 0.7540 | 0.7748 | 0.9822 | **0.9932** |
| cyclic | 0.9310 | 0.9232 | **0.9363** | 0.9900 | 0.9953 |

Beam does not help at m6+, and neither does the marginal rule that sums
trajectory probability over all routes to one product — the correction
Limitation (ii) calls for. So the deficit is not order ambiguity and not the
ranking rule. (The marginal rule *is* the better ranking wherever steps are
long: +4.0 points at m3–5, +2.1 at m6+, +1.3 on cyclic; and the worst on
one-move steps, −6.3, where a product has only one route.)

What the same runs show is that the answer is reachable: with beam the recorded
product is in AFM's ten candidates **99.3%** of the time at m6+ and in three
98.2%. The model builds the right chemistry and ranks it second.

## 5. Why: compounding, measured rank-free

`experiments/stratified/strata_likelihood.py`, 800 steps per stratum. The
recorded step's own move sequence is teacher-forced and its trajectory
log-probability compared with the model's best sampled trajectory. Neither
number comes from a ranking rule.

| stratum | mean moves | median per-decision p | best sampled = recorded product | median margin (nats) | within 1 nat |
|---|---|---|---|---|---|
| m1 | 1.0 | 0.707 | 60.8% | 0.00 | 97.8% |
| m2 | 2.0 | **0.987** | 77.6% | 0.00 | 98.5% |
| m3–5 | 3.5 | 0.932 | 67.8% | 0.00 | 85.6% |
| m6+ | 7.7 | 0.820 | **27.6%** | **0.89** | 53.9% |
| cyclic | 7.1 | 0.816 | 39.4% | 0.38 | 57.3% |

Read off the table:

1. **Per-decision quality holds up.** 0.82 median at m6+ against 0.99 at m2 —
   the model is not lost on concerted chemistry; each individual move of the
   chemist's route stays probable.
2. **The route probability compounds.** 0.82 per decision over 8.7 decisions is
   0.18 for the whole route, against 0.96 for a two-move step. This is
   structural for a sequential factorisation, not a training failure.
3. **The preference is genuine.** At m6+ the model's best trajectory reaches a
   different product in 72% of steps, with a median margin of 0.89 nats (≈2.4×);
   only 54% of steps are within one nat, against 98.5% at m2, where the median
   margin is exactly zero. On short steps the model is tied with itself and the
   ranking rule decides; on long steps it has a real opinion and it differs
   from the record.
4. **Confidence peaks at the corpus mode.** Per-decision probability is highest
   at two moves (64% of training) and falls away on both sides.

## 6. What this says for the paper

The paper's "the guarantees are not paid for in accuracy" is true *on average*
— 72% of the corpus is one- or two-move steps, where AFM leads by ~2 points.
Stratified, there is a price, and it sits on the concerted tail: −9.2 points at
six or more moves, 10% of the corpus. That is the exact dual of Theorem 1, and
stating both is stronger than stating one:

* an entrywise event buys a one-shot endpoint and pays in conservation and
  validity (measured: 0.93–0.98 and 0.75–0.80);
* a sequential event in `ker N` buys conservation and validity of exactly one
  and pays in compounding over decisions (measured: −9.2 points at m6+, route
  probability 0.18 against 0.96).

Neither is a defect to hide; together they are a trade-off with numbers on both
sides. The honest framing for Limitation (ii) is no longer "the score is a lower
bound" but "accuracy decays with the number of moves a step needs, and here is
the curve".

**The constructed-OOD retrain is not worth funding on this axis.** Holding out
pericyclic chemistry and retraining three models (~80 GPU-hours) was to test
whether AFM extrapolates better there. The eval-only measurement already says it
does not lead there at all. Cost of finding out: one afternoon of CPU and about
three GPU-hours.

## 7. Open

1. Separate order preference from product preference: the best sampled
   trajectory *that reaches the recorded product*, against the recorded route.
   Cheap, and it says whether the 0.89-nat margin is about the product or the
   path to it.
2. Are AFM's preferred long-step products chemically defensible? Branch-aware
   scoring moves m6+ by only +0.9 points, so they are not other recorded
   products of the same reactant. A chemist's eye on twenty, drawn with
   `experiments/draw_arrows/`, would settle whether this is a model error or an
   incomplete record.
3. The per-decision probability is flat-ish (0.82–0.99) while accuracy is not.
   A length-normalised ranking rule, or an exact product likelihood by summing
   over admissible orders (the paper's own open direction), is the obvious
   thing to try — and now has a stratum to be measured on.

## 8. Files

`analysis/concertedness.py`, `analysis/results/concertedness_{test,train}.json`;
`experiments/stratified/{strat_*.sbatch,beam_*.sbatch,strata_likelihood.py,likelihood_afm.sbatch}`;
metrics on bayes under `/data/smidl/ArrowFlowMatching/outputs_strata`,
`outputs_beam_score`, `outputs_beam_marginal`, `outputs/strata_likelihood_afm.json`.
