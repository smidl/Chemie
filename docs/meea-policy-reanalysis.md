# MEEA expansion-policy comparison — corrected reanalysis

**Date:** 2026-08-06 · **Source result:** `retrosyntesis/coordination/outbox.md`, 2026-08-05,
"MEEA Search Algorithm: Expansion Policies Benchmark on 190 Hard Targets" (Joris)
**Data:** `retrosyntesis/meea_backup/results/MEEA_{ReactionT5,AZF,Chemformer,LocalRetro}_retro190.json`
**Script:** `docs/scripts/reanalyse_meea.py` (run from `retrosyntesis/`)

Done without the author, from the per-target arrays he committed. **The headline survives and
strengthens. One supporting claim dies, and one table row is wrong by a factor of four.**

## What was wrong

| | defect | fixable from committed data? |
|---|---|---|
| D1 | LocalRetro is tabulated as a peer of three full-190 arms, but its results file holds **48** targets | partly — its own 48 can be compared honestly; the missing 142 need a rerun |
| D2 | Every non-resolution metric is averaged over **each policy's own successes**, so arms with 47 %–97 % resolution are measured on different and systematically different target subsets | yes, fully |
| D3 | The stratified table uses `OOD_Class`, invalidated 2026-08-06 | yes — drop it |

D1's mechanism is visible in `policy_MEEA_comparison.py`: `df['OOD_Class'] = classes_difficulte`
assigns a 190-row Series onto LocalRetro's 48-row frame, and pandas silently aligns on index and
truncates rather than raising. The chunk files are named `0_48 / 48_96 / 96_144 / 144_190` and only
the first merged, so the 48 are a contiguous prefix — the labels happen to line up, and nothing
anywhere signals that three quarters of the run is absent.

## Coverage

| policy | targets run | solved | rate over its own n | **rate over 190** |
|---|---|---|---|---|
| ReactionT5 | 190 | 185 | 97.37 % | **97.37 %** |
| AZF | 190 | 109 | 57.37 % | **57.37 %** |
| Chemformer | 190 | 90 | 47.37 % | **47.37 %** |
| LocalRetro | **48** | 26 | 54.17 % | **13.68 %** |

The published 54.17 % for LocalRetro is its rate on a quarter of the benchmark.

## Resolution — the headline, and it is now stronger

Paired McNemar over all 190 targets, which the original did not compute:

| comparison | A-only | B-only | p |
|---|---|---|---|
| ReactionT5 vs AZF | 78 | 2 | 4.4 × 10⁻¹³ |
| ReactionT5 vs Chemformer | 95 | 0 | 1.2 × 10⁻¹² |
| AZF vs Chemformer | 47 | 28 | 0.037 |

ReactionT5 solves **every target AZF solves but two**, and **every target Chemformer solves**. This
is not a survivorship artifact — resolution uses the full denominator — and it is the real finding.

## Everything else — paired on the 62 targets all three solve

Own-successes averaging inflated every arm's cost, and unevenly:

| metric | policy | own successes | paired (n=62) | shift |
|---|---|---|---|---|
| search time (s) | ReactionT5 | 63.02 | **40.75** | −22.27 |
| | AZF | 92.70 | **68.36** | −24.34 |
| | Chemformer | 139.65 | **136.50** | −3.15 |
| model calls | ReactionT5 | 15.20 | **11.61** | −3.59 |
| | AZF | 33.37 | **26.50** | −6.87 |
| | Chemformer | 26.02 | **25.58** | −0.44 |

Sign tests on the paired differences:

| metric | comparison | wins | p |
|---|---|---|---|
| **search time** | **ReactionT5 vs AZF** | **29/62** | **0.70 — no difference** |
| model calls | ReactionT5 vs AZF | 35/53 | 0.027 |
| depth | ReactionT5 vs AZF | 34/50 | 0.015 |
| search time | ReactionT5 vs Chemformer | 48/62 | < 0.001 |
| model calls | ReactionT5 vs Chemformer | 43/59 | 0.001 |
| search time | AZF vs Chemformer | 45/62 | < 0.001 |
| model calls | AZF vs Chemformer | 34/59 | 0.30 |

**The claim that ReactionT5 is faster than AZF does not survive.** On targets both solve, the median
difference is **+0.53 s in AZF's favour** and ReactionT5 wins 29 of 62 — a coin flip. The mean of
−27.61 s is a heavy tail: a handful of targets on which AZF is very slow. The original tables report
only means, so the tail read as a typical advantage.

What does survive is that ReactionT5 is **cheaper per solve** — fewer model calls (p = 0.027) and
shallower routes (p = 0.015) against AZF, and better than Chemformer on every axis. Combined with
resolution, the correct statement is *ReactionT5 solves far more targets and uses fewer calls to do
it*, not *and is faster*.

## LocalRetro, scoped honestly to its own 48 targets

Only 8 of 48 are solved by all four arms, so these averages are thin — directional only.

| policy | solved / 48 | search time | model calls | depth |
|---|---|---|---|---|
| ReactionT5 | 46 (95.8 %) | 31.93 | 8.62 | 5.25 |
| LocalRetro | 26 (54.2 %) | 137.43 | 34.75 | 8.62 |
| AZF | 23 (47.9 %) | 106.66 | 45.25 | 9.38 |
| Chemformer | 20 (41.7 %) | 221.80 | 37.75 | 8.38 |

On its own prefix LocalRetro is mid-field, which is roughly what the original said — but it cannot
be placed in a 190-target table, and the 40 % of the prefix it fails is not comparable to the other
arms' failures on the full set.

## What cannot be fixed without compute

LocalRetro's remaining **142 targets**. The prediction directory holds only single-row temp files,
not per-chunk results, so the three unmerged chunks were either never run to completion or their
outputs were not kept. Either the run is repeated or LocalRetro is reported as a 48-target
side-comparison with the restriction stated.

## Bottom line

The conclusion "ReactionT5 is the best expansion policy for MEEA on this benchmark" is **correct and
better supported than the original argued** — McNemar at 10⁻¹³ is a much stronger statement than a
resolution-rate table. Three things must change around it: the speed claim against AZF drops to
model calls and depth, LocalRetro's row is restated as 26/48, and the stratified table goes.
