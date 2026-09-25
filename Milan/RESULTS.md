# AFM / MechReact — collected results

All model numbers: nano width, sampling + frequency ranking (the paper's Table 1 protocol).

## 1. Pipeline calibration

| metric | ours | paper Table 1 |
|---|---|---|
| top1 | 0.8694 | 0.8692 |
| top10 | 0.9864 | 0.9862 |
| validity | 1.0000000 | 1.0000000 |
| electron | 0.9999995 | 1.0000000 |

Pipeline reproduces the published row. The 0.9999995 electron/proton figure traces to one candidate in 2.19M whose reactant carries `[HH]` (H2 as one mapped node with an *implicit* second H) — a corpus row violating the explicit-hydrogen convention, 35 train + 6 test lines. Theorem intact.

## 2. Benchmark characterisation

- Unseen step types in the released split: **0.0757%** (core arrow pattern), **1.9145%** (1-hop template). The split asks for no extrapolation.
- Corpus train: single-electron moves **0.20%** of 366,178 applied; steps admitting no order **0.049%** (paper says 0.05%).
- Corpus test: single-electron moves **0.15%** of 366,828 applied; steps admitting no order **0.053%** (paper says 0.05%).
- USPTO-Full: 62,319/1,808,937 = **3.45%** balanced+mapped as recorded. FlowER's template pipeline covers 289,024 of 1,100,105 attempted (26.3%), so it *manufactures* balance.

## 3. Alphabet coverage, model-free

| corpus | attempted | decomposed | failures |
|---|---|---|---|
| RMechDB radical | 5,295 | **5,293 = 99.96%** | 2 |
| PMechDB polar | 12,424 | **12,377 = 99.62%** | 47 |

17,623 of 17,671 curated steps = **99.73%**, no network. Comparable to ArrowFinder's 99.55% on the same task, without its learned ranker.

## 4. Where the alphabet diverges from chemists

- Bond→bond (three-centre) arrows: radical **42.9%**, polar **30.0%** — no single move exists for them.
- Fish-hooks come only in pairs, so the alphabet emits an even count; **58.7%** of curated radical steps have an odd count. Limitation (iv), quantified.
- Uniqueness **retracted**: allowing one cancelling pair takes mean valid decompositions from 1.00 to **13.546** (radical) and **19.94** (polar).
- Exact-arrow-match figures (39.2% radical, 15.4% polar) are **not quotable** — floors from our minimal search and, for polar, a notation mismatch with OrbChain's orbital grammar.

## 5. Is the constraint discriminating?

- polar: true 99.62%, wrong-but-balanced distractors **55.2%** (gap 44.42 pp)
- radical: true 99.98%, wrong-but-balanced distractors **89.4%** (gap 10.58 pp)

Overall 63.6% of wrong products are accepted. The guarantee is **representability, not plausibility** — and it reinterprets ArrowFinder's 68.86%: mechanisms exist for most wrong products, so their failures are OrbChain's narrowness, not mechanism non-existence.

## 6. The `_radical_moves` bug (issue #1)

`_radical_moves` handled only single-move odd-parity steps. `CollateAFM.trainable` therefore dropped:

| bucket | dropped, original | dropped, fixed |
|---|---|---|
| RS radical | **41.2%** | 0.43% |
| RC radical | **77.7%** | 0.29% |
| PM polar | 0.06% | 0.06% (unchanged) |

Every drop was `_radical_moves -> None`; none were `in_sector` or `_order`. Full corpus: dropped steps fall from ~3,900 to **115** (99.99% kept), recovering ~3,800 training steps. All 14,517 previously-kept targets are byte-identical under the fix.

## 7. Model results — full-corpus checkpoints (Milan's)

| split | model | top-1 | top-10 | validity | electron |
|---|---|---|---|---|---|
| hold_radical | afm | **0.4914** | 0.4959 | 1.0000 | 1.0000 |
| hold_radical | flower_discrete | **0.8263** | 0.9440 | 0.9247 | 0.8417 |
| hold_radical | flower | **0.7492** | 0.8449 | 0.8457 | 0.8365 |
| hold_polar_curated | afm | **0.8782** | 0.9502 | 1.0000 | 1.0000 |
| hold_polar_curated | flower_discrete | **0.8645** | 0.9363 | 0.9448 | 0.9018 |
| hold_polar_curated | flower | **0.7640** | 0.8232 | 0.8619 | 0.8570 |

AFM wins polar on accuracy *and* conservation; collapses on radical. Stratifying radical by whether AFM's own filter kept the step:

| model | kept (2,414) | dropped (2,674) | gap |
|---|---|---|---|
| afm | **0.9925** | **0.0381** | +0.9544 |
| flower_discrete | **0.9350** | **0.7319** | +0.2031 |

`flower_discrete` trained on both halves and loses 20 points — the dropped steps are harder. AFM loses 95, to near zero. Weighted average reproduces the headline: 0.9925x(2414/5088)+0.0381x(2674/5088)=0.4911 vs 0.4914 measured. **AFM is the best model in the study on radical chemistry it trains on.**

## 8. Polar-only retrain — the extrapolation arm

| split | top-1 | top-10 | validity | electron |
|---|---|---|---|---|
| test_uspto (in-dist) | **0.8728** | 0.9858 | 0.9780 | 0.9589 |
| hold_polar_curated | **0.1254** | 0.1899 | 0.9113 | 0.5809 |
| hold_radical | **0.0145** | 0.0157 | 0.9392 | 0.5730 |

`flower_discrete`, radical *and* curated-polar held out of training. It collapses on **both** held-out buckets, polar included (0.8645 -> 0.1254). **The degradation is data provenance, not chemistry** — the control fired. The corpus cannot support a clean radical-extrapolation test, because all its radical chemistry comes from a different source.

The real finding here is conservation under shift: learned electron conservation falls 0.9018 -> **0.5809**, while validity only falls to 0.91. AFM's is exact by construction. That measures what the guarantee is worth when the distribution moves.

## 9. Status

- Running: `fx2-L1..L8` (AFM full corpus, filter fix only, branch `filter-only` b9a12de) behind cache rebuild `fixprep2`.
- Running: `po-flow-*` evals of the second polar-only baseline.
- Pending: `tr-afm` polar-only arm (its chain died on the stale-cache race; not yet restarted).
- Shipped: issue #1 + follow-up comment on mlnpapez/ArrowFlowMatching.
