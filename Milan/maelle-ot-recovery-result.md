# Does label-free move recovery reproduce the chemist's arrows? — measured

**Date 2026-09-21.** Complements the human-plausibility check
(`afm-human-check.md`): that one asks whether the *trained model* prefers the
chemist's mechanism given the alphabet; this asks whether the competitor's
*label-free shortcut* recovers it at all, with no model anywhere.

Script `analysis/maelle_ot_recovery.py`, results
`analysis/results/maelle_ot_{pmechdb_test,pmechdb_train,rmechdb}.json`.
Paper pooled at `~/agents/library/nguyen2026_maelle.*`.

---

## Why this test

MAELLE (Nguyen, Susanu, Armstrong, Schwaller, arXiv:2608.27429, 28 Aug 2026)
marks the FlowER family — and therefore AFM — with a cross in the
**"Mech. step label-free"** column of its Table 1, footnoted "FlowER … requires a
mechanistic dataset with imputed elementary steps." Its own moves come from a
**balanced integer optimal-transport** problem over electron-pair occupation,
solved between the two endpoints, with no chemist annotation.

That claim is never validated against a chemist. Their own section title calls
the trajectories **"pseudo mechanistic"**, and the only evidence offered is
downstream product accuracy on USPTO-480K.

Nothing of theirs is needed to test it but the rule, which is fully specified in
their section 4.3 and Appendix C. No model, no training, no checkpoint, and no
code (they release none). Reimplemented here and run on curated data they did
not use, where the chemist's arrows are recorded.

---

## Results

### 1. Radical chemistry is outside their state space entirely

Their occupation counts electron **pairs**, so an unpaired electron has no
representation. Their Limitations say so: the method "models electron pairs
rather than individual electrons, which precludes radical reactions involving
unpaired electrons."

| RMechDB, all 5,426 curated radical steps | |
|---|---|
| carry an unpaired electron, **not representable** | **5,355 (98.7 %)** |
| representable, i.e. usable by their method | **0** |
| decomposed by the AFM alphabet, model-free (`RESULTS.md` §3) | **5,293 / 5,295 = 99.96 %** |

### 2. On polar chemistry their objective is *uninformative*, not wrong

PMechDB curated. The full training corpus is the headline; the challenging test
split is the independent replicate.

| | **train (12,799 rows)** | test-challenging (300) |
|---|---|---|
| representable and scored | **12,387** | 291 |
| **optimal transport cost** | **0 in every reaction** | 0 in every reaction |
| chemist's own mechanism is an **optimal** plan | **12,373 / 12,375 = 100 %** | 290 / 290 = 100 % |
| chemist's mechanism **selected** by the solver | **351 / 12,387 = 2.8 %** | 0 / 291 |
| rows where the optimum is **unique** | **233 / 12,375 = 1.9 %** | 0 |
| distinct optimal plans (20 tie-broken re-solves, so capped at 20) | mean **11.9**, median **12** | mean 12.7, median 14 |
| zero-cost off-diagonal site pairs per reaction | — | mean 83, median 44 |
| positive control — our own decomposition, identical rows | **99.88 %** | 100 % |

(12 rows failed the transport solve and 37 carried an unpaired electron even in
the polar corpus; both are reported in the JSON rather than absorbed.)

The mechanism of the result is simple and worth stating in one line. Their cost
is the shortest-path distance between the sites' constituent atoms, so **every
transfer between two sites that share an atom costs nothing** — and that is
exactly the set of moves a chemist ever draws. The chemist's mechanism therefore
always achieves the minimum, and so does every other same-atom shuffle, of which
there are dozens. The objective's argmin is not a mechanism; it is the whole
class of mechanisms that move electrons only within an atom's own sites.

> **The honest statement: their optimal transport does not identify a mechanism.
> It admits the chemist's, cannot distinguish it from at least a dozen others,
> and the one their pipeline trains on is whatever the solver's tie-breaking
> happens to return.** The supervision is a member of a large equivalence class,
> chosen arbitrarily.

This is why "label-free" is not the same as "annotation-free mechanism", and it
is the answer to their Table 1 column. AFM pays for annotations and gets a
mechanism; their rule is free and returns an arbitrary representative.

Compare directly with our own retracted uniqueness claim (`RESULTS.md` §4):
the AFM alphabet's minimal decomposition is **unique (mean 1.00)**, rising to
13.5 (radical) / 19.9 (polar) only when one cancelling pair is allowed. Their
objective starts at ≥12.7 with no relaxation at all.

### 3. Their non-conserving moves are never needed here

`ADD` and `DEL` — the moves that let their state leave the conservation level
set, and the reason electron conservation is *not* an identity for them — fired
in **0** of 12,387 reactions, and 0 of 291 in the test split. On curated
mechanistic data the reservoir is dead
weight; it exists for the unbalanced records of USPTO-480K. Worth saying, because
it shows the relaxation buys nothing on chemistry that is actually balanced.

---

## By-product: a bug in THIS TREE's arrow parser, and the correction is large

Not in Milan's code. `analysis/rmechdb_arrows.py` is the script this tree wrote
to score his alphabet against curated arrows; it does not exist in
`ArrowFlowMatching`.

`parse_arrows` resolves a bare-integer **sink** to a lone pair, applying the
bond-forming reading only when the file writes a trailing comma (`"10=20,"`).
The data does not respect that. After an **atom** source a bare-integer sink is
the **new bond** between the two, comma or not: `"10=20"` is the lone pair on 10
forming sigma(10,20). Only after a **bond** source does a bare integer mean a
lone pair (`"20,21=21"`, heterolysis onto 21). A lone-pair-to-lone-pair transfer
is not an arrow any chemist draws.

Two independent confirmations:
1. **Per row.** For `"7=4"` the recorded occupation change is bond(4,7) +1 and
   lone(7) -1. The lone-to-lone reading gives lone(7) -1, lone(4) +1, which is
   not what the molecules did.
2. **Population.** Under the current reading only **46 of 291** curated
   mechanisms in the PMechDB test split are even feasible as electron transport;
   under the corrected reading, **290 of 291**. A wrong grammar cannot produce
   290/291.

Prevalence: **9,274 / 12,799 (72.5 %)** of PMechDB training rows contain such an
arrow, 252/300 of the challenging test split, and only 122/5,426 (2.2 %) of
RMechDB — radical arrows are fish-hooks and mostly bond-to-atom.

**Clean A/B, single change, same script otherwise:**

| PMechDB curated train, 12,377 decomposed | current | corrected |
|---|---|---|
| **same electron flow as the chemist** | 3,304 (**26.69 %**) | **12,375 (99.98 %)** |
| exact match as drawn | 1,911 | **8,661 (70.0 %)** |
| different flow | 9,073 | **2** |
| decomposition verdicts (coverage) | unchanged | unchanged |

RMechDB moves by one row, 4,254 to 4,255, so **every radical number in
`RESULTS.md` stands**, including the 99.96 % decomposition and the 92.0 %
human-agreement check.

`RESULTS.md` §4 currently says the polar exact-arrow-match figure is "not
quotable … a notation mismatch with OrbChain's orbital grammar". That diagnosis
was wrong in its cause and much too pessimistic in its effect: **the alphabet
reproduces the chemist's electron flow on 99.98 % of decomposable polar steps.**
That is a headline number, not a caveat, and it sits directly against
ArrowFinder's own curated-arrow agreement.

**This needs owner review before it is quoted** (ADR-0004). It is a large
correction in our own favour, which is exactly the direction that warrants a
second pair of eyes. The A/B is one-line, the positive control (decomposition
coverage) is unchanged, and the patched copy is at
`/tmp/fixcheck/rmechdb_arrows_fixed.py` rather than applied in place.

---

## Limits, stated before anyone quotes this

- **This scores a reimplementation of a published rule, not their code.** They
  release none. Every claim here is about the procedure as specified in section
  4.3 and Appendix C, never about their trained model or their reported accuracy.
  Their USPTO-480K numbers are untouched by this and should not be contested.
- One parameter, the virtual-site penalty, is given only as "a large constant".
  It is irrelevant here: `ADD`/`DEL` never fire, so no plan pays it.
- RMechDB/PMechDB map only the reacting atoms, so the occupation is built over
  the mapped subgraph with hydrogens and unmapped heavy neighbours as per-atom
  spectator sites, both checked equal on the two sides per row. That is the same
  reduction `rmechdb_arrows.py` uses and validates row by row.
- The degeneracy count is a **lower bound**: 20 re-solves can reveal at most 20
  distinct optima, and zero rows had a unique one.
- Positive control passed at 100 %, so a failure of our row handling cannot be
  the explanation (ADR-0004 §2).

---

## How to use it in the paper

One paragraph in related work, not a new section. Suggested shape:

> Recovering the moves from the endpoints alone, as concurrent work does by
> optimal transport over electron occupation, does not determine a mechanism. On
> curated polar mechanisms that transport problem attains its minimum for every
> reaction, the chemist's mechanism is always among the minimisers, and so are at
> least a dozen others; no reaction has a unique optimum. Annotation is what buys
> the mechanism rather than an arbitrary member of its equivalence class.

Then the conservation contrast, which is the stronger half and is in their own
footnotes: they guarantee heavy-atom conservation only, concede that protonation
and deprotonation are "simplified", carry `ADD`/`DEL` moves plus a virtual
reservoir so electron count need not be conserved, and state no validity
guarantee. See `maelle-threat-assessment.md` §2.
