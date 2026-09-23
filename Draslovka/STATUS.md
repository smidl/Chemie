# Draslovka demo-prep — STATUS

*Snapshot of the partner-demo track. Informal folder (not a coord node yet — enroll when
Draslovka says go). Companion files: [BACKGROUND.md](BACKGROUND.md) (company + axes),
[experiments/](experiments/) (RCI probes + honest results).*

_Last updated: 2026-07-24._

## Goal & audience
Pitch a **joint program** to Draslovka (Czech HCN/cyanide specialty-chemicals leader). Audience =
**managers**. Bar = **competence, not novelty**. Mechanism = **value-for-data**: promise concrete
near-term value in exchange for a slice of their reaction data; escalate to differentiated science
only once trust + data exist.

## Where we are
- ✅ **Background check** — [BACKGROUND.md](BACKGROUND.md). Divisions (specialty / mining / agri),
  chemistry (nitriles, cyanohydrins, aminonitriles, amino acids, hydantoins), and the strategic
  DNA: **GlyCat = "same product, greener/cheaper pathway"** (proven revenue from substitution).
- ✅ **Pipeline probes on 6 of their products** — [experiments/RESULTS.md](experiments/RESULTS.md).
  Isolated: local `experiments/`, RCI `/mnt/data/resynthesis/draslovka/`. Harness left clean.
- ✅ **Prior art pooled + verified** — `li2026_mosaic` (MOSAIC, Nature 2026; 2,498 Voronoi LLM
  experts + confidence) and `sadowski2025_retrotrim` (RetroTrim; MetaScorer ensemble, chemist-
  labeled; **no code released**). Both own the **LLM/ensemble-scorer** ground.
- ✅ **LLM-as-judge proxy** (inline, not yet scripted) — rescues the failing cases; see below.
- ✅ **Two decks now exist, for different moments.** Do not merge them; they answer different questions.
  1. **Intro deck (Beamer/PDF)** — [slides/intro-deck.tex](slides/intro-deck.tex) →
     `intro-deck.pdf`, **3 slides**, 16:9, compiles with a single `pdflatex` run, no external assets.
     *Slide 1* = **primer: what retrosynthesis is**, for an audience that may not know — a target on
     top and three layers of reactions, worked on **5,5-dimethylhydantoin**, one of our six probe
     targets. Chosen deliberately: the spine of the tree read upwards is **Draslovka's own value
     chain** (\ce{HCN} → acetone cyanohydrin → hydantoin), it bottoms out in bulk feedstock
     (methane, ammonia, acetone, urea), and our own audit independently confirmed the cyanohydrin
     step **sound** and the correct industrial route (`experiments/RESULTS.md`). The point is that
     the method reproduces chemistry they already run — sanity before any novelty claim. Closes on
     the bridge line: enumerating trees is easy, knowing which arrows work in a reactor is not.
     *Slide 2* = **the toolbox as a cost ladder** (rewritten 2026-07-29 on owner instruction, replacing
     an earlier "what we work on" slide that was too self-revealing). Five rungs — templates & rules,
     learned reaction models, language models, physics barriers, experiment — ordered by cost per
     answer, each with the one thing it *cannot* do, plus **data** as the foundation under all of them.
     Message: **none of them solves it alone; each is strong exactly where the others are blind**, so
     our objective is to *combine* them — route each question to the cheapest tool that can answer it
     and climb only where the tools **disagree**. Then **active learning** as the research, extending to
     **experimental** active learning (which experiment to run next).
     *Slide 3* = **"Where these methods pay off"** — four recurring needs in industrial process
     chemistry (greener/cheaper route · lab-to-industrial routes · viability in real conditions ·
     feedstock valorisation), each with what the methods offer and an honest maturity tag, plus the
     USPTO/Pistachio domain caveat raised by us first. **De-targeted on owner instruction
     (2026-07-29): no company name, no second person, no HCN/C1 specifics.** Earlier drafts framed it
     as "Where this meets *your* business / mapped onto what Draslovka already does", which reads as
     telling them what their own priorities are. The deck's division of labour is now deliberate —
     **slide 1 is personal** (their molecule, their value chain: that is homework, and it earns
     credibility), **slides 2–3 are impersonal** (general capability and general industrial need).
     Do not re-personalise slide 3.
     **Use when: first meeting, they don't know us.**

     **Two things deliberately kept OUT of slide 2, do not reinstate:** (a) any count of our own
     failures — the earlier draft said "every failure in our 190-target benchmark was the search
     running out of budget" and "three separate attempts of ours failed this year"; (b) any
     calibration / "knows what it doesn't know" claim. Escalation is instead justified by **tools
     disagreeing with each other**, which is an *observable* and needs no confidence signal we do not
     have. That reframing is what lets the slide keep the active-learning story honestly. A comment
     block at the top of the `.tex` records this.
  2. **Diagnosis / phased-pitch deck (HTML)** —
     [slides/pitch-2slide.html](slides/pitch-2slide.html), self-contained and print-friendly, with the
     "why each tool fails → method vs data fix" competence panel. **Use when: we have their attention
     and are asking for data.** Content reflects the reconciliation below, **not** the original design
     plan.
  Both commit to a single light look (projected/printed); status is always a **word**, tinted — colour
  never carries meaning alone (the red/green pair fails colour-blind separation, ΔE 4.1 deuteranope).

## Key findings (evidence, honest)
1. **Route existence is trivial / uninformative.** 5/6 targets are purchasable commodities; forced
   deeper the routes are chemically unsound (EDTA via acetate = wrong). → pitch is *feasibility*,
   not route-finding.
2. **No single off-the-shelf feasibility signal works as a gate** on raw retro output:
   ReactionT5 (noisy), mass-balance (flags everything — retro steps drop byproducts), xTB ΔE
   (undefined until reactions are completed/balanced; thermo ≠ kinetics anyway).
3. **⚠️ Corrected diagnosis — the T5 failures are mostly IN-DISTRIBUTION, not OOD.** Esterification/
   Menshutkin/Biltz are common/textbook. Real causes:
   - **MMA (esterification):** NLL≈0.000 but round-trip FAIL → the model *knows* it; a **metric
     artifact**, not ignorance.
   - **phenytoin (Biltz):** **granularity mismatch** — a multi-step mechanism lumped into one arrow.
   - **chlormequat (Menshutkin):** partial **representation gap** — charged quaternary-salt product.
   → We over-called this "OOD" earlier; corrected.
4. **The LLM judge rescues these because it reasons at the named-reaction level** (Biltz, Fischer,
   Menshutkin) — **reasoning granularity, not more data.** MOSAIC/RetroTrim confirm the ensemble/
   LLM-expert approach works for literature-covered chemistry.

## What fixes what (the honest data ask)
| Gap | Fix | Needs their data? |
|---|---|---|
| Metric artifact (round-trip, no reagents/conditions) | better **scoring protocol** | ❌ we fix (competence) |
| Granularity (multi-step named reactions) | **step-decomposition / LLM-level reasoning** | ❌ we fix |
| **Admissibility — unbalanced / lumped steps (NEW 2026-07-29)** | **normalisation layer** (byproduct + counter-ion completion, elementary-step decomposition) | ❌ we fix — **now a Phase-1 deliverable, see below** |
| Coverage/calibration (charged/organometallic, rare/proprietary transforms, real conditions) | tuning on their reactions | ✅ **their data** |
| True no-precedent frontier (novel chemistry) | **physics-grounded feasibility** (barriers/mechanism) + data | ✅ Phase-2 research |

## Pitch reconciliation, 2026-07-29 (after the tree-wide status + the barrier-oracle results)
The four-step ladder **stands**; three things inside it changed. Slides:
[slides/pitch-2slide.html](slides/pitch-2slide.html).

**1. WEAKENED → then promoted. "Physics-grounded feasibility" had an unbuilt precondition.**
Auditing our own 11 route steps (RDKit atom+charge counts): **10 of 11 were unbalanced as emitted**,
so only **1 was admissible input to a physics oracle** — and after mechanical repair only ~2–4 have a
single transition state. So "run physics validation on your routes" was not demonstrable at any scale.
But it is **plumbing, not science**: 8 of 11 balance-repair by adding the dropped byproduct or
counter-ion. So the honest move is to **move it out of the Phase-2 research promise and into Phase 1
as a concrete engineering deliverable** ("we make your routes physics-checkable"). That is *more*
credible to a manager audience, not less, and it gives Phase 1 a second hard deliverable.

**2. STRENGTHENED. The diagnosis is now cross-validated by an independent modality.**
The Phase-1 product is the diagnosis itself. It previously rested on ML-side evidence only (model
likelihoods + the LLM judge). The physics side has now **independently confirmed the same taxonomy by
refusing the inputs for the same three reasons** — unbalanced (metric/representation), lumped cascade
(granularity), charge-separating (representation). Two unrelated modalities agreeing is much stronger
competence evidence, and it yields the new slide-1 headline: **"the tools are not ignorant of your
chemistry — they are being fed malformed inputs."** That replaces the old metric/granularity/coverage
triad, which was jargon to a manager.

**3. CHANGED. The data ask is now specific, cheaper, and lower-risk for them.**
Was "a slice of their reaction data". Now: **complete equations (full stoichiometry, byproducts,
counter-ions) · the conditions actually run · the failures too.** Public corpora (USPTO/Pistachio)
systematically drop byproducts — *that is exactly why 10 of 11 steps could not be checked* — and a
process plant necessarily records all three. This reframes the ask from "give us your IP" to "give us
the bookkeeping columns public data throws away." Much easier to say yes to.

### New asset for the deck (did not exist when the design plan was agreed)
The **oracle cost ladder**, measured on 225 reference reactions: relaxed NEB **MAE 8.83 kcal/mol,
Spearman 0.902** (~22 min/reaction); fast setting **MAE 9.89, ρ 0.853** (~6.5 min); learned-functional
reaction **energy MAE 4.02, r 0.996** (seconds); and the **negative — a gradient-free barrier shortcut
fails at MAE 47.72** (+102 % bias). Reading: thermodynamics is cheap and solved, **barriers cannot be
shortcut**. Knowing which shortcut fails is itself competence evidence.

### Claims that must now come OUT of the pitch
- **Any uncertainty / calibration claim.** "Knows what it doesn't know" is unsupported — it failed
  three independent ways this month (posterior σ ⊥ error; uncertainty-guided search negative;
  in-context conditioning does not transfer calibrated spread). The old "PFNs stay internal"
  guardrail **hardens to: no calibration or uncertainty language at all.**
- **The selective-computation justification changes.** It was "a calibrated model queries the
  simulator where it is uncertain." That is dead. It is now **cost-ladder triage** — run the expensive
  rung only where the cheap rungs disagree. Same value proposition, honest justification, and easier
  to explain to a manager.
- **The mechanism-kernel-as-better-feasibility claim.** The decisive route-level test (2026-07-28)
  found it does **not** beat a plain structural GP on backup diversity. Scope any mention to *barrier
  ranking* (ρ 0.585), or omit.
- **The L\* search-efficiency claim** (EDTA 21 vs 49 expansions). Not SOTA — MEEA\*-PC beats it by
  8–11 pt. `experiments/README.md` already said "don't oversell"; now say nothing specific. Pitch
  "we select and tune the search for your targets" instead of naming our heuristic.

## Pitch narrative (agreed, manager-ready)
1. **Competence shown** — ran our stack on your products; mapped exactly where today's tools work/
   break *on your chemistry*, and *why* (metric vs granularity vs coverage).
2. **Gaps are specific & fixable.**
3. **Phase 1 (now, low-risk):** stand up the SOTA feasibility layer *inside a working retro pipeline
   configured for your targets* → deliver a **reliability map** + **scored routes for N molecules you
   pick**, in exchange for a data slice. (Value = integration + diagnosis + tuning, *not* "we run
   MOSAIC".)
4. **Phase 2 (data-gated, the prize):** your proprietary/novel chemistry, where your data + our
   **physics-grounded feasibility** build capability no public tool has — yours.

**Guardrails:** competence, not IP, is Phase 1 (be clear-eyed internally). **PFNs stay internal**
(no proof yet) — Phase-2 research bet, never a manager promise. Don't imply their data fixes the
esterification/Biltz cases — *we* fix those; point the data ask at coverage/calibration/conditions +
the novel frontier.

## Open items / next
- **Owner review of the slides** — [slides/pitch-2slide.html](slides/pitch-2slide.html). Two calls to
  confirm: (a) is the "malformed inputs, not ignorance" headline the right opener for managers, or too
  self-critical; (b) the slide quotes "3 of 6 verdicts wrong" and "1 of 11 steps checkable" — both are
  true and both are *our* tools failing. That candour is the competence play, but it is the one
  judgement in the deck that could read as weakness rather than rigour.
- Optional: **script the LLM-judge proxy** (fixed prompt over the 6 steps, logged) → reproducible
  artifact for `experiments/`. Now doubly useful: the same script would give the retrosynthesis leaf
  its semantic-diversity measurement (named reactions vs template counts).
- **A barrier number for the deck.** The specialty set has been handed to the physics-oracle student
  (`retrosyntesis` inbox, 2026-07-29, `data/specialty_barriers_v1.json`). Two of the four computable
  rows are directly quotable here: the MAA-hydration case (favourable ΔE −23.4 yet the gate says FAIL
  → a barrier should explain *why* it is not the industrial route) and the Menshutkin case (the
  single-transition-state false negative). Neither is in the deck yet.
- Hold: **real MOSAIC deployment** (public code, but 2,498 Llama-8B experts / GPU — disproportionate
  for a 6-molecule toy; only if they want the actual system).
- When Draslovka commits: **`/coord init`** this folder as a node.

## Pointers
- Library: `li2026_mosaic`, `sadowski2025_retrotrim`, `ghiron1997_synth-org-exercises` (route book).
- RCI: `/mnt/data/resynthesis/draslovka/` (scripts/out/logs/data); ReactionT5 venv
  `/mnt/data/resynthesis/rxnt5_venv`; xTB `/mnt/data/resynthesis/xtb_dl/xtb-dist`.
