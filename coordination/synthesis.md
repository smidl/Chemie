# Cross-cutting synthesis — Chemie

Running picture of what the children collectively know. Derived from children's
outboxes; never restates a child's primary framing.

> **Structure note (2026-06-15):** the Synthesis orchestrator layer was dissolved
> (coord flatten to pilot-flat). Children are now **`retro-pfn`** (retrosynthesis
> feasibility / ξ_f) and **`MolGPT`**, directly under Chemie. Mentions of
> "Synthesis" below mean the retrosynthesis-feasibility project (`retro-pfn`); the
> student (`retrosyntesis`) and paper (`proposal`) are now Chemie-declared
> external/boundary.

## PFN overlap (Synthesis ⋈ MolGPT)  — opened 2026-06-06
Both children use Prior-data Fitted Networks (PFN):
- `Synthesis/` — PFN as the calibrated **reaction-feasibility validator** (ξ_f)
  inside route planning (see retro-pfn/xif/PLAN.md).
- `MolGPT/` — a general molecule model evolving **from GPT toward PFN**.

They do not yet share code or experiments. Cross-cutting findings on PFN
behaviour shared by both belong here; a binding shared decision → an ADR.

## In-context learning — shared substrate (seeded 2026-06-12)
In-context learning (ICL) is the methodological substrate both children sit on:
**MolGPT** explores GPT→PFN / in-context approaches for molecules (any task);
**Synthesis** applies the same PFN/ICL idea to **reactions** as one specific
application (ξ_f feasibility). A joint, seminal ICL literature base now lives in
the pool `~/agents/library/` — pulled from MolGPT's side (origin + reading map:
`MolGPT/phd-proposal-notes.md`), spanning five strands:
- general ICL (emergence, role of demonstrations, the canonical survey);
- ICL mechanism/theory (induction heads; transformers as gradient-descent /
  implicit-Bayes / statisticians);
- PFNs / amortized Bayes / neural processes / meta-learning (TabPFN(+v2),
  PFNs4BO, (attentive) neural processes, Matching Networks, MAML);
- ICL/few-shot for molecules (FS-Mol, MHNfs, PAR, Fifty 2024, one-shot drug
  discovery, MoleculeNet);
- ICL for reactions (BO-ICL, ChemLLMBench, MetaRF, LIFT-for-chemistry).

**Bidirectional flow (explicit policy).** General ICL/PFN methods surfaced for
MolGPT are candidates to apply to **reactions** in Synthesis (the specific
application); conversely, any ICL/PFN finding earned by **training on reactions**
(`retro-pfn`) propagates **back** here as evidence for MolGPT's general line.
Neither child owns this substrate — the pool holds the artifacts, this file
holds the shared picture. (E.g. retro-pfn's mechanism-kernel / correlation
findings are exactly the kind of reaction-trained result that should inform
MolGPT's in-context modelling, and vice-versa.)

**Concrete dual (2026-06-12).** MolGPT's `MolPFN` is the *generation-side* PFN
(in-context conditional molecule generation; reaches "PFN" later by adding
predictive uncertainty). retro-pfn's `xif/PLAN.md` model-class-3
("PFN-as-correlated-ξ_f") is the *prediction-side* PFN. Same
in-context-vs-amortized-Bayesian object approached from two ends — the canonical
seam for bidirectional transfer.

**Convergence direction (2026-06-13, low-urgency — converge slowly on purpose).**
*Refines an earlier framing.* Connecting MolGPT to Synthesis via ξ_f's
**model-class-3** is the weak route: class-3 ("in-context joint predictive of a
feasibility field") is, stripped down, predict-a-label-in-context — the **crowded
prediction-side ICL/PFN prior art** — and routing MolGPT through it discards MolGPT's
one differentiator: **the output is a structured chemical object, not a scalar.**

Better direction (owner steer): point MolGPT's *generative* strength at **reactions as
the output** — a **trained, in-context (support-set-conditioned) reaction
generator/predictor**. This lands MolGPT on a *different organ* of K-P-V than ξ_f:
- **MolGPT → Knowledge/Planning:** propose reactions / disconnections (structured output).
- **retro-pfn (ξ_f) → Validation:** score feasibility (scalar/field).
i.e. a **generate-and-validate pipeline** that complements rather than duplicates, with
the K-P-V planner as the meeting point (ξ_f filters the generator's proposals; the
generator supplies ξ_f realistic negatives).

Defensible niche (narrow but real): in-context conditioning × **structured reaction
output** × *trained* model. Prior art to confront — both already in the pool — is
**frozen-LLM** in-context-for-reactions: `guo2023_chemllmbench`, `ramos2023_bo-icl`;
plus non-in-context reaction transformers (Molecular Transformer / Schwaller 2019 —
**not yet pooled**, Chemformer, T5Chem) as baselines.

Still a *direction, not a task*: MolPFN is mid-debugging on molecule generation,
retro-pfn is GP-stage on ξ_f.
> **CORRECTED 2026-07-28.** (i) The reaction-generator direction **left this tree's MolGPT**
> on 2026-07-24 — it is now `retro-generation`'s (rektomar) charter; MolGPT keeps the molecule
> track. (ii) "MolPFN mid-debugging" is superseded: MolPFN completed a 6-run S0–S3 factorial on
> 2026-07-24 with a quantitative result (location transfers, **scale does not**). See
> §DEEP STATUS 2026-07-28 §1. Reaction→molecule feedback already live: retro-pfn's
**mechanism-kernel** finding (structure rugged, mechanism smooth over feasibility)
tells the generator which *similarity* its context selection should use.

Prior-art base for this direction now pooled (2026-06-13): forward
(`schwaller2019_molecular-transformer`, `schwaller2018_found-in-translation`,
`schwaller2021_rxnfp`), retrosynthesis (`liu2017_seq2seq-retrosynthesis`,
`tetko2020_augmented-transformer-retrosynthesis`, `irwin2022_chemformer`;
`lu2022_t5chem` queued paywalled), foundation (`chilingaryan2022_bartsmiles`).
**Closest precedents the niche must be argued against — the in-context angle is
NOT greenfield:** `liu2023_fusionretro` (in-context learning *for retrosynthesis*)
and `seidl2022_mhnreact` (few-shot single-step retro). FusionRetro is to the
reaction-generator direction what Bio-xLSTM is to the molecule side: the prior
work that owns the broad "in-context for reactions" framing, so the contribution
must be the specific, differentiated slice — not the idea itself.

**Reverse-map — these are ALREADY in use on the Synthesis side (2026-06-13), so the
convergence is concrete, not hypothetical:** `schwaller2021_rxnfp` is *used as code*
(a reaction-transformer embedding featurizer in retro-pfn's ξ_f representation +
correlation experiments, `xif/xif/featurizers.py`) — the same reaction
representation a MolGPT reaction-generator would use, and one already characterized
by the structure-vs-mechanism-vs-rxnfp kernel comparison. `liu2023_fusionretro` is
*used as a benchmark/inventory* in the vendored retro-fallback ICLR24 experiments.
`schwaller2019_molecular-transformer` is *cited as prior art* (proposal bib +
retro-pfn survey). So RXNFP is the most concrete shared touchpoint. (Citation slip
to fix on the student side: retro-pfn `docs/prior_art_survey.md` attributes
"Molecular Transformer" to Liu 2017 — that's Schwaller 2019; Liu 2017 is seq2seq
retrosynthesis.)

## Retrosynthesis: research↔student cross-track (migrated from the dissolved Synthesis layer, 2026-06-15)
Cross-cutting coordination between the **PFN research track** (`retro-pfn`) and the
**external student validation track** (`retrosyntesis`). Live detail/log:
`retro-pfn/coordination/outbox.md`.

**Work tracks & dependency**
- Student: baseline validation (done) → route generation → feasibility-validator integration.
- Research (`retro-pfn`): feasibility-model training (barriers + ξ_f) · validation · baseline methods.
```
route generation (student) ──baseline routes──▶ feasibility-model validation (retro-pfn)
feasibility-model training ──ξ_f predictor──────▶ feasibility-model validation
feasibility-model validation ───────────────────▶ feasibility-validator integration (student)
```
**Research→student handoff — four opportunities (origin 2026-06-05; now SUPERSEDED by the de-risk cycle).**
From student baseline validation (Retro-Fallback on PaRoutes, 212 targets: 35% coverage,
95% precision, Medium 43–58% vs Deep OOD 0%, budget-exhaustion bottleneck), research
proposed four opportunities. The (A) similarity vs (B) path/context-correlation distinction
was settled — the gas-phase-QM path-dependence audit is ill-posed → dropped (retro-pfn
ADR 0001 + xif/PLAN §4). **Current status (retro-pfn log → 2026-06-14):** headline metric
reframed (SSP confounded → calibration + correlation-specific test); decisive **hard-target
backup-preservation (c) test handed to the student track**; a recalibrated mechanism-kernel
ξ_f marginal is banked. The original 2026-06-19 handoff decision is folded into the active
de-risk line.
Refs: tripp2024_retrofallback, joung2025_electronflowmatching, Reaction-QM (Zenodo 10493799).

## Subproject alignment vs the active-acquisition program (onboarding audit, 2026-06-15)
Audit after ADR 0003; verdicts + re-pointing delivered to each leaf's inbox (deliver-not-execute).
- **retro-pfn / `xif` (T1 surrogate): PARTIAL** — builds the calibrated correlated ξ_f+σ
  (recalibration banked) but PLAN.md is *passive*: σ not used to select queries, no
  acquisition/VOI step, no Suzuki/AIMNet anchor, headline still "fusion." Re-point: σ as the
  acquisition signal; add the Suzuki/AIMNet VOI (active-vs-passive) step; name the oracle.
- **retro-pfn / `conditions` (T2 oracle): PARTIAL, mis-pointed + parked** — holds the
  AIMNet-Suzuki + Robin DFT-NEB bridge but framed as a surrogate-side condition head and parked
  on the SNAr negative (which closed only the condition-head sub-question); bridge scoped as bulk
  pre-compute. Re-point (needs ratification): re-charter as on-demand `oracle(rxn,cond)→(barrier,σ)`;
  un-park around the oracle role; adopt the Suzuki/AIMNet VOI probe; TS-automation = first task.
- **MolGPT (T3 proposer): DIVERGENT (substance) / PARTIAL (infra)** — _**VOIDED 2026-07-28**: this
  verdict and its re-point no longer apply to MolGPT. The reaction line was handed to
  `retro-generation` on 2026-07-24; MolGPT owns the **molecule** track and, graded on that scope, is
  aligned and evidence-producing. The T3 slot is held by `retro-generation`, whose first obligation
  is prior art — so the slot is vacant-and-earlier-stage, not filled. Original text kept below for
  provenance._ — in-context *molecule*
  generation now; role needs in-context *reaction* generation, balanced, σ-frontier-coupled. Infra
  reusable; reaction I/O + balance + σ-conditioning absent; its 3 advisory docs assert the
  superseded molecule-gen framing. Re-point: reaction tokenizer + dataset/balance (prereq) →
  disconnection-exemplar context + σ-token → loop coupling; recast the redundancy ablation for
  reactions. Expansion-phase, not blocking.
- Parked charters (`flow-ts`, `path-correlation`): peripheral to the loop; leave parked.

**Common thread:** the surrogate *substrate* is built; what's missing program-wide is the loop's
**connective tissue** — the acquisition primitive (σ→query selection), the oracle-on-demand
interface, and a reaction proposer — not the components themselves.

## Search guidance vs feasibility — the two-knob split (new node `retro-planning`, 2026-06-18)
The student 190-hard deliverable forced a reframe (Chemie status, 2026-06-18). The
KPV result `final_kpv_results_190_hard_RetroFallback.csv`: planner returns ≥1 route on
**190/190** targets, only **65/190 (34 %)** validate (in-dist 39 % / close 20 % / far 25 %),
and **every** rejection is `ERROR_TYPE_5_INCOMPLETE` — budget-exhausted / dead-end,
**1664/1664, zero feasibility-driven**. The binding constraint on hard/OOD targets is
**search guidance, not feasibility**: retro-fallback's Retro\*/MCTS are steered by a static
hand-crafted **SAScore** cost-to-go heuristic; the program improved the **edge costs** (ξ_f)
but never touched the **heuristic `h`**.

So the AND-OR planner has **two knobs**, now split across two leaves:
- **`retro-pfn` owns ξ_f — edge costs** (which reactions are feasible).
- **`retro-planning` owns `h` — cost-to-go** (which node to expand): learned, rank-trained,
  uncertainty-aware. Seeded as a Chemie leaf (ADR there: `retro-planning/coordination/adr/0001`).

They compose (`h × edge-costs`) on the same syntheseus harness, shared 190-hard benchmark,
metric = **budget-to-solve per stratum** (not SSP). First obligation in the new node is a SOTA
lit pass (`retro-planning/literature/LIT_BRIEF.md`) before any build.

**Three convergences this surfaces (program-level):**
1. **"Rank, not estimate" recurs on both sides.** retro-pfn's mechanism ξ_f is a strong
   *ranker* (ρ 0.585) that needed σ-scaling to *calibrate*; Chrestien et al (NeurIPS 2023)
   train `h` to *rank*, not regress cost-to-goal. Same principle, edge-cost and cost-to-go.
2. **σ-as-exploration reframes the σ⊥error result.** retro-pfn's GP-σ ⊥ prediction-error
   killed σ as a *feasibility-acquisition* signal; σ as a *search exploration bonus* (UCB,
   à la Jin–Yang–Wang LSVI-UCB) needs σ to track unexploredness, not error — possibly live here.
3. **PFN/DecisionBO fit:** an in-context tree-conditioned heuristic = the amortised PFN shape;
   "train `h` for solve-rate, not cost-accuracy" = DecisionBO's "train for the decision."
   > **UPDATED 2026-07-28.** The DecisionBO half is **corroborated** three ways and promoted to a
   > program invariant (§DEEP STATUS §2). The *in-context/PFN-shape* half is **weakened**: MolPFN
   > showed an in-context model does not learn calibrated scale from its context (§DEEP STATUS §1),
   > so "amortised PFN shape" cannot be assumed to deliver a usable σ. Convergence 1
   > ("rank, not estimate") also needs qualifying — MEEA's path-consistency term already ranks, so
   > rank **competes rather than stacks** with the strong baseline (§DEEP STATUS §3).

_(Superseded by the deep-status synthesis below — the shared results have landed.)_

## DEEP STATUS 2026-07-28 — the σ pillar is failing everywhere; the data/objective pillar is winning
Full recursive pull (3 enrolled leaves + 3 external students + 2 boundaries + tier-0 board).
This section **updates the program-level picture** recorded 2026-06-23 and above; where it
conflicts with an earlier paragraph in this file, this one is current.

### 1. Derived finding — THREE independent σ negatives, one mechanism
The program's organizing thesis (06-14) is "calibrated surrogate queries the expensive oracle
only where **uncertain** + where it **matters**." Every leaf that has now *tested* the
uncertainty half has returned a negative, by a different route:
- **retro-pfn** (06-17/18): GP/deep-ensemble σ ⊥ |error| (ρ 0.04–0.18, 2 models × 2 reps × 2
  datasets); σ-acquisition ≈ random / worse. The one signal that beat random is the
  **classifier's predictive/aleatoric entropy** (F1 0.83/0.82 vs random 0.77) — and
  **epistemic specifically stayed ≈ random** (0.76).
- **retro-planning** (06-21/22, re-confirmed): epistemic-MCTS (σ-into-leaf-value bonus) clean
  NEGATIVE, parked. Externally, **KeeA\* (NeurIPS'25) now occupies epistemic *selection***, so
  the novelty of "uncertainty-aware `h`" has eroded as well.
- **MolGPT/MolPFN** (07-24, NEW — never surfaced by the leaf): an in-context generator learns
  **location** from its support set but **not scale**. Generated std is flat (~0.31) while
  context std spans 0.087→0.330; the gen/ctx ratio crosses 1.0, the signature of a **fixed
  output floor** set by *conditioning difficulty* (0.066→0.31 across S0→S3), not by the context.
  Holds even in the two configs built to require width tracking.

**The convergence (new, program-level).** These are not three unrelated setbacks. Location/rank
information transfers; **calibrated scale does not** — whether the vehicle is a GP posterior, an
MCTS leaf bonus, or an in-context support set. MolPFN's floor is the *generative* face of the
same object retro-pfn measured as σ⊥error. This directly threatens (a) the σ-token half of the
reaction-proposer differentiator now held by `retro-generation`, and (b) this file's
retro-planning "convergence 3" (in-context tree-conditioned `h` = amortised PFN shape).

**Sharper worry nobody has confronted.** The *only* acquisition signal that works is largely
**aleatoric** entropy — irreducible noise. "Query where the label is noisy" is not the thesis;
the thesis needs *reducible* (epistemic) uncertainty. The empirically-supported version of our
own program is therefore **narrower and differently motivated** than what we publish. See
§Actions A1.

**Prior-art squeeze on the same claim** (`retro-generation`, 07-27): Molecular Transformer's
plain likelihood-derived confidence classifies its own correctness at **ROC-AUC 0.89** — a
non-Bayesian, 2019, 4-layer baseline. Any "calibrated in-context σ" claim must beat that.

### 2. Derived finding — what IS working: data regime + training objective, not cleverness
The positive results across three nodes share a shape:
- **retro-planning verdict flip (07-03/04)**: L\* went from losing to **winning** against the
  Retro\* value net purely by **training-breadth/distribution match** — 149 easy trees →
  8,628 PaRoutes-n1 trees (99.2 ± 0.3% vs 97.5 ± 0.7% on Chen-190, ~26% fewer expansions;
  64.3 vs 61.8 pooled on 6 drug-like sets, winning all 6, with a pure-`h` control). The earlier
  "L\* degrades OOD" was **coverage** (the rank loss only constrains pairs that co-occurred on
  OPEN), not representation and not scale.
- **MEEA\*-PC (07-05)**: pooled **72.7%** vs L\* 64.3 vs vanilla 61.8 (~2× efficiency) — credited
  to **data scale × additive-set architecture × path-consistency**, not to search (search is
  near-saturated: MEEA is *below* SeeA\* on easy in-dist USPTO, 95.5 vs 97.5).
- **retro-pfn's 06-18 reversal** came from running Zhong's *actual* pipeline, not a better idea.
- **retro-generation (07-27)**: two exact reproductions in 3 days (ReactionT5 92.60 vs 92.8;
  Molecular Transformer 90.40 vs 90.4) — rigour, not novelty, produced the useful findings.

**Program re-weight this justifies:** shift emphasis from *"find the right uncertainty signal"*
toward *"the right training objective in the right data regime."* This is the empirical content
of the 44-day-old tier-0 message from `PFN4BOrevisited` (decision-focused learning: likelihood
quality ⟂ decision quality) — which is now **strongly corroborated from three directions** and
should be closed as an *upgraded* invariant, not merely acknowledged.

### 3. Derived finding — the differentiator has moved (retro-planning)
"Rank/tree-trained `h`" beats the *weak/vanilla* baseline robustly, but is **not
SOTA-competitive**: MEEA\*-PC beats it by 8–11 pt. Worse for the thesis, MEEA's
path-consistency term **already ranks** — vertically (parent↔child along edges) where L\* ranks
horizontally (on-path vs off-path siblings on the OPEN cut) — so rank **competes rather than
stacks**. The live question is now "does rank/σ help a **strong** architecture" (leaf's H1/H2),
untested. PC is dense/absolute/propagating where rank is sparse and relative: that is the
leaf's own explanation of the coverage gap, and the most transferable methodological idea the
tree has produced this month.

### 4. Cross-cutting: the "route validation is a metric artifact" thread
Three nodes independently hit the same wall — our *validation* signals are measurement
artifacts before they are chemistry:
- **Draslovka** (07-24, unenrolled partner track): T5 round-trip failures are **in-distribution**,
  not OOD — MMA has NLL≈0.000 but round-trip FAIL (**metric artifact**); phenytoin is a
  **granularity mismatch** (multi-step named reaction lumped into one arrow); mass balance flags
  everything (retro steps drop byproducts). The LLM judge rescues these by reasoning at the
  **named-reaction level** — "reasoning granularity, not more data."
- **retrosyntesis** (06-25): replaced the hard pass/fail round-trip with continuous
  probabilities + AUROC, and fixed a ranking bug (was ranking only a route's *last* reaction).
- **retro-physics-validation**'s brief already names the same two traps (lumped multi-step
  transformations have no single TS; most entries unbalanced/ionic).
This is a real cross-cutting finding and belongs in the program's framing: **granularity and
balance are prerequisites for any feasibility oracle**, ξ_f included.

### 5. Oracle ladder — first honest numbers (retrosyntesis, 07-24, 225 Transition1x rxns)
Relaxed NEB (PySCF wB97x/6-31G(d)), 8 img/50 cyc: **MAE 8.83 kcal/mol, Spearman 0.902**, 1294
s/row. 4 img/25 cyc: MAE 9.89, ρ 0.853, 393 s/row (the practical rung). **Skala Ea via a
gradient-free LST shortcut FAILS** — MAE 47.72 (17.81 bias-corrected), +102% bias — although
Skala **ΔE** is excellent (MAE 4.02, r 0.996). Reading: thermodynamics is cheap and solved;
**barriers are not shortcut-able**, which is exactly the T2-oracle cost that makes acquisition
worth doing — the thesis's *premise* is confirmed even as its *signal* is in doubt. AIMNet2
barriers are still absent, so the 3-rung apples-to-apples barrier table does not exist.

### 6. Charter corrections (this file was wrong)
- **MolGPT is no longer T3.** The 06-15 audit verdict "MolGPT (T3 proposer): DIVERGENT" and its
  re-point (reaction tokenizer → σ-token → loop coupling) **left the node on 2026-07-24**: the
  reaction line was handed to `retro-generation` (rektomar). MolGPT keeps the **molecule** track
  (GPT→PFN) and, graded on that scope, is aligned and — for the first time — evidence-producing.
  **Consequence the program must absorb: the T3 proposer slot is now VACANT-and-earlier-stage,**
  held by a node whose first obligation is prior-art review. The "missing connective tissue"
  gap is *further* from closing than the 06-15 audit implies, not closer.
- **retro-planning's two-track split (07-05)** exported the abstract-algorithmic half — including
  the **paper** — to a root-level sister node `~/AIC/Planning`, outside Chemie.
  _**Corrected 2026-07-28:** `~/AIC/Planning` **is** in the tier-0 registry (added by the 07-05
  `/coord index` rebuild) — the leaf's "not yet in the coord registry" line is stale, and my
  first reading of it was wrong. What was genuinely missing is the **relationship declaration at
  this orchestrator**, now written into `AGENTS.md` §Peer trees: Planning is a **peer**, not a
  child; Chemie does not manage it or pull it as a child; methods flow down to `retro-planning`,
  190-hard phenomenology flows up; cross-tree traffic via the `~/agents` board._
- **The 06-23 "keep H1 and H2 both live" posture is not retro-pfn's stance.** The leaf's own docs
  treat barrier-GP σ as *falsified for acquisition* and keep the GP only as a marginal/ranking
  head. The live dichotomy inside the leaf is **aleatoric vs epistemic entropy**, not GP-σ vs
  entropy. Our recorded posture is one revision behind the leaf's.

### 7. Execution reality (the uncomfortable half)
- **retro-pfn: dormant since 2026-06-18** (5.5 weeks; one doc-housekeeping commit). The decisive
  route-metric T-VOI head-to-head **never ran** — the spec exists (`xif/harness/ROUTE_BUILD_SPEC.md`),
  no code followed. The "where it **matters**" (route-relevance) half of the thesis — the leaf's
  actual differentiator — has **never been probed once**. `conditions/` (T2 oracle) unstarted;
  AGENTS.md still calls it ACTIVE.
- **retro-planning: idle 23 days**, and the two-track split + MEEA decomposition + H1 correction
  + the two-axes tutorial are **uncommitted**, i.e. invisible to a submodule pull. Its outbox is
  3 weeks and two headline results behind its own findings.
- **MolGPT: outbox silent since 06-18** — the split and the first real results were never
  reported; the results live only in an **unregistered** sibling repo (`result_coordination`,
  rektomar's results-delivery channel).
- **retrosyntesis: drifted — but the drift is asymmetric between its two students** (see §11).
  Self-directed into the oracle rung (good work, §5) while **three standing asks are unfulfilled
  across two nudges**: the decisive hard-target (c) test (uncap `max_routes`, all 3 arms,
  per-stratum diversity — last touched 07-16, censored single-arm), syntheseus pluggable
  `value_fn` on 190-hard, and `.gitmodules`.
  _**Corrected again 2026-07-28, from RCI (`sacct -u moczyjor`) — the "(c) test is stalled since
  07-16" reading is WRONG and must not be repeated.** Joris has been running it near-continuously;
  it is invisible only because everything lives in `/home/moczyjor` (mode **700**) and is never
  reported. **A task is running right now** (array `11262590_92`, `rfb-missing`, n05, submitted
  2026-07-28 10:41). What actually blocked him is an **engineering wall, not inattention**:
  the uncapped run accumulates memory **without bound** — five successive `rfb-benchmark-full`
  deaths, all `OUT_OF_MEMORY`, at 32G (2d05h) → 128G (12h) → 256G (1d01h) → 128G (6h) → 128G
  (7h36), with **MaxRSS ≈ ReqMem every time** (33.4/32G, 133.9/128G, 267.9/256G). Removing
  `max_routes=30` removed the thing that was bounding memory; more RAM will never fix it.
  He then **re-architected correctly** to per-target SLURM arrays at 32G/task
  (`rfb-benchmark-array` ×51, `rfb-dynamic-array` ×10) and is now gap-filling residual targets
  **per arm** — `rfb-missing-independent` ×50, `rfb-missing` ×30, `rfb-missing-mech` ×15, i.e.
  **the three-arm structure the (c) test requires exists**. Waves are shrinking and most tasks
  finish in 1–30 min, so this is an endgame, not a stall. Two real risks remain: one target
  OOM'd even at 32G per-task (`11253595_59`), and between two consecutive waves today the missing-index
  set shifted by exactly −1 across all nine entries (31→30, 59→58, 70→69, 76→75, 88→87, 93→92,
  114→113, 119→118, 121→120) — either a legitimate 1-based→0-based fix or a shifted target list
  that will never converge; **ask, don't assume**. Nothing from this campaign is on the shared
  store: `/mnt/data/resynthesis/retro-fallback-harness` still holds only the June-13 three-arm
  smoke run (`stepc_{indep,mech,struct}`)._
  _Corrected 2026-07-28: `.gitmodules` and the FlowER evaluation **were** delivered — on
  `feature/FlowER_Model_Implementation` (07-27), not on `main`. So the failure is **merge and
  report discipline**, not the work. The FlowER result is a clean decisive negative that satisfies
  the 07-16 evidence gate and justifies parking FlowER: **T5 top-1 27.96% (59/211) vs FlowER
  exact-match 10.24% (504/4923)** — "FlowER does not outperform T5 on exact matches." It has never
  been written to the outbox._
- **retro-physics-validation: zero student commits in 4 days**; Phases 0–3 were scoped offline so
  RCI-pending is not a legitimate blocker, and nothing is flagged. Blinding intact.
- **retro-generation: the velocity outlier** — and it is the only node with a question waiting on
  us (below).

### 8. Metric discipline slipped (both planning arenas)
Program metric is **budget-to-solve per stratum**, never pooled. Current retro-planning headlines
are solve-rate at fixed budget, **pooled** over 6 datasets, with the Medium-in-dist / Deep-OOD
strata dropped; decisive runs moved to third-party harnesses (SeeA\*/KeeA\*/MEEA\*) with no λ and a
500-call budget, **off syntheseus**. The "compose `h` × ξ_f on syntheseus" deliverable therefore
has no live vehicle, and the composition itself (ξ_f × L\*) is **NULL on payoff** (70% vs 69%
depth-anchored vs 75% value-net) and data-blocked. Also: `hard50b` was a **ceiling artifact** of a
file-ordered benchmark — a caution for any future val/test split here.

### 9. Numbers to correct wherever we cite them
- **Molecular Transformer USPTO_MIT top-1 is 90.4, not 88.8** (+1.6 pp). 88.8 is the paper's
  *unaugmented Baseline* row whose weights were never released; the field, including ReactionT5's
  comparison table, quotes it and understates the standard baseline.
- **`sagawa2023_reactiont5` (preprint) ≠ `sagawa2025_reactiont5-jcheminf`**: 0.0 vs 92.8 top-1
  un-fine-tuned. The released checkpoint matches the **journal** version. Our pool cites the preprint.
- USPTO_MIT top-1 is **RDKit-version-dependent** (41/40,000 flip between RDKit 2024.03 and
  2026.03 on identical predictions) — nobody in the field reports this; we should.
- retro-planning internal inconsistency to reconcile before external use: 6-dataset L\* quoted as
  both 65.7/63.2 and 64.3/61.8; MEEA as both 73.6 and 72.7.

### 10. Actions this status generates (deliver-not-execute; not yet dispatched)
- **A1 — retro-pfn (highest value).** The thesis needs the *route-relevance* ("where it matters")
  probe far more than another uncertainty-signal comparison: it is the untested half and the only
  un-scooped one. Run it on the classifier-entropy arm; drop the GP-σ vs entropy head-to-head as
  the framing question and replace it with **aleatoric vs epistemic** — and answer explicitly
  whether an aleatoric-driven loop is still the thesis we want to publish.
- **A2 — retro-planning.** Commit the working tree (four artifacts are invisible to a pull);
  write the verdict flip + MEEA\*-PC into the outbox; file an ADR for the `~/AIC/Planning` split
  and decide registry enrollment; restore per-stratum budget-to-solve reporting.
- **A3 — MolGPT.** Surface the variance-floor negative to this node with the σ read-across spelled
  out; register `result_coordination`; append a superseding outbox entry. **Protocol breach to
  repair:** we wrote `MolPFN/coordination/README.md` into an external student repo (marker says
  "never write into it"), and it contains the now-**superseded** reaction roadmap — a student
  reading MolPFN today gets the wrong direction.
- **A4 — retrosyntesis.** Escalate `.gitmodules` from nudge to hard prerequisite; re-issue the (c)
  test as the one deliverable, uncensored; ask for the 3-rung barrier table on *shared* TS
  geometries (AIMNet2 rung missing).
- **A5 — retro-generation.** Answer the open DECISION: **yes** to reproducing MT's
  uncertainty ROC-AUC 0.89 before FusionRetro — cheap, artefacts downloaded, and it pressure-tests
  the σ niche *before* any modelling commitment, which §1 makes urgent.
- **A6 — retro-physics-validation.** Check-in; confirm or deny RCI. **Judgment call flagged, not
  taken:** routing retrosyntesis' NEB-vs-Skala table (§5) to him would partly pre-answer the
  tool-suitability question he is supposed to characterise independently — it does not break the
  *route* blinding, but it does contaminate Phase 1. Owner should decide.
- **A7 — tier-0.** Close the 44-day-old `PFN4BOrevisited` message, recording the §2 upgrade
  (three-way corroboration), and record it in this node's `inbox.md` (it bypassed the inbox).
- **A8 — briefing (flow: out) is 23 days stale and wrong in three places** — it still publishes the
  down-weighted H1 σ-driven loop as current, still headlines L\* as "the win" (superseded by
  MEEA\*-PC), and still attributes **reaction** generation to MolGPT. Needs a correcting pass
  before the next publish, not a mechanical push.
- **A9 — registry.** `Draslovka/` (active partner track, deliberately unenrolled), `_lib-inbox/`,
  `datasets.tar.gz` are unlisted; add to the "not enrolled (transparent)" list and re-run
  `/coord index` (marker count drifted 25→27).

### 10b. THE (c) TEST LANDED, 2026-07-28 15:32 — and the MECHANISM KERNEL LOSES at route level
**This contradicts the program's banked headline and this file's own §Feasibility record. Flagging
rather than absorbing.** Joris completed the uncapped 3-arm hard-target run (`max_routes` 30 →
**10000**, `limit_rxn_model_calls` 500, **189/190** targets shared across all three arms — one lost
to an OOM that corrupted its JSON). Artifacts on the shared store at
`/mnt/data/resynthesis/data/data_student/retrofallback-feasibility_models/{independent,gp,mechanism-gp}_strate_spec_500_10000__/`,
report `report_fm_comparison.txt`, reported in the leaf outbox (`513adb7`).

At feasibility threshold ≥0.1 (n: close 25 / far 27 / in-dist 137):

| stratum | arm | is_solved | top_feas | avg_n_rxn | n_viable | mech_diversity |
|---|---|---|---|---|---|---|
| close | independent | 0.480 | 0.157 | 2.55 | 115.7 | 26.9 |
| close | **structural GP** | **0.520** | **0.210** | 3.68 | 1466.0 | **58.8** |
| close | mechanism-GP | 0.480 | 0.183 | 3.75 | 1424.7 | 36.8 |
| far | independent | 0.704 | 0.229 | 3.92 | 210.0 | 41.5 |
| far | **structural GP** | **0.778** | **0.315** | 5.45 | 2355.6 | **88.0** |
| far | mechanism-GP | **0.778** | 0.298 | 5.51 | 1859.6 | 59.6 |
| in-dist | independent | 0.737 | 0.235 | 3.99 | 180.0 | 32.9 |
| in-dist | structural GP | 0.745 | 0.292 | 5.56 | 3514.1 | **69.9** |
| in-dist | **mechanism-GP** | **0.781** | 0.281 | 6.00 | 2947.2 | 57.7 |

**The student's conclusion** (his words): mechanism-GP does **not** preserve higher backup diversity
than structural; on `far` it is worse (59.6 vs 88.0 templates), finds fewer viable routes and forces
longer routes; "the mechanistic covariance appears too rigid, heavily penalizing otherwise valid
branches", leaving the **structural/latent GP as the most balanced method at scale**.

**Orchestrator reading — the direction is real, the stated strength is not yet supported:**
1. **On solve rate the mechanism kernel is NOT worse** — it is *best* in-dist (0.781 vs 0.745/0.737),
   tied on far, and one target behind on close (12 vs 13 of 25, i.e. noise). The negative is
   specifically about **diversity / n_viable**.
2. **Those two metrics are threshold-confounded, in the same family as the SSP confound we already
   caught.** The comparison uses a **fixed absolute** cut of 0.1 while the arms' score distributions
   differ systematically (struct `top_feas` is higher than mech in *every* stratum: 0.210/0.315/0.292
   vs 0.183/0.298/0.281). A fixed cut therefore admits more of struct's routes by construction. At
   threshold 0.3 the counts collapse (n_viable struct 4.4–6.8) and the ordering scrambles
   (mech in-dist 81.0 vs struct 6.8), which is what a calibration artifact looks like. **A
   calibration-matched or per-arm-quantile comparison is required before this is a verdict.**
3. **The 07-03 10-target positive did not survive scale-up — and the cap was the reason.** Capped at
   30 routes the n_viable ordering was indep 21.0 > mech 15.0 > struct 12.1 with mech best on
   diversity (12.9 vs 7.7); uncapped it **inverts** to struct 1466–3514 >> mech 1425–2947 >> indep
   116–210. The censoring Joris himself identified was suppressing exactly the arms that generate the
   most routes. Clean methodological finding: **that earlier "positive" was a small-n + censored
   artifact, and we recorded it as a result.**
4. **The program's declared metric is still not delivered:** `solution_time` is `inf` for **every arm
   in every stratum**, so budget-to-solve per stratum cannot be read from this run at all.
5. **Separate and possibly bigger finding, unremarked by the student: ξ_f is drastically
   under-confident.** Sweeping the threshold, solve rates go 48–78% (≥0.1) → 28–70% (≥0.3) → 0–12%
   (≥0.5) → **0.000 everywhere at ≥0.7 and ≥0.9**. **No route produced by any arm reaches feasibility
   0.7.** Either the calibration is badly off at the top of the range or nothing being proposed is
   actually feasible; both readings matter more to the program than the arm ranking does.

**What this does to the program picture.** The mechanism kernel's *barrier-ranking* result (ρ 0.585 vs
0.417 structural) is untouched — it remains a good ranker. What is **not** supported is the leap from
"better barrier ranker" to "better route-level backup preservation", which is how this file and the
published briefing have been presenting it. That makes this the **fourth** instance of today's
program-level pattern (§1–2): a component-level improvement that fails to survive the
decision-level metric. It is the reaction/route-side confirmation of the decision-focused-learning
invariant, arriving from an independent direction. Consequence for the briefing: the ✓ on the
mechanism kernel must be qualified as a *ranking* result, not a route-level one.

### 11. Student attribution inside `retrosyntesis` — the node has TWO owners on one seam
`retrosyntesis` is co-owned (`owners: [moczyjor, mollerob]`), both ENSICAEN engineering students, and
they never overlap on files. Attributing node-level status to "the student" has been hiding this. The
reliable attribution key is the commit author on `coordination/outbox.md` — **entries are unsigned**,
which is itself worth fixing.
- **Joris Moczygeba** (`Smox656` / `JorisM16` / `moczyjor`, 76 commits) owns the **K-P-V benchmark /
  planning / learned-validation** half: `src/benchmark/`, `retro_fallback_iclr24/`, `t5_performances/`,
  the learned validators, `extraction_book_synthesis/`, `syntheseus`. He is the only student in the
  tree with a **formal written phase ladder** (`doc/studentDocs/student_plan{,2}.md` + Phase 2
  `retro-phase2-task.md`, French): Phase 0 "make the K-P-V loop run end-to-end" → Phase 1 "know
  exactly where and why it fails" (stratified failure table, five decoupled metrics) → Phase 2
  "implement and compare 5 validation approaches", pass bar FP 56%→≤42%, FN ≤15%, cost ≤5×.
  He reported Phase 2 honestly as a **miss** (ensemble FP 61.4% vs the ≤42% bar, FN 7.0%).
- **Robin Molle** (`molle` / `Robin Molle` / `mollerob`, 38 commits) owns the **physics-oracle** half:
  `src/oracle_benchmark/` (16 files), `validation_dft_neb.py` / `validation_kinetics.py` /
  `validation_skala.py`, `src/route_benchmark/` (leaf resolution + stratification), `rci_setup/`.
  **He has no plan document of his own** — his only authored plan artifact is a French *translation*
  of Joris's Phase-2 task. His charter exists solely as supervisor prose in the leaf's `inbox.md`
  (06-24 "you own the oracle, your barriers are the labels"; 07-16 "make it a three-rung
  oracle-*selection* benchmark — the objective is a decision, not a plot").
- **Governance consequence:** Robin is now the de-facto owner of the program's **T2 oracle** — cited
  as a named upstream dependency in `retro-pfn/conditions/README.md` ("Robin's DFT-NEB = the PRIMARY
  general source") and in the active-acquisition thesis — while having no plan doc, no thesis
  statement, and no written objective. That is an unmanaged critical path.
- **The one instruction that requires them to cooperate is the one neither has done:** gate Robin's
  expensive NEB behind Joris's cheap T5 round-trip filter (asked 06-13, 06-24, 07-16). Without it
  the on-demand-oracle architecture that makes 190-target scale tractable does not exist — and that
  gating *is* the "oracle-on-demand interface" this file has been calling missing connective tissue
  since 06-15. It is a **student-integration** gap, not a research gap.
- Neither student has ever used the `BLOCKED:` / `DECISION NEEDED:` prefix the outbox protocol
  invites; both instead report soft blockers inside prose (Joris: 10 days lost waiting on a PR that
  was never a prerequisite; Robin: the AIMNet2 Python-3.11 pin, open since 06-29 with three offered
  workarounds untaken).
