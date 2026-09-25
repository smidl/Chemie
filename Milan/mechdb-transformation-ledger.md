# How RMechDB and PMechDB were transformed — the full ledger

**For Milan, 2026-09-21.** Answers three questions: what the pipeline does to the
curated corpora, how many rows survive each stage, and what we know is wrong.

Nothing here is new work; it reconciles numbers that were already in
`RESULTS.md` §3, `analysis/results/*_arrows*.json` and
`experiments/finetune/data/rmechdb_ft/manifest.json`, which until now only ever
showed the *last* stage. The arithmetic does reconcile — the "attempted" column
of `RESULTS.md` §3 is the row count minus the pre-decomposition exclusions.

---

## Stage A — CSV row to bond-electron matrix (`rmechdb_arrows.py::reduced_matrix`)

Both corpora map **only the reacting atoms**. The matrix is therefore built over
the mapped atoms alone, with every unmapped neighbour and implicit hydrogen
folded into a per-atom **context degree**. That reduction is valid exactly when
the context is a spectator, which is **checked per row and rows that fail are
dropped**, not assumed away.

## Stage B — bond-order delta to a move multiset, then to an admissible order

Split the delta into unit changes, assign each to one of the alphabet's moves,
keep assignments whose per-atom diagonal contributions match exactly, then search
for an ordering admissible at every prefix. Per-element capacity is measured from
the corpus endpoints, not hardcoded.

## The ledger

| | RMechDB | PMechDB |
|---|---|---|
| rows in the CSV | **5,426** | **12,799** |
| dropped: unmapped environment not a spectator | 7 | 358 |
| dropped: SMIRKS unparsable | — | 17 |
| dropped: malformed arrow code | 2 | — |
| dropped: no bond-order change at all | 121 | — |
| dropped: more than 10 unit changes, not searched | 1 | — |
| **attempted** | **5,295** | **12,424** |
| decomposed | **5,293 (99.96 %)** | **12,377 (99.62 %)** |
| no decomposition found | 2 | 47 |

Combined: 17,623 of 17,671 attempted steps = **99.73 %**, with no network. The
comparable published figure is ArrowFinder's 99.55 %, which uses a learned ranker.

## Stage C — decomposed step to FlowER training format (RMechDB only)

`experiments/finetune/make_rmechdb_flower_split.py`. The reactant is rewritten in
FlowER's convention (every hydrogen its own mapped atom); the product is **not**
taken from the CSV but **constructed** by applying the chemist's own moves to the
matrix and writing it back with the upstream `product_mapped_smiles_from_be`, so
the pair is exactly the step the chemist drew, in the model's numbering.

| | |
|---|---|
| candidate steps from `targets.json` + `multistep.json` | 4,871 |
| dropped: product round-trip mismatch | **46** |
| removed: exact duplicate (reactant, product) | 463 |
| **kept** | **4,362 steps in 3,950 reactant groups** |
| split 80/10/10 **by reactant group** | 3,485 / 444 / 433 |

Grouping by the canonical map-free reactant means a reactant with several
recorded products never straddles train and test.

---

## Where the data actually goes — the loss is much smaller than it looks

5,426 rows in, 4,362 in the fine-tune corpus, an apparent 19.6 % loss. Most of
that is not loss. **RMechDB's 5,426 rows describe only 4,861 distinct
non-identity transformations**; 565 rows are redundant annotations of chemistry
already present, and 5 are identity steps. Against what actually exists:

| | |
|---|---|
| distinct non-identity transformations in RMechDB | **4,861** |
| held by the fine-tune corpus | **4,362 = 89.7 %** |
| **genuinely missing** | **499** |

**Chemist disagreement accounts for none of it** — disagreement produces
*redundancy*, not loss. The 499 are itemised below, after the rerun.

## RERUN 2026-09-21 — done, and it corrects the diagnosis above

Both dumps regenerated with the current canonical gate, and the deduplication
changed to keep the **longer** drawing (preferring a chemist-matched
decomposition over an arbitrary admissible one). Environment pinned to
**RDKit 2024.3.5**, matching `ArrowFlowMatching/environment.yml`, which
reproduces the stored verdicts exactly — confirming the 47-row drift was the
RDKit version and nothing else. Previous artefacts in `_backup_20260921/`.

**The stale gate was real. `targets.json` goes from 2,057 to 4,301** — it had
been generated on 17 Sep with the old exact-as-drawn gate, three days before the
canonicalisation landed. `multistep.json` was already current at 2,814.

**But it recovers no data, and my "499 recoverable" claim above was wrong.**

| | before | after |
|---|---|---|
| fine-tune steps | 4,362 | **4,362** |
| reactant groups | 3,950 | **3,950** |
| reactions whose content actually changed | — | **21 of 4,362** |
| entries sourced from chemist-matched moves | 1,964 (45 %) | **3,939 (90 %)** |
| pairs where two drawings differ in move count | — | **3** |

**Why nothing moved.** The FlowER training format records `reactant>>product`,
not the move sequence. Two different admissible decompositions of the same pair
write the *same line*. So the provenance flip from 45 % to 90 % chemist-matched
changes which moves *constructed* the product, not what is trained on, and the
"keep the longer drawing" rule is immaterial here by construction. It is kept
because it is the right rule for anything that consumes move sequences.

**A positive result falls out.** The 207 CSV rows where chemists drew the same
transformation with different amounts of electron flow reduce to **3** pairs that
disagree on move count once both drawings are expressed in the four-move
alphabet. The alphabet absorbs 204 of 207 notational disagreements — that is the
canonicalisation working, and it is worth reporting.

**Where the rerun DOES pay: the human experiment.** `targets.json` is the
evaluable set for the chemist-agreement check, and it more than doubles.

| | before | after |
|---|---|---|
| reactions with a chemist-matched move sequence | 2,057 | **4,301** |
| of which **multi-move** | 0 | **2,244** |

The published 92.0 % agreement was measured on the 2,057 single-move rows, which
`afm-human-check.md` already flags as "the one-move sector the released
checkpoint knows". There are now 2,244 multi-move reactions with a canonical
chemist sequence to score against — the sector where the released model scores
0 % and the fine-tune recovers 85–90 %. **That experiment is now runnable and was
not before.**

## The real residue, and one item is a genuine alphabet limitation

Of the 499 transformations the corpus does not hold:

- **121 steps have no bond-order change at all**, and the alphabet cannot express
  them. Every one of its four moves changes exactly one bond order by ±1, so a
  single electron cannot relocate from one atom to another without a bond
  forming or breaking. All 121 are RMechDB's **`ha resonance`** class (119) plus
  2 `resonance`: `[O-:1][N+:2]=O >> [O:1][N:2]=O`, one fish-hook, charges move,
  no bond changes. This is the same parity argument as
  `problem02-termination.md` (N3) in a sharper form, it is **2.2 % of RMechDB**,
  and it does not appear in the paper's limitations list.
- **421 rows have a single-move decomposition that disagrees with the chemist's
  arrows** and reach neither dump: `--dump_targets` requires an arrow match,
  `--dump_multistep` requires ≥2 moves, and nothing accepts "one move, no match".
  That asymmetry is a design choice in the dump flags, not a validity criterion.
  Whether to train on a decomposition the chemist rejects is a scientific call,
  not a bug to fix.
- 74 product round-trip mismatches, still uncharacterised.

## What we know is wrong or uncertain

**2. Absolute arrow numbers drift with the RDKit version.** A fresh environment
(RDKit 2026.03.6) reproduces same-flow at 4,254 where the committed file says
4,301, and exact-as-drawn at 2,058 against 2,057 — a 47-row drift, larger than
the parser fix. The A/B above is unaffected (one interpreter, one line changed),
but **the stored arrow numbers should be regenerated with a recorded RDKit
version**. This tree already applies that rule to its USPTO numbers.

**3. Exact-arrow-match figures are floors, not measurements.** 39.2 % radical and
15.4 % polar come from a minimal search and should not be quoted as agreement
rates. The defensible quantity is *same electron flow after canonicalisation*,
which rewrites a bond-to-bond arrow through the atom the two bonds share.

**4. Uniqueness is retracted.** Allowing one cancelling pair takes the mean number
of valid decompositions from 1.00 to 13.5 (radical) and 19.9 (polar).

**5. Three-centre arrows have no single move.** Bond-to-bond arrows appear in
42.9 % of radical and 30.0 % of polar curated steps; the alphabet spends two moves
through the shared atom, so arrow *counts* differ from the chemist's even when the
flow is identical. This is the phenomenon ArrowFinder's 101/1331 (7.6 %)
"functionally equivalent but representationally different" measures independently.

**6. The 463 "duplicates" are mostly not copies, and dropping them is biased.**
Measured on `all.csv`: 430 groups share a canonical (reactant, product) pair,
562 redundant rows in total.

| | rows | |
|---|---|---|
| same drawing, differs only in atom numbering | **355 (63 %)** | true copies |
| **genuinely different drawing of the same transformation** | **207 (37 %)** | |
| — of which a different arrow count | 192 | |
| — of which one version is a **single** arrow, the other several | **188** | |

The numbering split is annotator variation, not two sources: 1,345 of 5,426 rows
use small indices and 4,081 use the 10/20/21 convention, mixed through every
sub-file. Example, *tert*-butoxy β-scission `CC(C)(C)C[O]`, one pair drawn twice:
`10-10,20;20,21-10,20;20,21-21` (three fish-hooks) and `2,4-2` (one). Same
reactant, same product, different amount of electron flow drawn.

**The consequence, and it runs the wrong way.** `make_rmechdb_flower_split.py`
keeps the first occurrence and iterates `("targets.json", "multistep.json")` —
single-move steps **before** multi-move ones. So every cross-file collision
resolves in favour of the *less detailed* annotation. Measured from the manifest:

| source | input | kept | dropped |
|---|---|---|---|
| `targets.json` (single-move) | 2,057 | 1,964 | **93** |
| `multistep.json` (≥2 moves) | 2,814 | 2,398 | **416** |

That biases the fine-tune corpus toward one-move annotations of multi-move
chemistry — **the exact failure mode `problem02-termination.md` diagnoses and the
fine-tune is meant to repair.** The CSV estimate puts the affected count near 188,
about 4 % of the corpus, so it is unlikely to overturn the 0 % → 85–90 % result.
But the direction is wrong and the fix is one line: prefer the longer annotation
on collision, or reverse the file order, and re-run. Worth doing before the
fine-tune table is published.

**7. What the 46 round-trip mismatches are has not been characterised.** They are
dropped, not diagnosed. At 1 % of the fine-tune corpus that is tolerable, but if
anyone asks what they are, we do not currently know.
