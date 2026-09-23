# Strategic reconsideration — where the Chemie programme actually stands

**Status: WORKING DOCUMENT, 2026-09-21. Not a decision, not yet a synthesis entry.**
Written at the owner's request for a high-level view: are we missing a bigger pattern?
Companion to `Expert Opinions on Retrosynthesis.pdf` (this folder).

Sources: this tree's own record (`coordination/synthesis.md`, `docs/`, `Milan/`,
`Nemec/report/`, `briefing/`) plus one external landscape sweep run 2026-09-21
(scratchpad, not pooled). **Verification status is marked throughout.** Roughly a third
of the external items are search-sourced and unverified; they are flagged and must not
be cited without a Crossref/arXiv check per the citation protocol.

---

## 0. The question

Three things prompted this. (1) Results are piling up and candidate research questions
keep turning out to be taken. (2) Five external experts, independently, say the problem
is **data**. (3) The owner's own reading: the laws of nature and human best practice are
not well respected in this field, Milan's Arrow Flow Matching (AFM) looks principled and
might propagate, and human planning looks **multiscale** — disconnections, then
reactions, then electron moves — which suggests some multi-fidelity-like unification.

This document answers: is that impression supported by our data, and what is the pattern.

---

## 1. Is "we keep getting scooped" supported? Yes — and *where* matters more than *that*

About ten pre-emptions since June, all recorded in `synthesis.md` or `docs/sota/`:

| what we had | who had it first |
|---|---|
| diverse route selection by penalty | Badowski 2019, *Chem. Sci.* 10:4640 (and we were using half of it from a docstring) |
| arbitrary-subset conditioning on reactions | Zipoli 2024, *MLST* 5(2):025071 |
| disconnection-site conditioning | Thakkar 2023 (IBM RXN) |
| bond constraints inside AiZynthFinder | Westerlund 2025 (AstraZeneca) |
| epistemic selection in search | KeeA\*, NeurIPS 2025 |
| ranking-trained `h` | MEEA\*-PC 2024 (path consistency already ranks) |
| rank calibration | RetroRanker 2023, Retro-Rank-In 2025 |
| LLM/ensemble route scoring | MOSAIC 2026, RetroTrim 2025 |
| balance-constrained decoding | CompleteRXN |
| mechanism enumeration from (reactants, products) | ArrowFinder 2025, *JACS* 147(44):41168 |

**The informative part: every one of these sits inside a single level of description.**
A single-step reaction, a re-ranking, a route-distance metric, a decoding constraint.
Not one crosses levels. That observation is the seed of §3.

---

## 2. Is the experts' "data is the bottleneck" supported? Right about the field, wrong about the axis

The five experts (Bjerrum/AbbVie, Wójcikowski/Merck, Sayle/NextMove, Tetko/Helmholtz,
Varnek/Strasbourg) converge on: public data is exhausted, internal data is noisy and
lacks context/provenance, and meaningful gains need new robotic/HTE data. Varnek adds
that broad DFT inside a retrosynthetic search is computationally implausible — which is
a **separate and, on our evidence, correct** point; see §4.

### 2.1 What our record confirms

- **Negatives barely exist.** Corpora record what worked and was published. An
  unreported reaction is unlabeled, not infeasible.
- **No dataset co-labels conditions × energetics × outcome** on the same reactions
  (`briefing/tutorial/data-landscape.md`). The bridge has to be built, not looked up.
- **Balance is rare.** 2.4 % of sampled USPTO records are atom-balanced (6/250);
  3.45 % of USPTO-Full is balanced *and* mapped as recorded (62,319/1,808,937).
- **Barriers are class-local.** ≈0.8 kcal/mol within data-rich classes (Jorner 2021),
  25–35 kcal/mol at drug-like scope (Gilkes 2025, arXiv 2505.00604).
- Externally, **Tanović 2026** (*Digital Discovery* 5(2):793) shows dataset **size**
  without **template diversity** buys almost nothing, architecture-independent.

### 2.2 What our record contradicts — and this is the strongest single piece of evidence we have

**MU1700, the one target with a chemist's published route and a blind run**
(`Nemec/report/REPORT-MU1700.md` §7, titled "Where the tooling actually failed"):

- **Not a data gap.** All four of his starting materials were in our 313,458-compound
  stock. His route was fully reachable.
- **Not a ranking gap.** Scored by our own seven scorers and inserted into our set, his
  route ranks **#1 on three of seven criteria** (`n_precursors`, `n_precursors_stock`,
  `frac_in_stock`).
- **It is a search-prior gap.** The ring-forming disconnection he used *is* in the
  template library and *is* proposed on request: rank 25 of 100 at prior 0.0027 under
  `uspto+ringbreaker`, rank 3 of 50 at prior 0.0454 under `ringbreaker` alone. Suzuki
  disconnections carry priors one to two orders of magnitude higher. MCTS at 1000
  iterations over branching factor 100 never expands rank 25.

Robotic data changes none of that.

Reinforced twice more:

| result | implication for "more data" |
|---|---|
| completion fills a genuine LHS deficit in **0 of 50,016** records; **0** routes saved | cleaner data *of the same kind* adds nothing |
| ~3,500 curated chemist mechanisms move AFM's multi-move radical classes from **0 % to 85–90 %** (`Milan/afm-human-check.md`) | a tiny amount of data at a *different level* is transformative |

### 2.3 The synthesis

The field **is** data-limited. But the missing data is not more reactions. It is three
things a corpus of published transformations structurally cannot contain:

1. **negatives** — externally supported: Toniato 2025, *Sci. Adv.* 11,
   DOI 10.1126/sciadv.adt5578 (Crossref-verified) reaches SOTA from ~20 positives when
   backed by a negative set ≥40× larger;
2. **mechanism-level decomposition** — the level at which conservation actually holds;
3. **cross-step strategy** — see §3.3.

**And nobody has measured the ceiling.** The external sweep found **no scaling-law study
for reaction corpora at all**. Five experts independently assert a ceiling that has never
been quantified. That is itself a research opening (§5, item 4) and is worth saying back
to them.

---

## 3. The pattern: level-crossing without a lifting operator

This is the candidate "bigger pattern". Almost every failure this tree has recorded is
the same error, and each was recorded separately and never named as one thing:

> **A quantity defined at one level of description is consumed at another, with no
> operator connecting them.**

| # | quantity, and its native level | consumed at | outcome |
|---|---|---|---|
| 1 | barrier / transition state (elementary step) | template arrow (overall transformation) | see caveat below |
| 2 | single-step top-k accuracy (per reaction) | route solvability (per route) | ICC ≈ 0.04–0.05 over routes; a step average *cannot* predict a route outcome |
| 3 | novelty by Morgan similarity (molecule) | planner competence (reaction) | the 190-hard OOD stratification is void |
| 4 | atom balance (arithmetic) | "supplies what a corpus needs" (chemistry) | the 2026-08-26 completion call had to be reversed |
| 5 | step accuracy vs pathway accuracy (FlowER) | compared as a ladder | pathway accuracy is teacher-forced, carries no compounding error |
| 6 | proposal size ratio (per step) | progress toward a strategic goal (per route) | the open problem of 2026-09-06 |

**Caveat on row 1, and it corrects something I said in conversation.** The
`specialty_11` run returned 0 barriers from 11 steps with `NON_MONOTONIC_PATH`, but its
designated **positive control also failed**, so per ADR-0004 §2 that run cannot
distinguish "the inputs are ill-posed" from "the pipeline cannot handle them". The tree
retracted the strong reading on 2026-07-30 and again on 2026-08-26. What still supports
row 1 is the **hand audit**: of 11 planner/template arrows, only ~2 are clean single-TS
elementary steps; phenytoin/Biltz is a whole condensation cascade in one arrow, EDTA-via-
acetate changes charge −4→0, and `CC(=O)O >> CC(=O)[O-]` is a protonation state change,
not a reaction. That argument is independent of the failed run and stands.

### 3.1 This is also the precise sense in which "laws of nature are not respected"

They are not violated. Conservation holds exactly at the **mechanism** level. The corpus
lives one level up, where 2.4 % of records conserve atoms at all. Nobody is doing bad
physics; people are computing physical quantities on objects that are not physical
states.

### 3.2 …and the sense in which human best practice is not respected

Němec's key intermediate `Clc1cnc2c(Br)coc2c1` differs from our consensus
`Brc1cnc2c(Br)coc2c1` by **one atom**. He chose chlorine at step 1 so that the couplings
at steps 5 and 6 would be chemoselective **by construction** (oxidative addition follows
I > Br > OTf ≫ Cl). That is a decision at the atom level, taken for a reason that only
materialises three steps later at the strategy level. Our report's own words: the
software produced a substrate whose viability turns on a selectivity question *it cannot
pose*.

His first email asks for exactly this, unprompted: *"stačí když uvidím jak to rozloží
složité molekuly na jednodušší stavební bloky"* — it is enough if I see how it decomposes
complex molecules into simpler building blocks. That is our shrink-the-target open
problem, stated by a chemist who had not seen it.

### 3.3 Where the crowd is, in these terms

Crowded ground is **within-level** (§1). The ground where this tree found something
un-scooped is **at level boundaries**: the fitted ξ_f marginal, the per-reaction vs
per-route variance decomposition, the size-ratio diagnosis, disconnection information
inside a learned `h`. That is an actionable selection rule.

---

## 4. AFM: what actually transfers, and what does not

### 4.1 The theorem, not the alphabet

AFM's core argument: *a product measure supported on the level set of a non-trivial
linear functional must be a point mass in every coordinate*, so an entrywise model is
compatible with exact conservation only if it is deterministic. **Atom balance in a
reaction is also a linear functional.** The argument therefore applies verbatim to any
token-level reaction generator trained to be balanced — which is exactly the current bet
in `retro-generation` (claim C1: conservation learned implicitly from SynRBL-balanced
data). The principled alternative is to make the *generative event* conserving, rather
than training on balanced data and hoping, or masking the decoder at the end
(CompleteRXN's approach).

This is the strongest transfer and it lands on **arbitrary conditioning** (the
miniproject's item 4 is literally "a hard, exactly checkable linear constraint").

### 4.2 A second transfer, and it is the only live route back into active acquisition

All four of our uncertainty negatives were **posterior quantities**: GP variance,
ensemble spread, MC-dropout, in-context scale. Milan measured something that is not a
posterior: under distribution shift, *learned* electron conservation falls 0.9018 →
0.5809 while validity only falls 0.9448 → 0.9113; AFM's is exact by construction.

> **A constraint-violation rate is a shift detector of a different kind from the four
> that failed.** Untested as such. Cheap to test.

### 4.3 What does not transfer, and it must travel with any pitch

**The guarantee is representability, not plausibility.** Our own measurement: 63.6 % of
*wrong* products are still accepted by the constraint (polar 55.2 %, radical 89.4 %).
Conservation buys a correct output *space*, not a correct output.

Also travelling: the alphabet cannot emit an odd arrow count (fish-hooks come only in
pairs), and 58.7 % of curated radical steps have one.

---

## 5. Multiscale: real, but it is not multi-fidelity

**Multi-fidelity** assumes one quantity computed at different cost and accuracy, so
spending more converges. Our **V arm** (wet-lab → DFT → MLIP → ξ_f) genuinely is that,
and Ayman's Topic B is correctly posed as multi-fidelity active learning.

**The disconnection → reaction → electron-move hierarchy is not.** The levels hold
*different objects*, related by coarse-graining, not by approximation error. A lumped
template arrow does not converge to an elementary step with more compute; it has no
single transition state at all. You need a **decomposition**, not a budget.

So the right structure is two operators, not one ladder:

```
strategy  ──coarse-grain──►  transformation  ──coarse-grain──►  mechanism
          ◄────lift──────                    ◄────lift──────
```

Status of each rung, as of today:

- **Lower lift exists and is principled.** ArrowFinder takes reactants and products and
  enumerates the mechanism between them (99.55 % recovery on PMechDB); our own
  model-free measurement puts the AFM alphabet at **99.73 %** coverage of 17,671 curated
  steps with no network.
- **Upper lift is now occupied — correction to an earlier claim of mine.** Roh, Joung,
  Yu, Tu, Bartholomew, Santiago-Reyes, Fong, Sarpong, Reisman, Coley, *Higher-Level
  Strategies for Computer-Aided Retrosynthesis*, **ACS Cent. Sci. 12(3):345–357 (2026),
  DOI 10.1021/acscentsci.5c02014** (Crossref-verified). Abstracts away substructures of
  intermediates absent from the target, so search commits to skeleton first and defers
  functional-group choice. Coley with two total-synthesis chemists. **Not in our pool.**
  This is the incumbent for any hierarchical-planning angle.
- **What Roh does *not* do**: attach a cost model or acquisition function to the levels.
  **Nobody frames the hierarchy as multi-fidelity or multi-scale optimisation.** That
  half of the owner's intuition survives intact.

---

## 6. Crowded vs open — external sweep, 2026-09-21

### 6.1 Saturated (25+ groups; diminishing returns on the headline metric)

- Single-step transformers / graph models on USPTO-50k. Top-1 plateaued at 55–65 %.
- Template-based classifiers (and undermined by Tanović 2026 on rare templates).
- MCTS / Retro\*-style search variants. Novelty has moved to the objective, not the search.
- **LLM-as-retrosynthesis-agent — crowded and pre-consolidation.** RetroAgent, LARC,
  Retro-R1, Synthelite, Ariadne, RETROSPECT and more within ~18 months, no shared
  benchmark. arXiv abstract counts for `retrosynthesis`: 23 (2023), 22 (2024), 33 (2025),
  30 (2026 to 20 Sep) — flat volume, but the LLM-agent share went from near zero to
  roughly a fifth.

### 6.2 Active but not crowded — mechanism-level modelling (5 groups)

FlowER (Coley/MIT), ArrowFinder-PMechRP (Baldi/Irvine), **DeepMech** (Sunoj/Baranwal,
*Chem. Sci.* 17:15745–15761 (2026), DOI 10.1039/d6sc02809h, Crossref-verified),
**Reactron** (Jung/SNU, arXiv 2503.10197, verified), **MAELLE** (Schwaller/EPFL,
arXiv 2608.27429, 27 Aug 2026, verified).

**MAELLE is the nearest neighbour of our own mechanism work** — discrete flow matching
over electron occupation, a continuous-time Markov chain, optimal-transport
interpolation — and it resolves the conservation constraint the opposite way: it
relaxes the constraint with a virtual electron reservoir, where an alphabet whose
increments cancel makes conservation an identity. Its guarantee is heavy-atom
conservation only; electron and proton conservation are not exact, and it has no
validity guarantee. Assessed in `Milan/maelle-threat-assessment.md`; now pooled as
`nguyen2026_maelle`, with DeepMech and Reactron still to pool.

Also: **FlowER's own OOD evaluation ranges from >90 % to 0 % across 12 reaction types**,
tracking elementary-step similarity to training. That is published corroboration of
Milan's alphabet-coverage framing.

### 6.3 Empty — 0 groups found, from three independent angles

1. **A mechanism-level model as an inner feasibility oracle inside a planner.**
   Planner-side feasibility is still round-trip consistency or a learned classifier,
   never a barrier and never a mechanism.
2. **Any multi-fidelity formulation of route search.** MFBO for chemistry exists and is
   applied to condition optimisation and materials, never to planning.
3. **Reverse-mechanism retrosynthesis.** MAELLE's authors name the missing ingredient
   themselves: atom-level insert/delete edits.

Two independent confirmations that this is the live bottleneck: Ariadne's authors name
route validation explicitly as what remains, and retro-fallback defines the socket for a
calibrated feasibility signal, admits its marginal is hand-set, and **nobody has filled
it**.

4. **Quantifying the public-data ceiling.** No scaling-law study for reaction corpora
   exists (§2.3).
5. **Elementary-step alphabet completeness as a formal object.** One group adjacent
   (Baldi's arrow taxonomy); nobody treats alphabet coverage as a measurable property
   with a closure argument. We have the only model-free measurement of it.
6. **Calibrated route-level uncertainty from step-level models.** The gap is documented
   by one group twice; the variance decomposition is ours and unpublished.

---

## 7. What this implies for the portfolio

**We already hold the piece that fits the empty quadrant, and it is deprioritised.** We
fitted retro-fallback's ξ_f marginal: **p ≈ 0.533 / r^2.152** (AiZynthFinder) and
**0.285 / r^1.825** (ReactionT5) against the assumed **0.75 / r^0.100** — an exponent
18–22× steeper. That socket is defined by a published planner, admitted uncalibrated by
its own author, and unfilled by anyone.

**The candidate organising line**, replacing "active acquisition" as stated:

> A **mechanism-level model supplying the calibrated feasibility** that the planning
> literature has a socket for and no filler.

It unifies, using work already done and measured:

| piece | what it contributes | state |
|---|---|---|
| AFM / mechanism model | the lift operator; conservation as an identity | Milan's, strong, competitor 3 weeks old |
| ξ_f marginal | the only fitted marginal in existence | measured, deprioritised |
| granularity audit | why elementary steps are required | measured (hand audit, §3 caveat) |
| barrier-accuracy requirement | how accurate the oracle must be (structure > magnitude, 8.3 % vs 14.4 %) | measured |
| oracle cost ladder | the cost model multi-fidelity needs | measured |
| evaluation negatives | the methodological spine | strongest asset we have |

And it is **0 groups by three independent counts**.

**What it is not.** It is not "invent strategy abstraction" — Roh 2026 has that. It is
not "a better single-step model". It is not a new uncertainty signal; four have failed.

---

## 8. Open questions for the owner — this is where the discussion starts

1. **Does the level-crossing framing hold up, or is it a post-hoc narrative over six
   unrelated bugs?** The honest test: it should *predict* a failure we have not yet
   measured. Candidate prediction — any metric we currently trust that is defined at one
   level and consumed at another is wrong. Name one and check it.
2. **Is the empty quadrant empty because it is hard or because it is uninteresting?**
   Varnek's objection is the serious version: identifying *which* transformation to
   compute is the hard part, not computing it. A mechanism model is precisely an answer
   to that, but the argument has to be made explicitly.
3. **Does AFM's exactness survive being put in a loop?** Representability is not
   plausibility (63.6 %). What does a planner do with a feasibility signal that is exact
   about conservation and 63.6 % permissive about chemistry?
4. **Resourcing.** Every node's most recent commit is the owner's. This line needs a
   mechanism model (Milan's, not ours), a planner harness (exists), and someone to join
   them. Who?
5. **Do we tell the five experts that nobody has measured the ceiling they assert?**

---

## 9. Provenance and verification

- Internal claims: sourced to files in this tree, named inline.
- External claims marked **Crossref-verified** or **arXiv-verified** were checked against
  raw API responses during the 2026-09-21 sweep: Roh 2026, DeepMech, Reactron, MAELLE,
  Toniato 2025, Ahlbrecht 2026 (Roche, 66k HTE, ACS Cent. Sci. 12(2):222–232).
- **Unverified, search-sourced only — do not cite**: RSGPT, React-OT details, Pfizer/
  Merck/AZ HTE counts, ORD's 2026 record count, LARC, Retro-R1, the URSA-expert OOD
  critique (social-media sourced), multi-objective MCTS timings.
- No PDFs were downloaded; nothing was pooled to `~/agents/library`; nothing was added to
  `paywalled.md`, **except MAELLE**, which was fetched and pooled as
  `nguyen2026_maelle` (PDF, text, digest, arXiv-verified bib). Roh 2026, DeepMech and
  Reactron remain to be pooled.
