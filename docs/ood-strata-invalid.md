# The 190-hard OOD stratification is invalid — analysis and consequences

**Date:** 2026-08-06 · **Status:** settled · **Scope:** every per-stratum claim in this tree
**Scripts and logs:** `/mnt/data/resynthesis/admissibility/` — `B0_leak.py`, `B1_basek.py`,
`logs/leak-11315356.log`, `logs/basek-11315362.log`

## Summary

The `in-distribution` / `close` / `far` stratification applied to the 190 hard retrosynthesis
targets does not measure what it is used to measure. **100 % of the targets labelled "far"
(deep-OOD) appear verbatim as products in USPTO**, against 78.1 % of those labelled
"in-distribution" — the gradient runs *backwards*. The label is arithmetically correct but
references the wrong corpus: it measures structural distance from **ORD's product index**, while the
planner's knowledge comes from **USPTO reactions**. Consequently the stratum labelled most novel is
the most memorised, and every "generalises / degrades out of distribution" claim built on this axis
is void.

## 1. What the label actually is (verified, not assumed)

`retrosyntesis/src/benchmark/calculate_ood_190.py`:

```
target → Morgan fingerprint (radius 2, 2048 bits)
       → max Tanimoto similarity against "base K"
       → ≥0.80 in-distribution | 0.50–0.80 close | <0.50 far
```

`base K` = `ord_global_index.json` + RxnScribe-extracted ACS patent reactions, described in the
source as "the empirical knowledge of CLOVER". Thresholds were inherited from `calculate_ood.py`
"for consistency with PaRoutes".

Three facts established by direct measurement rather than by reading the code:

- base K contains **1 048 347** canonicalisable product molecules.
- The label is **computed correctly**. Re-deriving max-Tanimoto for `far` targets against 400 k base-K
  fingerprints reproduces values of **0.32–0.49**, all genuinely below the 0.5 threshold.
- Membership is consistent with the label: **94.2 %** of `in-distribution` targets are *literal
  members* of base K, versus **0/25** `close` and **0/28** `far`.

So the stratification is internally sound. The problem is external.

## 2. The measurement that breaks it

Scanning all **1 939 253** rows of `uspto.csv` (atom-mapped) and asking whether each of the 190
targets appears as a **product**, with atom maps stripped and both sides canonicalised:

| stratum | target is a USPTO product | n |
|---|---|---|
| in-distribution | **78.1 %** | 137 |
| close | **96.0 %** | 25 |
| **far (deep-OOD)** | **100.0 %** | 28 |
| all | 83.7 % | 190 |

Every target designated most-novel is a molecule USPTO already makes. The rate is **monotonically
increasing in nominal novelty**, which is the opposite of what the axis is supposed to express.

## 3. Why the gradient inverts

The label and the planner's knowledge are drawn from **different corpora that only partly overlap**:

| | corpus | size | object |
|---|---|---|---|
| the **label** measures distance to | ORD product index (+ACS) | 1.05 M molecules | **products** |
| the **planner** actually learned from | USPTO | 1.94 M reactions | **reactions** |

Everything the planner uses is USPTO-derived — the reaction templates, every expansion policy
evaluated (ReactionT5, Molecular Transformer, Chemformer, LocalRetro, AiZynthFinder), the PaRoutes
route corpus, and the Chen et al. 2020 target list itself. So a target can be genuinely far from ORD
*and* be a memorised USPTO product whose synthesis the templates already encode.

The label therefore answers **"is this product structurally unusual relative to ORD?"** when the
question that matters is **"is the chemistry needed to make this novel relative to what the planner
was trained on?"** Those come apart, and here they come apart *systematically and in the wrong
direction*.

## 4. Two alternative explanations, tested and demoted

Both were plausible and both were checked before the leak test.

**(a) `far` is chemically easier.** Partly true, and it contributes. `far` targets are significantly
less stereochemically demanding — **1.29 stereocentres vs 2.12** for `close` (permutation p=0.036)
and 2.09 for in-distribution (p=0.024) — with **35.7 % wholly achiral versus 20.0 %** elsewhere, plus
lower Fsp3 (p=0.014 vs in-distribution) and higher aromatic-ring fraction (p=0.028). Stereocontrol is
a major driver of synthetic difficulty, so this is a real secondary effect. It is not the main one,
and with eight tests at n=25/28 none survives multiple-comparison correction. SAScore, the most
direct difficulty proxy, trends the same way but is not significant (p=0.34 vs close).

**(b) The inversion is noise.** True for one of the three observations, false for another.
Joris's MEEA benchmark (`far` 28/28 = 100 % vs `close` 22/25 = 88 %) has **overlapping Wilson
intervals** — [87.9, 100] against [70.0, 95.8] — so that inversion is **not statistically supported**;
it is three molecules. The (c) test's inversion **is** supported (`far` 77.8 % vs `close` 48.0 %,
permutation p=0.041). Note that there the outlier is **`close`**, with `far` ≈ in-distribution — a
middle stratum underperforming both ends, which is a binning signature rather than a difficulty
gradient.

## 5. Consequences

**Void — do not repeat, do not publish:**
- `retro-planning`'s "L\* degrades OOD" and "OOD generalisation is the open gap" framing.
- The (c) test's per-stratum backup-diversity comparison.
- Joris's 2026-08-05 conclusion that ReactionT5 is "robust when facing chemical novelty" — its
  100 % on `far` is 100 % memorisation.
- The per-stratum L\* numbers published in the briefing (in-dist 69 % vs 52 %; deep-OOD 79 vs 82).

**Survives — unaffected, because it never used the strata:**
- The reseeded L\* result: **64.43 % vs 61.86 % pooled, 6/6 datasets**, n=18 876 per arm.
- The budget-exhaustion finding that seeded `retro-planning` (all hard-target failures were
  `ERROR_TYPE_5`, independent of this label).
- The oracle ladder and all barrier work.
- Anything else reported pooled.

## 6. How to fix it, in increasing order of trustworthiness

1. **Re-reference the label to USPTO.** Replace base K with the corpus the templates and policies
   were actually trained on. Cheap, and it makes the existing axis mean something. Note the ceiling
   this reveals: with 83.7 % of the benchmark leaked overall, a USPTO-referenced label leaves a
   *far* stratum of at most ~31 targets.
2. **Define novelty over reactions, not products.** Template rarity, or similarity of the *required
   transformations* to the corpus. This is the quantity that should have been measured — product
   structure was never a good proxy for synthetic difficulty, as §4(a) independently shows.
3. **Use a genuinely external corpus.** ORDerly (JCIM 2024) ships **non-USPTO test sets**; that is
   the only construction available to us that USPTO cannot contaminate, and the only one that would
   support an OOD claim at all.

Until one of these lands, **no OOD claim from this tree is admissible.** Per ADR 0004, existing
claims are not grandfathered.

## 7. Reproducing this

```
# leak test: targets as USPTO products, per stratum
sbatch /mnt/data/resynthesis/admissibility/scripts/leak.sbatch      # B0_leak.py
# base-K diagnosis: is the label buggy, or the corpus wrong?
sbatch /mnt/data/resynthesis/admissibility/scripts/basek.sbatch     # B1_basek.py
```
Inputs: `/mnt/data/resynthesis/data/data_student/uspto.csv` (1.94 M rows, atom-mapped),
`ord_global_index.json` (1.05 M keys), and the stratified target list
`retrosyntesis/src/benchmark/data/benchmark_190_hard_targets.csv`.
Outputs: `out/leak_targets.json`, plus the two logs above.

## 8. Limits of this analysis

- "Appears as a USPTO product" is **exact canonical-SMILES membership**, so it is a *lower bound* on
  leakage: near-duplicates, salts, tautomers and stereoisomer variants are not counted.
- It establishes that the targets are known to USPTO. It does **not** directly establish that the
  *routes used* were memorised — that would need the route-step leak test, which could not run
  because the archived route artifacts store `top_routes` for only 133–141 of 190 targets per arm
  and `solution_time` is `inf` elsewhere (a separate known defect).
- The chemistry-difficulty analysis in §4(a) is n=25/28 and does not survive multiple-comparison
  correction; treat it as directional.
- Nothing here bears on whether OOD *generalisation* is a real phenomenon in retrosynthesis. It
  bears only on whether **this benchmark can measure it**. It cannot.
