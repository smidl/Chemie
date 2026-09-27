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

**QUANTIFIED 2026-07-28 — and promoted from observation to candidate program bottleneck.** Audited all
11 Draslovka steps in `/mnt/data/resynthesis/draslovka/out/dE_lstar.json` by hand (RDKit atom+charge
counts, verified). As emitted, **10/11 are unbalanced → `dE_kcal: null`**, i.e. xTB refused them and
NEB would refuse identically. But the unbalancedness is **bookkeeping, not chemistry**:
- **8/11 are balanced or one byproduct/counter-ion away**: cyanohydrin needs HCN instead of the
  emitted **cyanide anion** (then balanced *exactly*, no byproduct); MMA/methyl-ester need `+H2O`;
  amide↔ester need `+MeOH`/`+NH3`; hydantoin needs `+EtOH+H2O`; chlormequat needs `+[Br-]`.
- **3/11 are not**: phenytoin/Biltz (a whole condensation cascade in one arrow, with **ethanol — a
  solvent — listed as a reactant**); EDTA-via-4×-acetate (charge −4→0, and *chemically wrong* anyway,
  so refusal is a **correct** verdict); and `CC(=O)O >> CC(=O)[O-]`, which is a protonation-state
  change rather than a reaction and should be filtered upstream.

**The deeper point — the mismatch is ONTOLOGICAL, not domain or cost.** Balance is the easy gate; the
hard one is whether an arrow is a **single elementary step with one transition state**. Several of the
8 balanced steps still are not: only **chlormequat (Menshutkin, textbook concerted SN2)** and
**acetone+HCN** (rate-determining C–C formation) have clean single TSs; the hydration and Fischer
esterification are computable as *uncatalysed* concerted TSs and informative precisely because the
barrier should be high; the acyl substitutions and the hydantoin cyclocondensation are genuinely
multi-step. **Honest yield: ~2–4 meaningful barriers out of 11.** We are asking a transition-state
method to score **retro-template arrows**, which are overall-transformation bookkeeping objects, while
barriers are defined on **elementary steps**. ξ_f inherits the same mismatch — it is trained on
barrier data (Reaction-QM / Transition1x, elementary-ish) and deployed on template arrows.

**MEASURED 2026-07-29 — the answer is ZERO, and my estimate above was wrong.** The physics student ran
the set (`/mnt/data/resynthesis/outputs/specialty_11/results.json`, 4 865 s of DFT). Of 11 steps:
**0 barriers obtained.** 7 correctly excluded on input; 1 (`chlormequat`, Menshutkin) correctly
**skipped** because the pipeline has no implicit-solvation path and he declined to publish an
untrustworthy gas-phase number; and the 3 I predicted would be "computable as uncatalysed concerted
TSs" — cyanohydrin, MAA hydration, MMA esterification — all returned
**`failed_no_ts_found` / `NON_MONOTONIC_PATH`** after 25–30 min each. A non-monotonic NEB path means
there is **no single maximum**, i.e. these arrows are *not* elementary steps either, even once
balanced. So my "~2–4 meaningful barriers out of 11" was optimistic by 2–4.

> **⚠ RETRACTED IN PART, same day — the positive control failed, so this run cannot support the
> attribution I gave it.** `spec01_cyanohydrin` was designated the **positive control** in the task
> spec (audit-confirmed sound, the real industrial route). It failed too. **A run whose positive
> control fails cannot distinguish "the inputs are ill-posed" from "the pipeline cannot handle this
> class of input"** — and I recorded it as the former. Reading the criterion
> (`validation_dft_neb.py:302`): `NON_MONOTONIC_PATH` fires when the highest-energy image is **not
> above both endpoints** (margin 1e-4 Ha). That is "no interior maximum found", which is *consistent
> with* multi-step but equally consistent with a collapsed or unconverged band, or with bad endpoint
> geometries. Note all three failures are **bimolecular** (acetone+\ce{HCN}, MAA+\ce{H2O},
> MAA+MeOH) and their geometries were generated from SMILES, whereas the pipeline was validated on
> **Transition1x, which supplies consistent reactant/TS/product geometries in one frame**. For a
> bimolecular reaction built from two separate SMILES, the interpolation typically has to pass
> through association first, and the band slides into the pre-reaction complex well — a classic
> setup failure, not a chemical verdict. **Most likely explanation is therefore geometry/protocol for
> bimolecular reactions, not granularity.** To separate them: rerun one known-elementary bimolecular
> reaction *from Transition1x* through the same SMILES→geometry path. If that fails too, the finding
> is about the pipeline; only if it passes does the granularity reading stand.

**Revised, and this is the harder claim:** balance repair is *necessary but nowhere near sufficient*.
The binding gate is **elementary-step granularity**, and on real planner output it currently rejects
**everything**. Retro templates emit *overall transformations*; a transition state exists only for an
*elementary* step; nothing in our stack bridges the two. Note the failures are **diagnoses, not
crashes** — the NEB ran to completion and reported "this is not one step", which is the physics side
independently confirming the granularity finding on three further cases. Also note the honest cost:
**81 minutes of DFT to learn that the inputs were ill-posed** — precisely the waste a cheap
admissibility check in front of the oracle would prevent.

**Program consequence.** Byproduct-dropping is a property of template retrosynthesis *in general*, not
of cyanide chemistry, so this admissibility rate is roughly what any physics rung sees on **any**
planner output, pharma included. So the binding constraint on the validation programme may be neither
oracle **accuracy** nor oracle **cost** — both of which Robin has now characterised well (§5) — but
**how much planner output is admissible input at all**. Nobody has that number. It also reframes the
learned-gate noise: T5 happily scores unbalanced, lumped arrows because it does not care about
well-formedness, which is *why* it is noisy — so **the learned gate's false negatives and the physics
gate's refusals share one root cause: representation, not chemical knowledge.** A
normalisation/balancing layer between planner and oracle (SynRBL-class) is therefore an
**engineering** prerequisite sitting in front of a research programme — cheap relative to what it
unblocks, and currently owned by nobody.

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
5. **Threshold sweep: no route from any arm reaches feasibility ≥0.7.** Solve rates go 48–78% (≥0.1)
   → 28–70% (≥0.3) → 0–12% (≥0.5) → **0.000 everywhere at ≥0.7 and ≥0.9**.
   > **⚠ Self-correction, same day.** I first recorded this as "ξ_f is drastically under-confident,"
   > arguably bigger than the arm ranking. **That reading is probably wrong and must be excluded
   > before it is repeated.** Route feasibility in retro-fallback **compounds over steps** (a product
   > of per-reaction feasibilities in the independent case), and mean route length here is
   > **3.7–6.0 steps**. Reaching a *route* score of 0.7 over 6 steps needs ≈0.94 per step; over 4
   > steps ≈0.91. So a 0.7 route-level ceiling may be **arithmetically expected from compounding, not
   > a calibration defect at all** — consistent with retro-pfn's banked *marginal* calibration
   > (σ-scaling κ=1.71, coverage 0.949). The sweep supports compounding: as the threshold rises the
   > surviving routes get sharply shorter (in-dist mech `avg_n_rxn` 6.00 → 2.30 → 0.14 at
   > ≥0.1/0.3/0.5). Cheap decisive check: regress route score on route length.
   >
   > **This introduces a SECOND confound into the arm table above.** If route score compounds, a
   > fixed absolute threshold **systematically penalizes whichever arm finds longer routes** — and
   > the arms differ markedly in length (independent 2.5–4.0 vs structural 3.7–5.6 vs mechanism
   > 3.7–6.0). So the fixed-0.1 comparison is confounded by **both** per-arm score distribution
   > **and** route length. Note this cuts *for* the structural arm's win, since it leads on diversity
   > *despite* producing longer routes than independent — but the magnitudes are not interpretable
   > as they stand.

6. **NEW, and it threatens every per-stratum claim in the tree: the OOD strata are not ordered by
   difficulty.** Across **all three arms** `far` (deep-OOD) solves *better* than `close`
   (0.704/0.778/0.778 vs 0.480/0.520/0.480). The same inversion appeared in the June KPV run
   (in-dist 39% / close 20% / far 25%), so it **reproduces across runs and harnesses**. If
   `calculate_ood_190.py` is not ordering by difficulty, then per-stratum reporting — ours,
   retro-planning's in-dist/medium/deep-OOD splits, and any OOD-generalization claim built on this
   benchmark — inherits the defect. Independent audit of the stratification is now a prerequisite,
   not a nicety.

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

### PROBE 2026-07-30 — the 0/11 result IS THE TOOL. Verdict: my task spec violated the input contract.
Evidence, all from the code on `origin/main` plus job metadata (the run itself is uninspectable —
workdir `/home/mollerob/retrosyntesis`, home mode **700**, and **the specialty runner was never
committed**; the repo contains only my inbox note and the data file):
1. **The contract is geometry-in, not SMILES-in.** `run_dft_neb_barrier(reactant_xyz, product_xyz, …)`
   is documented as running "a real NEB between two **already atom-mapped/aligned** xyz geometries",
   and `estimate_barrier_neb` advertises a "**geometry (no SMILES)** … geometry-in contract".
   **I supplied SMILES.**
2. **Nothing in the repo bridges that gap.** No SMILES→3D→aligned-atom-mapped-xyz path exists in
   `src/`; the only `MolFromSmiles` uses are fingerprint/similarity code. So an ad-hoc conversion had
   to be improvised for this run, outside the validated path and outside version control.
3. **The atom guard is weaker than it looks.** `validation_dft_neb.py:198` compares **element
   sequences** (`react_geom.atoms != prod_geom.atoms`), not a genuine atom correspondence. A wrong
   mapping that happens to be element-consistent **passes silently**, and IDPP then interpolates
   between mismatched atoms. `ATOM_MISMATCH` did *not* fire, so the sequences matched — which tells us
   nothing about whether the correspondence was right.
4. **The failure mode is exactly what a bimolecular reactant frame produces.** For acetone+\ce{HCN},
   MAA+\ce{H2O}, MAA+MeOH the reactant side is **two separate molecules** that must sit in one frame as
   a sensible pre-reaction complex. IDPP from "two molecules placed apart" to "one bonded product"
   gives a profile dominated by **association, which is downhill** — so the highest image lands at or
   near an endpoint, which is *precisely* the `NON_MONOTONIC_PATH` trigger (HEI not above both
   endpoints, margin 1e-4 Ha).
5. **Same code, opposite outcome, discriminated by input provenance.** 450/450 success and MAE
   8.83 kcal/mol on **Transition1x, where the dataset supplies consistent atom-mapped
   reactant/TS/product geometries**; 0/3 on SMILES-derived geometries. **3 of 3 attempted cases were
   bimolecular and all 3 failed identically.**

**Conclusion: the run measured our conversion step, not the chemistry.** It says nothing about
elementary-step granularity, and the granularity claim reverts to *unsupported by this evidence*
(it still has independent support from the Draslovka/Biltz lumping case, which is a different
argument). **Robin executed correctly** — schema, controlled vocabulary, and he declined the
untrustworthy solvated number. The defect is in my task specification: **I asked a geometry-in
instrument a SMILES-shaped question, and the layer that would bridge them is the very normalisation
layer we have identified as missing.** The experiment presupposed the component under investigation.

### MECHANISM FOUND AND FIXED 2026-07-30 — unrelaxed endpoint geometries. Reproduced on RCI.
Run under this session (not delegated): `/mnt/data/resynthesis/admissibility/` — scripts, logs and
JSON results. GFN2-xTB stands in for DFT (seconds, not half an hour); the algorithm mirrors
`validation_dft_neb.py` exactly (idpp interpolate → relax band, 6 moving images / 50 LBFGS cycles →
`hei < max(e_react,e_prod) − 1e-4`). Ground truth = Transition1x's own wB97x barriers.

**Two wrong hypotheses eliminated first** (both mine): with mapping/placement varied and endpoints
left as supplied, **neither** reproduced the failure. Pushing bimolecular fragments 8 Å apart merely
**inflates** the barrier (96.6→138.7, 149→204 kcal/mol unrelaxed); an **element-sorted, silently
wrong mapping** inflates it 3–10× (289 / 612 / 577 vs 96 / 149 / 162) or **crashes the calculator**.
Consequential, but they do not produce `NON_MONOTONIC_PATH`.

**The variable that does it: are the endpoints at a minimum of the NEB's own level of theory?**
`e_react`/`e_prod` are **single points at the supplied geometries — never optimised**. Transition1x
supplies wB97x-optimised endpoints, so a relaxing band cannot fall below them. A SMILES-derived
geometry is a **force-field embedding**, so its single-point energy sits far too high, the interior
images relax *below* it, and the path is rejected as "non-monotonic" while the chemistry is fine.
Holding mapping and placement fixed and varying **only** this (n=4: 2 bimolecular, 2 unimolecular):

| reaction | frags | ref. barrier | A: supplied (DFT min) | D: MMFF endpoints | E: **fix** — endpoints re-optimised at the NEB's level |
|---|---|---|---|---|---|
| C3H3N3O/rxn7723 | 2 | 77.5 | **OK**, HEI +26.1 | **NON_MONOTONIC**, HEI **−106.9** | **OK**, +15.5 |
| C3H3N3O/rxn7724 | 2 | 88.8 | **OK**, +31.1 | **NON_MONOTONIC**, **−38.0** | **OK**, +60.9 |
| C2H2N2O/rxn2091 | 1 | 88.7 | OK, +12.6 (barrier 82.8) | OK, +7.7 (87.7) | OK, +16.9 (82.0) |
| C2H2N2O/rxn2092 | 1 | 127.4 | **NON_MONOTONIC**, −12.4 | (FF setup failed) | — |

**Confirmed:** the flip is caused by endpoint relaxation state, the effect is enormous (up to
**107 kcal/mol** below the endpoint maximum — not a marginal artefact), and it bites **bimolecular
cases (2/2) but not unimolecular (0/1)** — matching Robin's 3-of-3 bimolecular failures exactly.
For a two-fragment system a force field has no useful information about the intermolecular
arrangement, so the endpoint lands very far off the electronic-structure surface.

**THE FIX (one step): optimise both endpoints at the NEB's own level of theory before interpolating.**
Arm E demonstrates it recovers a valid barrier on both cases that failed.

**Second, independent finding — the criterion itself is unsafe.** On `rxn2092` the **control arm
failed** with perfect supplied geometries: 1 false positive in 4. `NON_MONOTONIC_PATH` therefore
conflates *bad input* with *unconverged band* (my bands sat at max|force| ≈ 0.06 vs a 0.0025
threshold after 50 cycles). It needs a **convergence check attached** before it is read as a
statement about the input, and it should be reported as `INDETERMINATE`, not as a rejection.

**Honest caveats of this probe:** xTB not DFT (the mechanism is level-agnostic — it is about
endpoint/level *mismatch* — but the magnitudes are not his); n=4; MMFF-relaxing a Transition1x
geometry stands in for "an RDKit embedding" rather than being literally his conversion path.

### CONFIRMED AT DFT 2026-07-30 — root cause is a COLLAPSED MULTI-FRAGMENT EMBEDDING
Repeated the D/E arms at ab-initio level on **`spec01_cyanohydrin`** — the specialty set's own
designated positive control — with hand-written, fully H-explicit **atom-mapped** SMILES (13 atoms,
formula check C4H7NO, all 13 map numbers bijective). Arm D reproduced **`NON_MONOTONIC_PATH`**, and
the recorded endpoint energies gave it away:

- `e_react` = **−209.75 Ha**, `e_prod` = **−284.66 Ha** — a **75 Hartree** (≈47 000 kcal/mol) gap
  between two structures with *identical atoms*. Impossible as chemistry.
- Inspecting the geometry the pipeline was handed: **min interatomic distance 0.142 Å**, between the
  acetone carbonyl carbon and the HCN carbon (a C–C bond is 1.54 Å). Whole-molecule extent only
  4.18 Å for a two-molecule system. **The two fragments were embedded on top of each other.**

**Why:** RDKit's ETKDG has **no intermolecular term for disconnected fragments**, so embedding a
multi-fragment reactant SMILES collapses the fragments into one another. The pipeline then takes
`e_react` as a **single point at that geometry, never optimised**, so the endpoint energy is tens of
Hartree too high. The NEB relaxes the interior images to sane structures, which therefore sit far
*below* the corrupt endpoint, and `hei < max(e_react,e_prod) − 1e-4` fires. There *is* an interior
maximum; it is simply below a garbage endpoint. This explains all of it at once: 3/3 bimolecular
failures, 450/450 on Transition1x (sane, DFT-optimised, supplied geometries), and the misleading
"non-monotonic" wording.

**The fix is therefore bigger than "optimise the endpoints"** — you cannot reliably optimise out of a
0.14 Å C–C clash; the optimiser is as likely to simply let the fragments react. Required:
1. embed **each fragment separately**;
2. place them as a **pre-reaction complex** (reacting atoms ≈2.5–3.5 Å apart), not by a whole-system
   embedder;
3. **then** optimise the complex at the NEB's own level of theory;
4. and add the **cheap pre-flight guard that would have caught this in milliseconds instead of
   25 minutes of DFT**: reject any endpoint whose minimum interatomic distance is below ~0.8 Å, and
   check the endpoint energy against the sum of separately-optimised fragment energies.

Step 4 is the highest value-per-line change in this whole thread: a two-line sanity check in front of
the oracle, versus 81 minutes of DFT spent on inputs that were never physically valid.

**Consequences.** (i) The 0/11 admissibility result is **withdrawn** — it measured our endpoint
handling. (ii) The granularity claim keeps only its independent Draslovka/Biltz support. (iii) The
**normalisation layer** must therefore include *endpoint optimisation at the target level*, not just
balancing and mapping — a design requirement we did not know we had. (iv) Ready to transfer to Robin.

**To settle it definitively (cheap, ~minutes):** take a Transition1x reaction the pipeline already
solved *with supplied geometries*, discard them, regenerate from SMILES through the same ad-hoc path,
rerun. Failure ⇒ contract/conversion confirmed. Secondary: ask for endpoint energies and the logged
`perp_rms` for the three failures — if the maximum sits at an endpoint and `perp_rms` is large, the
band never converged either. Also ask for the reactant `.xyz` files: whether both fragments are
present, and at what separation.

## EVIDENCE AUDIT 2026-07-30 — how many of our negatives are TRUE negatives?
Prompted by the owner's question. Verdict: **of ~9 standing negatives, 2–3 are robust and 6–7 are
single-setup, thin-n or confounded.** The "four independent fronts" framing I used on 07-28 is better
stated as **four fragile signals pointing the same way** — suggestive *because* independent, but not
one of them would survive a referee alone.

### Robust (would survive review)
- **Gradient-free barrier shortcut fails** (Skala over an LST scan): 225 reactions × 2 directions
  against Transition1x reference barriers, MAE 47.72 (17.81 bias-corrected), +102 % bias, ρ 0.673.
  Adequate n, real reference, huge effect. True negative *for that shortcut*.
- **Baseline / citation corrections**: MT USPTO_MIT top-1 = 90.4 not 88.8; ReactionT5 journal ≠
  preprint; RDKit-version dependence (41/40 000 flip). Verified by exact reproduction, byte-for-byte
  against upstream's own predictions. These are *facts*, not inferences.
- (Positive, and the best-controlled experiment in the tree) **breadth-matched L\* beats the Retro\*
  value net**: 4 seeds, tight sd, pure-`h` control, leak-checked, off-ceiling datasets carry it.

### Fragile — must NOT be quoted as settled
| Negative | Why it is not yet a true negative |
|---|---|
| σ ⊥ \|error\| (retro-pfn) | **Already flipped once on setup choice** (regression-σ/Morgan-GP/AUC → classifier-entropy/DRFP/F1). Setup-sensitive, and measured on **yield**-HTE, not on the route task we actually claim. |
| epistemic ≈ random | **2 seeds**; MC-dropout only, a weak epistemic estimator; the source paper's claim rests on a BNN we never ran. |
| epistemic-MCTS negative | One **crude implementation** (σ bonus into leaf value), not the hypothesis (σ in *selection*, UCB). The leaf itself re-elevated it as H2 — so the negative is scope-limited and we have been reading it as general. |
| MolPFN variance floor | Checkpoint selected on **train** loss; temperature fixed at 1.0; **`ctx_len`=8** (8 points is a poor basis for estimating a spread — a floor is the *expected* outcome); **no conditioning-token arm** (all configs `qry_props: none`); label ablation missing for exactly the two configs where conditioning works. |
| Mechanism kernel loses at route level | Two confounds already identified (fixed absolute threshold vs differing per-arm score distributions; route-length compounding). Already sent back for a calibration-matched rerun. |
| 0/11 admissibility | **Positive control failed** → cannot attribute to the inputs. Criterion is "no interior maximum", and all three cases are bimolecular-from-SMILES against a pipeline validated on geometry-supplied Transition1x. See retraction above. |
| FlowER worse than T5 | `59/211` vs `504/4923` — **different denominators**, and plausibly different tasks/output granularity. The comparison is not obviously sound as stated. |

### What the ground truth actually is now, per claim (the honest inventory)
After **reference-match / top-1 was ruled UNSOUND** (2026-06-10) and **SSP ruled CONFOUNDED**
(2026-06-12), and after round-trip was shown to be **artifact-prone on in-distribution chemistry**
(Draslovka: MMA NLL≈0.000 yet round-trip FAIL), there is **no single oracle**. Three different ones
are in use for three different sub-claims:

| Sub-claim | Oracle in use | Domain of validity |
|---|---|---|
| does a reaction work | **HTE yield datasets** (Buchwald–Hartwig, Suzuki) — real wet-lab | 2 curated families, HTE conditions, in-distribution *by construction* |
| barrier accuracy | **Transition1x** reference barriers | computational ground truth on **curated elementary** reactions — the regime our planner never emits |
| route/search quality | **PaRoutes / USPTO-190** "solved = reached buyable stock in budget" | a **search** criterion, not chemical correctness |
| step plausibility | forward round-trip (T5), continuous, AUROC 0.91 / ECE 0.16 | artifact-prone; rejects textbook chemistry |
| granularity / named reactions | LLM judge | **unscripted, never validated against anything** |
| chemist labels | **none** | RetroTrim has them; we do not |

**The gap, stated plainly: we have no validated ground truth for the quantity we actually claim to
predict — whether a proposed route step would work in a reactor.** We have real yields on two curated
families, computed barriers on curated elementary steps, and a search-success criterion. Each is a
proxy for something *adjacent*. Worse, the **declared programme metric — budget-to-solve per stratum —
has never once been computed** (`solution_time` = `inf` in every arm of the (c) test), and the strata
may not even be difficulty-ordered (far solves better than close, reproducibly).

### Protocol this tree does not have and needs
1. **Per claim, name the oracle and its domain of validity** before running, not after.
2. **Positive control mandatory, and a negative counts only if the control passed in the same run.**
   (Robin's spec had one — it failed, and we nearly banked the result anyway.)
3. **Minimum 3–5 seeds** with spread reported. Several standing results are n=2.
4. **Pre-register the metric**; fix `solution_time` so budget-to-solve actually exists.
5. **Audit the stratification** before any further per-stratum claim.
6. **Separate "tool failed" from "hypothesis false" in the status vocabulary** — Robin's controlled
   vocabulary already does this well; generalise it to every leaf.
7. **A negative is scoped to its implementation** unless a second, differently-built arm agrees.

## ARBITRARY-SUBSET CONDITIONING over complete reactions (owner reframing, 2026-07-31)
**Supersedes the "role identification" framing I proposed.** Owner's objection is decisive: *a role
is user intent, not a property of the reaction.* HCl from an acylation is a byproduct if you want the
amide and the product if you want HCl; water from an esterification is waste unless you are studying
dehydration. So any fixed reactant/reagent/byproduct schema bakes in one consumer's intent, and
ORDerly-style role labels inherit that.

**The reframing: train on COMPLETE reactions, generate under PARTIAL conditioning.** Keep every
species on both sides at training time; at inference, condition on whatever subset you know and let
the model complete the rest. One joint model over (reactants, reagents, conditions, products,
byproducts) replaces the field's separate fixed tasks:
- condition on {reactants} → forward prediction (products *and* byproducts)
- condition on {product} → retrosynthesis
- condition on {product, one reactant} → co-reactant / reagent proposal
- condition on {reactants, product} → **condition prediction**
- condition on {reactants, product, conditions} → scoring / feasibility

**Why this is better than role labels, concretely.**
1. **Intent-free.** Nothing is designated waste at training time, so no consumer's convention is
   privileged.
2. **It dissolves the forward/retro asymmetry structurally.** The round trip stops being a hoped-for
   property of two separately-trained models and becomes conditioning the *same* joint model two
   ways. This is the clean answer to the byproduct/round-trip question measured on 2026-07-31
   (products carry a byproduct in 6.8% of records; the forward model emits one in 0/250).
3. **It is the tree's own line.** Arbitrary-subset conditioning *is* the in-context / amortised-
   Bayesian shape `MolGPT`/`MolPFN` and the PFN thread care about, applied to reactions — and it is a
   sharper niche than "in-context reaction generation" because the differentiator is the
   **conditioning set is a free variable**, not the modality.

**The binding constraint moves to data COMPLETENESS, and that is measured: 2.4%.** Only 6/250 real
USPTO records are atom-balanced, so a corpus of complete reactions does not currently exist at
scale. Training this needs completion first — and completion is partly rule-derivable
(esterification → water, acylation → HCl, quaternisation → halide; SynRBL-class), with the model
generalising beyond the rules afterwards. Not circular, but ordered.

**CONVERGENCE WORTH NAMING: one component now serves both students.** The
balancing/completion layer is (a) exactly what `retrosyntesis`' physics track needs, because a
transition state only exists for a balanced elementary step, and (b) exactly what
`retro-generation` needs to train a joint model on complete reactions. The
"highest-leverage unowned piece" identified on 2026-07-30 now has **two customers and one spec**,
which is the strongest argument yet for resourcing it deliberately rather than letting each student
improvise it.

**Prior-art obligation before any build** (rektomar's standing protocol, and this is exactly the kind
of idea that has precedent): any-order / masked-infilling reaction models, multi-task reaction
transformers (Chemformer's task heads), text-infilling formulations of reaction prediction, and
any-subset conditional generative models generally. The niche is only defensible if
*arbitrary-subset conditioning over complete reactions* is genuinely unoccupied.

## NODE ALLOCATION BY CONCERN (owner observation, 2026-07-31) — numerics is in the wrong place
**Owner's framing: `retrosyntesis` is an INTEGRATION project; numerical development belongs in the
physics node.** Checking it against reality shows the misallocation is real and worse than it looks.

**What is actually where.** `retrosyntesis` (co-owned moczyjor/mollerob) holds *both* concerns: Joris
owns integration (K-P-V benchmark, planner harnesses, learned validators, syntheseus) and Robin owns
numerics (`src/oracle_benchmark/`, DFT-NEB, Skala, `validation_kinetics.py`, the three-rung ladder).
Meanwhile **`retro-physics-validation`'s declared charter is almost exactly Robin's job** — "evaluate
physics-based tools for validating reactions … determine which tool is suitable for which kind" — and
it has **zero student commits in 7 days** (only the two enrolment commits). So the node chartered for
the numerics question is empty while the numerics is being done inside the integration repo.

**But the two were separated on purpose, and that constraint is still live.** `retro-physics-validation`
is not a numerics-development node as chartered; it is an **independent blind assessment** — the study
protocol has the student characterise tools on anonymised routes *before* opening
`data/ground_truth.md`. Robin's calibrated ladder is the un-blinded version of the same question.
Re-chartering that node as the numerics home therefore **destroys the blinding**, which was the point
of having it.

**So the decision is not "move the code" but "what is the blind study worth".** Three options:
1. **Blind study is worth keeping** → numerics needs its *own* home (new node, or Robin's own repo);
   `retro-physics-validation` stays an independent check.
2. **Blind study is dead** (7 days, nothing, and its offline phases were explicitly unblocked) →
   re-charter that node as the numerics home with **Robin** as owner. Cheapest in node count.
3. **Do nothing structural**, but declare the interface: `retrosyntesis` consumes a settled
   `oracle(reaction) → (barrier, status)` API and numerics development is explicitly scoped as
   Robin's sub-project inside it.
Recommendation: **decide (1) vs (2) by asking jinrehacek for a status first** — the numerics should
follow Robin regardless, because moving code away from the person who wrote it to an inactive student
is strictly worse than leaving it.

**Correction to my own handover:** `reaction_complex.py` went into
`retrosyntesis/coordination/handover/`. Under allocation-by-concern that is the wrong node — it is
neither integration nor numerics but the **shared symbolic layer** (RDKit, atom mapping, balance
arithmetic, geometry construction). It is self-contained with 11 passing tests, so relocating it is
cheap, and it should move wherever the completion layer ends up owned.

### Is retro-generation a consumer of numerics, or does it need something special?
**Consumer, weakly, and at small n — and the component it actually shares is not numerics at all.**
1. **Not a training signal.** At ~22 min/reaction a physics oracle cannot label at the scale a
   generative model trains on. Physics is an *evaluator* of a sample, not a source of supervision.
2. **What it genuinely shares is the completion/balancing layer**, and that is **symbolic
   cheminformatics** — rules, atom mapping, balance arithmetic — not numerics. Cheap, fast, upstream
   of everything. My miniproject §9 called it a dependency of "the physics-oracle track", which
   understates it: it is upstream of *both* consumers and belongs to neither.
3. **The one genuinely numerics-specific thing it could want: HARD NEGATIVES.** The corpus contains
   only reactions that worked, so a joint model trained on it has no representation of infeasibility.
   Physics can label a small set of *plausible-but-high-barrier* reactions — negatives no corpus can
   supply. A few thousand hard negatives are worth more for calibrating a likelihood than millions of
   random ones. That is a **data request, not a service dependency**.
**Consequence: do not wire retro-generation to the oracle in phase 1.** Its dependency is weak,
asynchronous, and satisfiable by a delivered dataset. The real coupling between the two students is
the completion layer, and that is the thing to resource and assign an owner.

### CORRECTION 2026-07-31 — the succession plan, and what I got wrong about it
**Owner's intent: Robin owns numerics now; `retro-physics-validation` is deliberately slow because
jinrehacek is TRAINING; when ready he takes over Robin's responsibility.** Three corrections to the
analysis above:

1. **I misread jinrehacek's seven silent days as drift. It is a planned ramp.** Withdraw that
   framing; it should not be repeated in a status.
2. **The blind study is primarily a TRAINING VEHICLE, not an independent check.** Its `GUIDE.md` walks
   Phase 0→6 — frame validation, characterise reactions before touching a tool, *map the tool ladder*,
   build a suitability rubric, small hands-on probe, suitability matrix. That is a curriculum for
   acquiring exactly the competence needed to inherit the oracle, and the blinding exists so he forms
   his own judgement first. **So option 2 from the node-allocation note — re-charter that node now and
   install Robin — would have destroyed the mechanism that makes the succession possible.** Do not.
3. **The structure was therefore already right; only the timing was unclear.** Numerics sits with
   Robin now → migrates to `retro-physics-validation` at handover → `retrosyntesis` becomes pure
   integration consuming a settled oracle. No node surgery required.

**What this changes in practice — Robin's most valuable remaining deliverable is TRANSFERABILITY, not
more numbers.** A succession only works if the incumbent's work can be picked up, and right now it
largely cannot: the specialty-set runner was never committed, results sat in a mode-700 home
directory, and the oracle-benchmark branch only merged on 2026-07-30. Concretely he should be asked
for: everything on `main`, results on the shared store, calling conventions documented, and the
endpoint fix integrated *with its test* — because the test is what survives a change of owner.

**Correction to my own correction:** I called `reaction_complex.py` misplaced in `retrosyntesis`.
Under the succession it is **correctly placed** — it is numerics plumbing (geometry construction and
NEB failure classification), it belongs with whoever owns numerics, and it should simply **travel with
the numerics** at handover. No relocation now.

**Gap that the succession makes load-bearing:** `retro-physics-validation/data/ground_truth.md` is 26
lines and contains **none** of Robin's measured ladder (no 8.83 kcal/mol NEB MAE, no ρ 0.902, no
Skala ΔE 4.02 / r 0.996, no failed-shortcut 47.72). The answer key predates the empirical result. It
should be updated before Phase 5, or jinrehacek's suitability matrix gets graded against something
weaker than what we already know.

**The binding constraint is Robin's end date, not jinrehacek's readiness.** Both are ENSICAEN
internship students, so there is presumably a fixed departure. If Robin leaves before the handover the
numerics is orphaned — and that date, which this node does not record, sets the deadline for the
transferability work above. Worth capturing.

**One thing the succession does NOT resolve: the completion layer.** It must *not* travel with
numerics, because `retro-generation` needs it too. It belongs with integration or as a Chemie-owned
component — still the only unowned piece, now with three consumers (Robin's barriers, Joris's gates,
Martin's M2).

## STRATEGY 2026-08-02 — two academic bets, everything else backbone; ξ_f OPEN but DEPRIORITISED
Owner's framing, adopted. It resolves several ambiguities that have been open for weeks.

**Academic priorities** (where we intend to contribute):
1. **Uncertainty-aware planning** — "a better KeeA*".
2. **`retro-generation`'s any-subset conditional generation** (`MINIPROJECT-conditioning.md`).

**Everything else is backbone**: use the best existing tools as well as we can, and do not rebuild
what the field already provides. Feasibility gating = continuous round-trip (AUROC 0.91, and the
measured 18.5 pp advantage over exact-match) + physics barriers where admissible + LLM/ensemble
judging, where MOSAIC and RetroTrim already own the ground.

**`xif` / ξ_f: OPEN, DEPRIORITISED — not closed.** Its organising thesis lost its mechanism (σ ⊥
error; the mechanism kernel does not beat a plain structural GP at route level) and it has been
dormant since 2026-06-18. It is *not* being wound up: the route-relevance VOI question — "spend the
expensive oracle where it changes a decision" — remains the one un-scooped part and is exactly what
the sister project `~/zcu/PFN4BOrevisited/DecisionBO` is pursuing in the BO setting. Deprioritised
means: no new resourcing, no headline claims, keep the line alive, and **let DecisionBO lead** —
re-prioritise if their objective-side result transfers.

**Status against the priorities, honestly:**
- Priority 2 is healthy: active, staying, right expertise, well-posed with kill criteria at M0/M1.
- **Priority 1 has no one on it.** `retro-planning` has had no commit since 2026-07-05 (4 weeks) and
  six artefacts remain uncommitted; the theory half sits in the peer tree `~/AIC/Planning`. Of the two
  students who stay, one is priority 2 and the other is backbone numerics. This is a resourcing
  decision, not a research one.
- Backbone is in decent shape except the **completion/mapping layer**, still unowned, now blocking
  three consumers.

**Recommended refinement of priority 1 — define uncertainty as OBJECTIVE COVERAGE, not posterior
variance.** All four of our uncertainty negatives were model-posterior quantities (GP σ, ensemble
spread, MC-dropout, in-context scale). None asked *"did my training objective constrain me here?"* —
and that is precisely what retro-planning's best result points at: L*'s OOD weakness was **coverage**,
because a pairwise rank loss only constrains pairs that co-occurred on OPEN. A coverage-based
epistemic signal is different in kind from the four that failed, is motivated by our only positive OOD
finding, and differentiates from KeeA*'s epistemic *selection*. It also folds in the tree's genuine
un-scooped asset: path-consistency is **dense, absolute, propagating** where rank is **sparse,
relative**.

## CROSS-TREE TRANSFER 2026-08-02 — DecisionBO tested our thesis and REFUTED it
Read of `~/zcu/PFN4BOrevisited/DecisionBO` (THEORY, HYPOTHESES, RESULTS_p0, EXPERIMENTS, ADRs 0001–0009,
outbox to 07-12). **Note the parent's `synthesis.md` is stale — last updated 2026-06-14, and still
presents the founding thesis as the open slot. The leaf spent June refuting it.**

**The number that matters most to us.** Their M2 = a region-localized pairwise **ranking loss** on the
predicted mean, i.e. structurally our "rank, not estimate". Its advantage over plain likelihood
training, swept across model capacity (1 seed/rung):

| model / steps | surrogate quality ρ_off | rank-loss gain Δρ_in |
|---|---|---|
| d16/L1/15k | 0.19 | **+0.097** |
| d32/L2/30k | 0.56 | +0.028 |
| d64/L3/60k | 0.62 | −0.006 |
| d128/L4/150k | 0.65 | **−0.007** |

Monotone decay, crossing zero at **ρ_off ≈ 0.6**; a 14× swing. Their verdict: *"the pilot gain is GONE
at scale. It was an undertraining artifact."* Confirmed on regret too — paired, 16 seeds, ties
everywhere (p=0.93, 0.74, 0.87). Their founding hypothesis H1 went 0.6 → **0.02 refuted**.

**The theory they built from it — "regret-relevant sufficiency"** (`paper/03regret-sufficiency.tex`):
a surrogate influences the decision only **up to a quality threshold**; above it the outcome is set by
the acquisition, the search and the budget. Source-validated: every published success of
value-aware/loss-calibrated learning they could find was demonstrated *below* a threshold — VaGraM
under reduced capacity, Maus 2024 under a constrained SVGP budget, Lacoste-Julien under a constrained
variational family, Bergna under noise.

**This unifies our own findings into one sentence: the training objective matters exactly while you
are below sufficiency.** And our tree already shows the shape — L\*-rank beats the *vanilla* value net
but loses by 8–11 pt to MEEA\*-PC, which has more data and a better architecture. **So "rank, not
estimate" may have a shelf life, and we have not tested where ours sits.**

**ACTION (cheap, decisive, and it should gate priority 1):** rerun the rank-vs-value comparison at
3–4 rungs of capacity/training length and plot the gap against a quality proxy. Monotone decay ⇒ our
rank result is a low-capacity phenomenon and the planning story needs rebasing on the objective
*structure* (path-consistency) rather than on rank per se.

### Where their evidence CONTRADICTS ours — the most useful part
1. **σ may not be dead in our setting.** Their nulls are all on **deterministic** benchmarks, and
   ADR-0004 states decoupling gains arise only under **heteroscedastic** noise, ≈0 homoscedastic,
   exactly 0 deterministic; they later declared their home turf to be ≳1–3 % relative noise. **Our
   feasibility signals are experimental and noisy**, so their nulls may simply not transfer, and σ
   could be worth more to us than to them.
2. **Global vs local acquisition — they caught themselves twice.** Global KG scored 32.6 where the
   *same* one-step KG confined to a trust region scored 9.27 on the same problem the same day
   (p=0.0009, replicated p=0.0008). H16 was corrected to: *"VOI is universal; what is regime-limited
   is the myopic one-step VOI approximation."* **Our un-run route-relevance VOI is precisely the
   localized form** — so the evidence argues it may work where our global σ-acquisition failed. That
   is a concrete reason the deprioritised ξ_f line should stay open. (Caveat from their record: local
   KG carries a catastrophic tail — mean 1300 vs 941 — and needs a fallback.)
3. **A published fix for MolPFN's variance floor.** Their calibration was *fine* (pred/true-std ≈0.91)
   and still bought nothing; their failure mode was **sharpness, not calibration**, with fidelity
   collapsing in dimension (0.90@D4 → 0.55@D12). And **Decoupled PFNs (Bergna 2026)** gets scale right
   and wins, by supervising latent-signal and aleatoric heads with **privileged `f`/`σ²` labels from a
   controllable prior**. That is a live, published fix for exactly our in-context-scale negative — and
   note it is *better likelihood training with privileged labels*, not decision training. Actionable
   for MolPFN, whose prior is controllable.
4. **They named our route-level null: "acquisition insensitivity".** Surrogates that rank candidates
   alike pick the same points, produce identical trajectories and yield null downstream deltas —
   exactly the mechanism-kernel result. Their ADR-0002 response is the evaluation design we should
   adopt: **lead with a low-variance mechanism metric measured in-region vs off-region, treat the
   downstream outcome as noisy confirmation, and always pair an off-region parity guard** so a gain
   is not bought by destroying global fit.

### Methodology to adopt wholesale (this is the criteria list, already built)
- **Undertraining masquerades as a method win** — never accept a training-objective result at pilot scale.
- **Init-design pseudo-replication** (flagged tree-wide 2026-07-05): a run seed shared across problem
  instances silently reduces design-replication n to the number of seed values. **Four of their
  headline results at p ≲ 0.003 collapsed**, one reversing sign. Fix: `run seed = base + s + 9973·i`.
  *"n≥32 paired + Wilcoxon is not sufficient if the design is shared."* Directly relevant to
  retro-planning's multi-seed comparisons.
- **Random is the bar, not a formality** — MALIBO scored *below* Random on the only discriminating task.
- **Carry the dumb classical baseline** — Py-BOBYQA beat the entire GP stack by ~16× geo-mean on
  deterministic problems.
- **Reproduction gate (ADR-0003):** no competitor enters a head-to-head until our run reproduces *that
  paper's* headline on *that paper's* benchmark; "could not reproduce" is a recorded outcome, never a
  silent strawman. It caught an AABO inversion that was their adaptation's artifact, not the method's.
- **Pre-register where the lever must NOT pay** (their γ̂=∞ honesty cells); a gain there is a red flag.
- **Guardrail principle (ADR-0005):** every refuted hypothesis is kept as a baseline, and no "the
  learned thing is needed" claim is admissible until it beats the strong simple alternatives on the
  same problem. Our analogue: no learned-`h` claim until it beats SAScore *and* MEEA\*-PC.

### ACTION MAPPING 2026-08-02 — where the DecisionBO transfer lands
Note first: **most of it lands on academic priority 1, which is the one with no capacity.** The
transfer sharpens exactly the thing we currently cannot act on. That is the operational headline.

**GATES — run before investing further in priority 1. Both currently unowned.**
- **G1. Capacity sweep, rank vs value.** 3–4 rungs of model size / training length, plot the gap
  against a quality proxy. Decides whether "rank, not estimate" is a real effect or our version of
  their +0.097 → −0.007. Cheap (existing harness, existing data). **If it decays monotonically the
  planning headline must be rebased on objective *structure* — path-consistency — not on rank.**
- **G2. Seeding audit of retro-planning.** Their init-design pseudo-replication collapsed **four**
  headline results at p ≲ 0.003, one reversing sign; the trap is a run seed shared across problem
  instances, which silently reduces replication n to the number of seed values. Our L\* verdict-flip
  (4 seeds, tight sd) and the 6-dataset comparison are exposed. Check the seeding; if shared, re-run
  with `run seed = base + s + 9973·i` before the result is quoted again. **The L\* flip is already
  published in the briefing**, so this is a correctness issue, not housekeeping.

**ROUTE — one concrete method to a named consumer.**
- **R1. Decoupled PFNs (Bergna 2026) → `retro-generation` §Q3/scoring, and MolPFN.** A published fix
  for calibrated scale via privileged `f`/`σ²` labels from a **controllable prior** — which MolPFN
  has. It is better *likelihood* training, not decision training, so it sits inside the backbone
  framing rather than competing with a priority.

**ADOPT — the evaluation protocol, borrowed rather than invented.**
- **P1. Mechanism-first evaluation (their ADR-0002).** Lead with a low-variance mechanism metric
  measured **in the decision-relevant region vs off it**; treat the downstream outcome as noisy
  confirmation; always pair an **off-region parity guard** so a gain is not bought by wrecking global
  fit. This is the design our mechanism-kernel null needed and did not have.
- **P2. Guardrail principle.** No "the learned thing is needed" claim until it beats the strong simple
  alternatives on the same problem. Our analogue, binding: **no learned-`h` claim until it beats
  SAScore *and* MEEA\*-PC.**
- **P3. Random is the bar**, not a formality. **P4. Carry the classical baseline.** **P5. Reproduction
  gate** before any head-to-head; "could not reproduce" is a recorded outcome. **P6. Pre-register the
  cells where the lever must NOT pay**; a gain there is a red flag.

**CORRECT THE RECORD — two claims I have been over-stating.**
- **C1. "Four independent σ negatives" needs scoping.** Ours were: GP/ensemble σ ⊥ error on HTE,
  epistemic ≈ random **under MC-dropout** (a weak estimator; the source paper's claim rests on a
  BNN we never ran), a crude MCTS leaf-value bonus, and in-context scale. That is a strong negative
  for *those estimators*, not for uncertainty in general. DecisionBO's own nulls are
  **deterministic-regime only** and therefore do not corroborate ours the way I implied.
- **C2. Route-relevance VOI is the LOCALIZED form, and localization is exactly what rescued their
  result** (global KG 32.6 vs the same KG in a trust region 9.27, p=0.0009). Recorded as a standing
  prediction: if ξ_f is re-prioritised, the route-localized VOI is the arm most likely to work, and
  the global σ-acquisition negative should not be read as having pre-refuted it. Their caveat travels
  with it: local KG carries a catastrophic tail and needs a fallback.

**UNCHANGED, but now better justified:** ξ_f open-and-deprioritised (C2 strengthens it); the
completion/mapping layer still unowned and still blocking three consumers.

## THE OOD LABEL IS MEASURING THE WRONG CORPUS — resolved 2026-08-06
The `far`/`close`/`in-distribution` stratification of the 190 hard targets is **invalid**, and the
mechanism is now identified rather than suspected. Scripts/logs:
`/mnt/data/resynthesis/admissibility/` (`B0_leak.py`, `B1_basek.py`).
**Full writeup: [`docs/ood-strata-invalid.md`](../docs/ood-strata-invalid.md)** — measurement,
demoted alternatives, void/survives lists, three ranked fixes, reproduction, limits. Published to
the knowledgebase 2026-08-06 (`briefing/what-we-tried.md`, `reports/retro-planning.md`, and the
generalised lesson in `tutorial/data-landscape.md`).

**What the label is.** `calculate_ood_190.py`: max **Morgan-2 (2048-bit) Tanimoto of the TARGET
MOLECULE** to "base K", thresholded ≥0.8 → in-distribution, 0.5–0.8 → close, <0.5 → far. base K =
`ord_global_index.json` + RxnScribe-extracted ACS patents. Verified: base K is **1 048 347 product
molecules**, and the label is **computed correctly** — `far` targets really do sit at max Tanimoto
0.32–0.49, and 94.2 % of in-distribution targets are *literal members* of base K while 0/25 `close`
and 0/28 `far` are.

**The killer measurement.** Scanning all **1 939 253** rows of `uspto.csv` for the targets as products:

| stratum | target appears as a USPTO product | n |
|---|---|---|
| in-distribution | **78.1 %** | 137 |
| close | **96.0 %** | 25 |
| **far (deep-OOD)** | **100.0 %** | 28 |
| all | 83.7 % | 190 |

**Every single "deep-OOD" target is a verbatim USPTO product, and the gradient is INVERTED** — the
stratum labelled most novel is the most memorised, the stratum labelled least novel is the least.

**Why.** The label measures novelty against **ORD's product index (1.05 M molecules)** while the
planner's knowledge comes from **USPTO (1.94 M reactions)** — the templates are USPTO-derived, every
policy (T5, MT, Chemformer, LocalRetro, AZF) is USPTO-trained, PaRoutes is USPTO-derived, and the
Chen-2020 target list is USPTO-derived. The two corpora overlap only partially, so a target can be
genuinely far from ORD while being a memorised USPTO product. **The label is not wrong arithmetic; it
is the wrong reference corpus** — and empirically it is *anti-correlated* with novelty relative to
what the planner actually learned.

**This fully explains the inversion seen three times** (June KPV, the July (c) test, Joris's August
MEEA benchmark). Two secondary contributors, both now demoted: `far` targets are also mildly
*easier* chemically — significantly fewer stereocentres (1.29 vs 2.12 close, p=0.036; 35.7 % vs
20.0 % wholly achiral), lower Fsp3 (p=0.014 vs in-dist), more aromatic (p=0.028) — and Joris's
MEEA inversion is **not statistically supported at all** (far 28/28 CI [87.9,100] overlaps close
22/25 CI [70.0,95.8]). The (c) test inversion *is* significant (far 77.8 % vs close 48.0 %,
permutation p=0.041), and note there the outlier is **`close`**, with `far` ≈ in-distribution.

**VOID as a result of this.** Every claim of the form "method X generalises / degrades out of
distribution" that rests on these strata: retro-planning's "L\* degrades OOD" and "OOD
generalization is the open gap"; the (c) test's per-stratum diversity comparison; Joris's "ReactionT5
is robust when facing chemical novelty" (its 100 % on `far` is 100 % memorisation). **The briefing
carries per-stratum L\* numbers (in-dist 69 % vs 52 %, deep-OOD 79 vs 82) and must be corrected.**

**SURVIVES.** Anything pooled or stratum-free: the reseeded L\* result (64.43 % vs 61.86 %, 6/6
datasets), the budget-exhaustion finding that seeded `retro-planning` (independent of this label),
the oracle ladder, and the barrier work.

**The fix — three options, in increasing order of trustworthiness.**
1. **Re-reference the label** to the corpus the planner actually learned from (USPTO templates), not
   to ORD. Cheap, and it makes the existing axis meaningful.
2. **Define novelty over reactions, not products** — template rarity or required-transformation
   similarity. This is the quantity that should have been measured; product-structure novelty was
   never the right proxy for synthetic difficulty.
3. **Use a genuinely external corpus.** ORDerly's **non-USPTO test sets** (rektomar's find) are the
   only construction here that cannot be contaminated by USPTO. This is the one that would let us
   make an OOD claim at all.
Until one of these lands, **no OOD claim from this tree is admissible** — and per ADR 0004 the
existing ones are not grandfathered.

## DEEP STATUS 2026-08-17

**Moved:** retro-physics-validation (jinrehacek), Chemie. **Silent since 08-05/06:** retrosyntesis
(moczyjor, mollerob), retro-generation, retro-pfn, retro-planning.

**AIMNet2 on BH9** (jinrehacek, 449 reactions / 898 barriers, exact geometries):

| | MAE (kcal/mol) |
|---|---|
| barriers, general `aimnet2` | 16.70 |
| barriers, domain-routed | 4.728 — in-sample; fallback chosen after inspecting BH9 |
| reaction energies, routed | 2.881 — beats 19 of 25 DFT variants in BH9 Table IV |
| worst TS failures | up to 77 |

Same model scored 4.76 on Transition1x. BH9 is 57.5 % multi-fragment; Transition1x 0.1 %.
Not a safe final kinetic oracle. Step 2 (geometry error) blocked on BH9 SMILES — answered in his
inbox: connectivity from XYZ acceptable, stereochemistry is leakage.

**R7 — our July diagnosis was incomplete.** `build_endpoints` gave a guarded 2.5 Å contact; the
reactant still relaxed to 4.632 Å under AIMNet2-rxn. `NO_AIMNET_CONTACT_MINIMUM`, NEB not started,
no barrier claimed. Placement was a defect, not the defect.

**Barrier pipeline** (this node, autodE 1.4.5 + ORCA 6.1.1): errors −5.95, −2.98, −2.47 on three
pericyclic reactions vs BH9's PBE0 pericyclic MAE 3.34. DLPNO-CCSD(T) rescore of **all three**,
single points on the same geometries: errors **−0.73, +0.92, −0.88**, mean absolute **0.84** vs
PBE0's 3.80, signs differing. Geometry right, error is the functional, at n=3. Stereochemistry-free input SMILES:
+8.57 kcal/mol error. Zwitterionic product expels CO₂ under gas-phase optimisation (C–O 1.16 Å,
C–C 3.0–3.4 Å); autodE refuses a barrier.

**Unowned:** implicit solvation; conformational sampling (untested — everything that ran is rigid,
the one flexible case cannot run gas-phase); hydrogen-resolved atom mapping, three consumers.

**Fixed:** `rehacji1` now in the `resynthesis` group.

**Departures — recorded 2026-08-17.** Joris (moczyjor) and Robin (mollerob) have left. Last commits
2026-08-05 and 2026-08-06.

**Succession.** The physics/numerics line transfers to jinrehacek **gradually**, not at once. First
piece sent 2026-08-17: run R7 through autodE + ORCA — one bounded reaction that settles his own open
question, with the working invocation and the five environment traps supplied. Explicitly retained
here for now: the six-reaction walkthrough, cost-ladder validation at DFT level, solvation, and
planner integration. BH9 Step 2 stays his higher priority.

**Open:** `retrosyntesis` is now unowned — its `AGENTS.md` still lists `owners: [moczyjor, mollerob]`.
Owner intends to take it as the shared integration node.

## DEEP STATUS 2026-08-21

**Moved:** this node + `briefing`. **Silent:** retro-generation, retro-pfn, retro-planning
(pre-08-17); retrosyntesis (only our merge/salvage).

**jinrehacek — working, then quiet.** 39 RCI jobs, all on **08-17 itself** and all behind the report
he committed that day (`r7-aimnet-neb` ×6, `bh9-aimnet-{full,2025,routed}` ×7). Nothing since:
no jobs, no commits, 4 working days. Three tasks outstanding, assigned that same day after his
commit — BH9 Step 2 (priority), the R7 autodE/ORCA run, and the `reaction_complex.py` reconciliation.
The last needs no compute, so local work would be invisible. Not chased yet.

**This node.** Barrier-accuracy requirement measured on real routes: error **correlation** dominates
**magnitude** — a 16.70 kcal/mol oracle with error common to a route's steps disturbs the chosen route
less than a 0.84 kcal/mol oracle whose error varies (8.3 % vs 14.4 % top-1 flip at w=20). Proposes
selecting the functional by `|ME|/MAE` rather than MAE; BH9's Table V already tabulates it (ωB97M-V
2.15/2.06; PBE0 3.34/**−0.05**, i.e. autodE's default is the scatter case). **Deliberately unpublished**
pending confirmation — job `11381115` rescores the three validated geometries at ωB97M-V.

Framing correction recorded: DFT error is deterministic, not noise, so the perturbation repeats are
arithmetic over reactions, not statistics. Numerical settings measured at **0.047 kcal/mol** total
(SCF 0.028, grid 0.019, COSX 0.000) — axis closed, and it exonerates our configuration.

**Briefing** carries the confirmed results only: the working DFT oracle, the DLPNO rescore, AIMNet2 on
BH9, the two mapping failures, stereochemistry at 8.57, the zwitterion, and Transition1x being 99.9 %
single-fragment. Correlation result withheld.

**retrosyntesis** triaged 24 branches → **1**, 23 `archive/*` tags pushed first. Robin's never-merged
`18-handover` integration is on main (his 12 tests pass). **Open:** `reaction_complex.py` now exists
twice and has diverged — `validation_dft_neb` imports the older `src/` copy, so the pipeline runs
without `SUBMERGED_BARRIER`, `e_separated` or the Open Babel backend. Assigned to jinrehacek.

**Board:** 3 messages, 2 open to pfn4bo (2026-08-02 sufficiency, 2026-08-06 leaked OOD). No replies.

**Cluster note:** a `corpus_v1_iv` array (~99 tasks) and the `army-*` line run under `smidlva1` and are
not this tree's. Unlabelled RSA key in `~/.ssh/authorized_keys` still unidentified.

**Unowned:** implicit solvation; conformational sampling (untested — everything that ran is rigid, the
one flexible case cannot run gas-phase); hydrogen-resolved atom mapping; `retrosyntesis` ownership
(`AGENTS.md` still lists both departed students).

## RECONCILIATION 2026-08-26 — the portfolio is labour-bound, and the strongest assets are the evaluation negatives

Owner asked for a reconciliation: too many open streams, where is the highest gain. This section is
the triage. It **supersedes the "five efforts" framing** in `AGENTS.md` and `briefing/README.md`,
both of which still read as though five lines are live.

### The binding constraint, measured

Last **non-owner** commit per node, checked against `origin/main`:

| node | last student commit | reality |
|---|---|---|
| `retro-pfn` | **none in last 20 commits** | dormant since 06-18 |
| `retro-planning` | **none in last 20 commits** | no real work since 07-05 |
| `MolGPT` | **none in last 20 commits** | dormant |
| `retrosyntesis` | 08-07 (mollerob, departed) | **unowned** |
| `retro-generation` | 2026-07-30 in git | **but working on RCI to 08-10** — see below |
| `retro-physics-validation` | 2026-08-17 (jinrehacek) | training ramp, quiet 9 days |

Every node's most recent commit is the owner's. Three of six have no student activity in recent
history at all. **Anything that needs a student to finish is already parked whether or not we said
so.** The real choice is what the owner finishes alone, plus which single student bet gets protected.

**Consequence for academic priority 1 (uncertainty-aware planning).** Recorded as having nobody on it
on 08-02. Twenty-four days later: still nobody, node dormant, and both gating experiments (G1 capacity
sweep, G2 seeding audit) still unowned. It is an aspiration, not a priority. Record it as parked.

### rektomar is NOT silent — the git signal was wrong

`git log` shows nothing since 07-30, but `/mnt/data/resynthesis/retro-generation/` has work to
**2026-08-10** and an **unpushed `coordination/outbox.md` on the cluster**. This is exactly the
"uncommitted work is invisible to a pointer pull" trap `AGENTS.md` warns about, and the 08-21 deep
status called him silent on the strength of git alone. **Withdraw that.**

What is in the unpushed outbox, and it is substantial:

- **FlowER reproduced at full scale on its own benchmark.** 162 002 elementary steps × 32 samples =
  **5 184 064 ODE integrations**, ~45 V100-hours, scored with upstream's own `sequence_evaluation.py`.
  All **13** reported numbers within 0.5 pp (top-1 step 88.41 vs published 88.48; pathway 88.75 vs
  88.97; validity 94.84 vs 94.94). Targets read from the article's Source Data spreadsheet, not off
  the plot.
- **The conservation claim is exact and replicates: 0 non-conserving predictions in 5 184 064
  samples.** Against Fig. 2a's 17.2–33.0 % cumulative conservation for G2S/MT on the *same* balanced
  corpus. His conclusion, and it should be adopted: **consume balance structurally rather than learn
  it.** This closes his Q4 twice over.
- **Four things the paper does not say.** (i) The metric is **unseeded** — `eval_multiGPU.py` never
  calls `set_seed`; rerunning one shard moves top-1 pathway by **1.10 pp**, and Fig. 2b/c carry no
  error bar, so the published number cannot be reproduced exactly by anyone including the authors.
  (ii) Pathway accuracy is **teacher-forced** — it scores ranks along the ground-truth graph with the
  true intermediate at every branch, so it carries no compounding error and is not what
  `beam_predict.py` does. (iii) Inference costs **~100× Molecular Transformer** per reaction on
  identical V100s (~1.0 step/s vs 17.6 rxn/s at 5.8 steps/reaction) — for a propose→validate loop
  this **inverts** the efficiency comparison the paper makes on parameter count. (iv) The 7M-vs-16M
  framing holds: at top-1 FlowER-7M is third of four, 3.54 pp behind G2S on pathway; parity needs
  16M, i.e. G2S's own budget. Conservation is free only at matched capacity.
- **Two leakage facts nobody reports**, from a 3.8M-step scan of both corpora: `master`'s training set
  contains **2.72 %** of the *published* test split, and within each corpus **~4 %** of test steps
  appear verbatim in train (reaction-level split, step-level scoring). Also: the May 2026
  `flower_new_dataset` is **a different benchmark, not a patch** — same reactions (+2.5 %) cut into
  31 % more elementary steps, only 64 % of old steps surviving, 52 % of the new test split new material.
- **Still open, and it gates his own headline:** overlap between FlowER's corpus and the **USPTO-MIT
  test split**, which decides whether anything trained there is reportable against his 85.4.

**This materially changes the paper picture** (below): benchmark-integrity findings are no longer one
person's analysis of one target list. Independent person, independent benchmark, same class of defect
— unseeded metrics, teacher-forced evaluation, train/test leakage, corpus substitution.

### ωB97M-V returned, five days unread, and it inverted its own prediction

Job `11381115` COMPLETED 2026-08-21T00:41:36 — **four minutes after** the deep status that calls it
"pending" was committed (00:37:42). Full record: `docs/wb97mv-rescore.md`.

| rung, identical geometries | errors | MAE | \|ME\|/MAE |
|---|---|---|---|
| PBE0 (autodE default) | −5.95, −2.98, −2.47 | 3.80 | **1.00** |
| ωB97M-V | −1.56, +1.32, −0.54 | **1.14** | **0.23** |
| DLPNO-CCSD(T) | −0.73, +0.92, −0.88 | 0.84 | 0.27 |

Predicted from BH9 Table V: ωB97M-V 0.96 (systematic), PBE0 0.015 (random). **Measured: the reverse.**
On the criterion we proposed, PBE0 is the best of the three. Likely mechanism — accuracy and
systematicity are **not independent axes**, because removing systematic error is what makes a method
accurate, so a high |ME|/MAE is the signature of a large uncorrected bias.

**Survives:** the perturbation arithmetic (8.3 % vs 14.4 %), and that error *structure* dominates
error *magnitude*. **Withdrawn:** choosing a functional by |ME|/MAE read off a published table
(`barrier-accuracy-requirement.md` item 2, now struck; `docs/sota/` banner-corrected). **Gained
anyway:** ωB97M-V is a near-DLPNO rung at ~4× less compute (MAE 1.14 at ~4.3 min/reaction vs 0.84 at
~17 min) — adopt it on cost-accuracy grounds, not on error structure. **Newly blocking:** measuring
our own error correlation, which now needs n ≫ 3 across families on shared geometries — the argument
for adopting **RGD1** rather than generating it.

Second independent confirmation that the geometry is right: ωB97M-V and DLPNO are single points on
PBE0/def2-SVP geometries and both scatter small; a bad saddle would depress every method on it.

### The OOD fix was applied to the CODE ONLY — the strata were never regenerated

`retrosyntesis/src/benchmark/calculate_ood_190.py` was corrected by Smox656 on **2026-08-07**
("feat: ood stratification resolved (code only)") — the day after our 08-06 finding, before he left.
It now builds base K from **USPTO products** rather than ORD, i.e. it implements fix option 1.

But `src/benchmark/data/benchmark_190_hard_targets.csv` still carries **137/25/28**, the pre-correction
ORD-referenced strata. So the code is fixed, the labels in use are not, and **any rerun using that CSV
still reproduces the void stratification.** Regenerating it is cheap and unowned.

### Portfolio triage — what is actually finished

**Finished, defensible, needs only writing (owner-only, no student, no compute):**
- Benchmark integrity: 83.7 % of the 190 hard targets appear verbatim as USPTO products, rising
  monotonically to 100 % in the stratum labelled most novel (n=137/25/28, 1 939 253 rows).
  Round-trip artifact-prone on in-distribution chemistry (Draslovka MMA: NLL ≈ 0.000, round-trip
  FAIL). Exact-match is the wrong metric — likelihood accepts 81.5 % where top-1 accepts 63.0 %
  (18.5 pp). Survivorship-conditioned MEEA metrics. Baseline corrections verified byte-for-byte
  (MT 90.4 not 88.8; ReactionT5 journal ≠ preprint; RDKit-version flip 41/40 000). **Plus rektomar's
  FlowER findings above.**
- **SMILES→barrier failure modes** (corrected framing, see the block below): the multi-fragment
  embedding collapse (92.6 % of real reactant sides multi-fragment; naive ETKDG clashes <0.8 Å in
  98.4 % of them vs **0 %** single-fragment, n=800; the acetone+HCN case at 0.142 Å → 75 Ha endpoint
  gap), the unrelaxed-endpoint mechanism and its one-step fix, `NON_MONOTONIC_PATH` shown unsafe as a
  criterion (1 false positive in 4 on perfect geometries), balance (2.4 % of USPTO records atom-balanced,
  6/250; 10/11 planner steps unbalanced so xTB refused), stereochemistry-free input at 8.57 kcal/mol,
  the CO₂-expelling zwitterion, and mapper failure at **both** confidence tails (0.330 and 0.968).
  Plus the robust shortcut negative (Skala over LST, 225 × 2, MAE 47.72, +102 % bias).

> **CORRECTION 2026-08-26 to this same entry — I mis-stated the admissibility asset above and in the
> paper proposal that followed it.** I listed "**0/11 yielded a barrier** ⇒ the binding gate is
> elementary-step granularity" as a load-bearing gate. **That was retracted on 2026-07-30** by this
> file's own §PROBE and §MECHANISM FOUND AND FIXED blocks, and the 07-30 evidence audit records it as
> "positive control failed → cannot attribute to the inputs". The retraction stands: the run *measured
> our conversion step, not the chemistry*, the root cause was a collapsed multi-fragment embedding
> with unrelaxed endpoints, and it has a one-step fix (relax both endpoints at the NEB's own level
> before interpolating — arm E recovers a valid barrier on both failing cases). **The
> elementary-step-granularity claim remains unsupported by that evidence**, retaining only the
> independent and weaker Draslovka/Biltz lumping argument. `coordination/outbox.md` 2026-07-30 is
> **stale** on this point and should not be quoted.
>
> Consequence for the paper: its thesis cannot be "planner output is inadmissible to physics". The
> defensible thesis is the **constructive** one — SMILES→barrier is a pipeline of silent, quantified
> failure modes, most of which we diagnosed and fixed. That needs no chemistry-authority claim about
> mechanism, which is also the honest answer to the "do we need a domain authority" objection.

**Solid backbone, thin alone:** the oracle (0.84 at n=3), AIMNet2 on BH9 (449 rxn: 16.70 / 4.728 /
2.881), numerical settings closed at 0.047, ωB97M-V as above.

**One healthy method bet:** rektomar's any-subset conditioning — real baseline (85.4 top-1 at 5.7 M
params, 3.4 pp behind MT like-for-like), two components publishable independent of chemistry
(permutation-invariant likelihood over an exchangeable side; hard verifiable atom conservation).
Blocked on data completeness → **the completion layer, still unowned, now with one consumer rather
than three** — which makes it cheaper, not less necessary.

**One published claim of uncertain validity:** the L\* result (64.43 vs 61.86, 6/6, n=18 876/arm) is
in `briefing` and **G2, the seeding audit, is unowned**. DecisionBO's pseudo-replication trap
collapsed four of their results at p ≲ 0.003, one reversing sign. Correctness exposure, not housekeeping.

### The reading, and the recommendation

The tree's strongest, most finished, most defensible results are all **measurements of why the field's
standard evaluation practice does not work** — benchmark leaked, OOD axis inverted, round-trip
artifact-prone, exact-match wrong, planner output inadmissible to physics, baselines miscited, metrics
survivorship-conditioned and unseeded. Seven-plus findings, all measured, none needing a student or
more compute. Meanwhile every *method* bet has lost its mechanism (σ failed in all three leaves,
DecisionBO refuted the objective-side version, mechanism kernel null at route level).

So: **stop treating the evaluation findings as debris of failed method work and recognise them as the
contribution.** One paper written by the owner; one method bet (rektomar) actively protected by
resourcing the completion layer; everything else parked explicitly in writing.

**DSVR (`dominant-structural-variant-ranker`, tevang, MIT, cloned 2026-08-26): do not invest now.**
It addresses endpoint microstate quality — solvation, conformers, protomers, stereo — which only
starts to matter *after* the admissibility gate, and 0 of 11 real planner steps currently pass it.
Optimising past the binding constraint is the error `strategy-after-dft.md` warns about. **One
exception:** it is the natural constructive answer to the admissibility paper's endpoint-state gate,
so contributing the two regression cases (8.57 kcal/mol stereochemistry; the CO₂-expelling zwitterion)
and the AIMNet2 fragment-count finding is worth ~a day *as a by-product of writing the paper*. Hold
the correlation result back — as of 08-26 it is not merely unconfirmed but inverted. Assessment in
full: this node's chat record, to be folded into a `docs/` note if the collaboration proceeds.

### Gate before committing to the paper — IN FLIGHT

The leakage headline has one soundness hole. The 190 targets were **drawn from USPTO by
construction**, and standard practice holds out the target's own *reaction* while the molecule may
legitimately appear elsewhere. We scanned the full 1.94 M-row corpus, not a training split. So
"appears as a USPTO product" may be expected rather than scandalous — and `calculate_ood_190.py`/CLOVER
is **our own code**, so the broken label is an internal correction, not a published benchmark's defect.
The publishable claim is the leakage one, and it needs this settled.

**Split-independent test, job `11418664`** (`scripts/B2_multiplicity.py`): count **distinct** USPTO
reactions producing each target. Benchmark construction can hold out one reaction per target; it
cannot hold out reactions it never associated with the target. So k ≥ 2 ⇒ leaked under *any*
reaction-level split, with no need to know the split. k = 0 genuinely unseen, k = 1 consistent with
correct hold-out.

### RESULT — the leakage claim does NOT survive. The gate did its job.

COMPLETED, 1 939 253 rows rescanned; output `admissibility/out/multiplicity.csv`.

| stratum | n | k=0 | k=1 | **k≥2** | **k≥2 %** | median k | max k |
|---|---|---|---|---|---|---|---|
| in-distribution | 137 | 30 | 98 | 9 | **6.6 %** | 1 | 7 |
| close | 25 | 1 | 24 | 0 | **0.0 %** | 1 | 1 |
| far | 28 | 0 | 27 | 1 | **3.6 %** | 1 | 2 |
| **ALL** | 190 | 31 | **149** | **10** | **5.3 %** | 1 | 7 |

It reproduces B0 exactly — 159/190 = 83.7 % appear in USPTO — and then explains it away.
**78.4 % of the targets appear as a product exactly once.** That is precisely the signature of a
benchmark that held out each target's own reaction correctly. The split-independent leakage bound is
**5.3 %, ten targets**, not 83.7 %.

**Retracted, and it must not be repeated:**
- "**100 % of deep-OOD targets are verbatim USPTO products … the stratum labelled most novel is the
  most memorised**" — 27 of those 28 targets have **k = 1**, so their one producing reaction is
  consistent with correct hold-out. Appearing in the corpus is **not** memorisation, and we conflated
  them. The dramatic reading was wrong.
- The **inverted gradient** as evidence of anything. On the split-independent measure the strata are
  flat and tiny (6.6 / 0.0 / 3.6 %), and such order as there is runs the *ordinary* way, with
  in-distribution marginally more leaked. Nothing to explain.
- Joris's "ReactionT5 is robust to chemical novelty → it is 100 % memorisation" rebuttal. The
  contamination-shaped explanation for his 97 % is **not supported by this measurement**. His result
  needs a different explanation, or none; the ORD/USPTO ReactionT5 training-corpus overlap is a
  separate and still-live concern, but it is not established by target leakage.

**Survives, on its own reasoning and unaffected by this test:**
- The **label references the wrong corpus** — product-structure distance to ORD, while the planner
  learned USPTO *reactions*. That mismatch is conceptual, not empirical, and the strata remain void as
  a measure of novelty-relative-to-planner-knowledge. It is an **internal correction to our own
  code** (`calculate_ood_190.py`, CLOVER — ours), which is what it always was.
- Every fix option in `docs/ood-strata-invalid.md` §6, especially option 2 (novelty over *reactions*,
  not products) — this test independently shows product-level membership carries almost no signal.

**Consequence for the paper.** The benchmark-integrity spine loses its headline number, and with it
the claim that the field's standard hard-target benchmark is compromised. It is not. What remains in
that column is (i) rektomar's FlowER findings, which *are* about a published benchmark and are
externally valid, (ii) the metric findings (round-trip artifacts, exact-match 18.5 pp, survivorship
conditioning), and (iii) the byte-verified baseline corrections. **The paper should re-centre on
admissibility** — the planner-granularity/physics mismatch, which this test does not touch and which
remains the strongest owner-owned asset in the tree. See the paper discussion following this entry.

**Cost of the gate: one 8-minute CPU job.** It prevented writing a paper around a claim that would
not have survived the first referee who knows how USPTO-190 was built. Per ADR 0004 §"positive
control", this is the pattern to repeat: the cheap split-independent version of a dramatic claim,
before the claim is committed to.

## COMPLETION LAYER: MEASURED, AND IT IS AN ADOPT — NOT A BUILD (2026-08-26)

**Corrects the "highest-leverage unowned piece" framing** used at `synthesis.md:834`
("two customers and one spec"), `synthesis.md:940` ("still the only unowned piece, now with three
consumers") and `outbox.md` 2026-07-30 ("the single highest-leverage unowned piece of work in the
tree"). Those entries are superseded: **the piece is not unowned, it is unadopted.** An off-the-shelf
implementation has been in our own literature pool the whole time — `phan2024_synrbl`, cited in
`retro-physics-validation/literature/sota.md` as "a *prerequisite* for any energetics" — and a
benchmark with a violation-mode taxonomy landed in April 2026 (`phan2026_synrxn`, Sci. Data 13(1),
CC-BY: MNC 33 147, MOS 12 781, MBS 491, Complex 1748).

### Measured on OUR corpus, not theirs

`scripts/C1_synrbl.py`, SynRBL 1.0.6 in `admissibility/.venv-synrbl`, 2000 records sampled at stride
900 across all 1 939 253 rows of `uspto.csv`. **Balance verified independently of SynRBL**, by RDKit
element counting on both sides including implicit H, so the verdict does not rest on the tool's own
reporting.

| | n | % |
|---|---|---|
| balanced **as stored** | 35 / 2000 | **1.75 %** |
| unbalanced as stored | 1965 / 2000 | 98.25 % |
| SynRBL output balances (verified) | 1581 / 1965 | **80.46 %** of the unbalanced |
| SynRBL output still unbalanced | 384 / 1965 | 19.54 % |
| output unparseable / no output | 0 / 0 | — |

**Corpus balance 1.75 % → 80.80 %.** Solved by: MCS-based 1171, rule-based 410, unresolved 384.
Cost **35.5 ms/reaction** at `n_jobs=4` → **≈19 core-hours for the entire 1.94 M-record corpus.**

Two honest notes. (i) The 1.75 % baseline **reproduces** our own 2.4 % (6/250) figure within sampling
noise — that measurement was sound. (ii) **80.46 % is below SynRBL's published 89.83–99.75 % success
range**, and the likely reason is selection: their validation used "171,913 reactions with at most two
products that have balanced Reaxys records", a curated subset, where we sampled `uspto.csv`
indiscriminately. So on our data it works well but ~9–19 points worse than advertised — which is
exactly what "how well does it work in our case" was asked to find out.

### What this changes

1. **The completion layer is a ~19-core-hour batch job, not a research project.** Any proposal to
   build one must beat 80.8 % at 35 ms/reaction first.
2. **rektomar's blocker is removed.** His arbitrary-subset-conditioning miniproject was gated on
   corpus completeness measured at 2.4 %; it is 80.8 % for one overnight job. These two facts have sat
   in separate documents in this tree for a month.
3. **Stop quoting 2.4 % as a headline.** It is a *pre-repair* number and `phan2026_synrxn`'s taxonomy
   supersedes it. The interesting residue is the **19.54 % SynRBL cannot fix** — that, not the raw
   imbalance, is the real completion gap, and characterising it against SynRXN's MNC/MOS/MBS/Complex
   modes is the follow-up worth doing.
4. **The 07-30 "nothing in our stack bridges the two" claim is doubly retired** — already by the
   same-day PROBE retraction, and now by SynRBL for the balance half plus SCINE Chemoton (published
   "up to 80%") for the elementary-step half.

### Still open, and genuinely ours

Running SynRBL on **planner-proposed** reactions rather than database records. Not done, because the
route artifacts store *templates*, not concrete reaction SMILES (`top_routes` entries carry
`templates` + `n_rxn` + `feasibility`; 137/190 non-empty), so planner steps must be reconstructed by
template application before they can be tested. **The distinct risk to measure there: SynRBL was
validated on reactions that really happened. A planner proposes reactions that may not. A repair tool
that confidently balances a nonsense reaction is worse than one that fails on it** — and nothing in
its published evaluation covers that case.

## SynRBL ON REAL PLANNER OUTPUT (2026-08-26) — 92.9 % usable, and the 7.1 % residue has a signature

Follow-up to the entry above, and it answers the design question "plan first and fill the gaps later,
or make the planner emit complete reactions?". `scripts/C2_planner_synrbl.py` + `C3_suspect.py`.

**Reconstruction.** Route artifacts store *retro SMARTS templates*, not reaction SMILES, so steps had
to be rebuilt: frontier of molecules from the target, apply each template to whichever frontier
molecule it matches, record the forward step `precursors >> molecule`. Of 137 targets with routes,
**96 reconstructed fully**, 41 hit `template_no_match` partway (their partial steps are kept), giving
**316 unique planner steps**. Sampling caveat: a 70 % full-reconstruction rate could bias toward
simpler routes.

| | n | % |
|---|---|---|
| planner steps balanced **as emitted** | 4 / 316 | **1.27 %** |
| unbalanced as emitted | 312 / 316 | 98.73 % |
| **SynRBL output balances (verified independently)** | **308 / 312** | **98.72 %** |
| still unbalanced | 4 / 312 | 1.28 % |

**The predicted risk did not materialise — the opposite did.** I expected SynRBL to do *worse* on
proposed reactions than on database records. It does **much better**: 98.72 % vs **80.46 %** on raw
`uspto.csv`. The reason is that template-generated steps are *cleaner* than patent records — exactly
one product, a well-defined reaction centre, no OCR noise or odd multi-product stoichiometry — i.e.
close to SynRBL's own curated validation regime (≤2 products, Reaxys-backed).

**Where it does fail, it fails informatively.** 22 of 308 fixes — **7.14 %** — achieve balance by
inserting an **atomic radical**: `[H]` (38 instances) or `[O]` (10). Those are not valid energetics
inputs: DFT on a hydrogen atom is radical chemistry, not the polar reaction intended. And the
signature is chemically coherent rather than random — every case is a **redox step whose reagent the
planner never specified**:

- `Ar-Cl >> Ar-H` balanced as `+ [H].[H] >> + Cl` (real: hydrogenolysis / a hydride source)
- ester `>> ` primary alcohol balanced as `+ [H]×4` (real: LiAlH₄ or DIBAL)
- sulfide `>>` sulfone with mCPBA balanced as `+ [O]` (real: **two** equivalents of peracid — so this
  is a *stoichiometry* failure papered over with atomic oxygen)

So: **SynRBL cannot balance a redox step without the redox reagent, and it silently substitutes an
atomic species instead of failing.** That is precisely the "launders an implausible step into a
well-formed one" hazard, and it is confined to a recognisable 7 %.

**286 / 308 = 92.86 % of fixes are clean and directly usable as energetics input.**

### The consequence, and it settles the design question

**Fill-later wins for the physics path.** A two-line filter — reject any step whose balancing added an
atomic species — costs microseconds, retains 92.9 %, and flags exactly the steps that need reagent
identification rather than balancing. That filter *is* the cheap admissibility pre-check this tree has
wanted since the 81-minutes-of-DFT-on-invalid-input episode, and it now exists as a criterion.

**Planner-side completeness is not justified by planning cost, and is not refuted by it either.** The
corpus is completed **once, offline** (≈19 core-hours for 1.94 M records); inference emits complete
reactions because that is what was trained, so there is **no per-node cost in the search**. The
argument for it was never load — it is that (i) a likelihood over incomplete reactions is not a
feasibility signal, and (ii) conservation becomes structural rather than learned, where
`retro-generation`'s own FlowER reproduction measured **0 non-conserving predictions in 5 184 064
samples** against 17.2–33.0 % for G2S/MT on the *same balanced corpus*.

**Recommendation: both, in this order.** (1) Adopt SynRBL + the atomic-species filter now as the
physics-arm gate — it is measured, cheap, and unblocks the oracle input path today. (2) Use SynRBL to
manufacture the complete-reaction corpus for `retro-generation`, **filtering the 7.14 % first**, since
training on `[H]`/`[O]` as reagents would teach a generative model that atomic radicals are ordinary
species. The 7 % residue — redox steps missing their reagent — is the honest open problem, and it is
*reagent identification*, not balancing.

## THREE-ARM RERUN + THE GATE IS BUILT (2026-08-26)

**Rerun** (`admissibility/scripts/C4_allarms.py`, job `11419180`, 55 s). The single-arm numbers in the
entry above were drawn from `gp` only at a 70 % reconstruction rate; repeated across all three
feasibility-model arms they hold.

| | single arm (316 steps) | **pooled, 3 arms (728 steps)** |
|---|---|---|
| balanced as emitted | 1.27 % | **0.96 %** (7/728) |
| SynRBL repairs | 98.72 % | **98.06 %** (707/721) |
| repairs via an atomic radical | 7.14 % | **6.79 %** (48/707); `[H]`×70, `[O]`×25 |
| clean, energetics-ready | 92.86 % | **93.21 %** (659/707) |

Reconstruction per arm: gp 96/137 targets full, independent 85/133, mechanism-gp 96/141 — so 64–70 %,
and the bias is now visible rather than assumed: route **depth** distribution is mode 3 with 4–7 well
represented (gp `{2:5, 3:93, 4:27, 5:8, 6:4}`), so the sample is not only shallow routes. Still, the
30–36 % that hit `template_no_match` are unmeasured and could be systematically harder.

**Built:** `retrosyntesis/src/completion/` (`c7e29ee`) — `element_counts`, `is_balanced`,
`added_species`, a `Verdict` taxonomy with an `admissible` property, and `gate` / `gate_batch`.
Placed **outside `validation/` deliberately**: two consumers, so per this file's own 2026-07-31 rule
it must not travel with numerics at handover. Balance is verified by independent element counting and
never from SynRBL's own report, so the gate can contradict it. SynRBL is imported lazily — balance
checking and the filter work without it installed. **27 tests, pure RDKit, no quantum chemistry**,
passing in the cluster venv including the SynRBL paths.

The verdicts a caller branches on: `BALANCED_AS_GIVEN` and `REPAIRED` are admissible;
`REPAIRED_WITH_ATOMIC_SPECIES` (the 6.79 %), `UNREPAIRED` (1.94 %) and `UNPARSEABLE` are not.

**Unpushed.** `retrosyntesis` is declared external in `AGENTS.md` ("inventory + coordination only")
even though the owner intends to take it as the shared integration node. Committing code there is a
change of posture and the push is the owner's call.

## CONCEDED 2026-08-27 — the SynRBL-corpus idea IS dataset curation, and it was already done and released

Owner's objection: "if we complement existing databases using Phan, don't we do just dataset
curation? Isn't this a common job that is done?" **Correct, and it is worse than that.** The
rebalanced corpora are already published, and **`retro-generation` established this on 2026-08-04** —
three weeks before yesterday's recommendation — in `reviews/complete-reactions_data-and-models.md`,
which is **on the cluster and unpushed**, so it was invisible to `git log`.

His bottom line, quoted:

> "**So completeness is *constructed* — and someone already did it, at scale, and released it. The
> brief's 2.4 % balance figure describes *raw* USPTO, not the available data. This is the most
> consequential finding for M0.**"

What already exists, from his review:
- **FlowER**: 250,782 / 2,801 / 28,049 overall reactions → **1,445,189 / 15,744 / 162,002 elementary
  steps**, conserving heavy atoms, protons and electrons *by construction*, Figshare + MIT.
- **SynRXN `_B`**: **445,115 / 50,000 / 50,016** SynRBL-rebalanced reactions, `Complete = Yes`,
  CC-BY 4.0 — "packaged as *classification* benchmarks, which is why reaction prediction hasn't
  noticed them."
- Plus mech-USPTO-31k, PMechDB, RMechDB, ReactMech (29,604 mechanisms / 104,964 steps).
- And his caveat on the SynRXN rebalancing sets I cited yesterday: they are **evaluation only**,
  "explicitly not intended for model training". The `_B` sets are the trainable ones.

### Two corrections to what this node recorded yesterday

**(i) "SynRBL removes rektomar's 2.4 % blocker" was wrong twice.** There was no blocker — complete
data exists at ~10⁶ scale — and the specific remedy proposed (run SynRBL over USPTO ourselves)
duplicates a released CC-BY corpus. Retract the framing in the 2026-08-26 entries. The 2.4 % figure
describes raw USPTO and should never again be quoted as a constraint on the generative track.

**(ii) I mis-described SynRBL's headline evaluation.** I attributed the gap between its published
89.83–99.75 % and our measured 80.46 % on raw `uspto.csv` to a "curated ≤2-product Reaxys subset".
Read from the PDF, the larger factor is that the 171,913-reaction Reaxys test set is **artificially
unbalanced**: "We artificially made these data unbalanced by removing the smaller product molecule in
reactions with two products. In addition, all non-carbon compounds are removed from both sides."
So the headline is largely *can SynRBL put back a species we deliberately deleted*, with the answer
known by construction. Real records are unbalanced for messier reasons, which explains our 80 % far
better than my earlier guess. (A separate `5420` appears in its confidence-estimation table.) This
also sharpens rektomar's caveat that SynRXN's "balance provenance is SynRBL + the SynCat release, not
manual review at scale."

### What survives

**Not the corpus work.** Adopt `SynRXN _B` or FlowER's set; do not rebuild either.

**The gate does, but modestly and for a different reason.** `retrosyntesis/src/completion/` filters
*proposed* reactions at the point of physics gating — novel model output that no dataset contains — so
it is a runtime admissibility check, not curation. The 6.79 %-atomic-radical finding is about what a
repair tool does to chemistry that may not be real, which no curation paper measures. That is a small
engineering contribution, not a research result, and it should be described as such.

**The real niche is unchanged and is NOT a data-curation task.** From his §1.6: "**None models a
distribution over a complete reaction with an arbitrary conditioning set**", and "**no corpus carries
conditions *and* atom balance**". He explains why the intersection is empty *structurally*:
"Conditions live in the patent/ELN record; balance lives in mechanistic corpora built by applying
templates to reactants — and those pipelines *discard* the condition metadata." Constructing that
intersection is genuinely unoccupied work; re-running SynRBL is not.

**And he has already priced the architecture question.** Trained on >1 M balanced steps, SMILES
seq2seq models conserve heavy atoms in only **27.7–39.1 %** of predictions and mass+protons+electrons
in **17.2–33.0 %** — so "balance is *not* learnable from balanced data by our architecture family."
That is the strongest available argument for structural conservation, and it is his, measured, from
the paper's own numbers.

### Process finding — third incident today

Unpushed cluster-side work has now cost this node three times in one day: rektomar's outbox (FlowER
reproduction), this review, and the resulting bad recommendation. `AGENTS.md`'s standing instruction
to check working trees covers *submodules*; these are **externals**, whose cluster working directories
are not checked at all. The `/coord status` recipe should add: for externals with RCI allocations, list
`/mnt/data/resynthesis/<node>/` and diff against `origin/main`. Cheap, and it would have caught all
three.

## SynRXN `_b` CARRIES SynRBL-INSERTED ATOMIC RADICALS (2026-08-27) — measured on the published corpus

Follow-up to the concession above, and the one thing this node has that `retro-generation`'s M0 review
does not. His caveat was that SynRXN's "balance provenance is SynRBL + the SynCat release, not manual
review at scale". Quantified, on the shipped corpora (SynRXN v1.2.1, Zenodo
`10.5281/zenodo.22045145`; `admissibility/scripts/C5_synrxn_scan.py`):

| corpus | reactions | contain `[H]`/`[O]` as a component | instances | attributed to rebalancing |
|---|---|---|---|---|
| **`uspto_50k_b`** | 50 016 | **6 270 — 12.54 %** | `[H]` 14 243 · `[O]` 620 | **6270 / 6270** |
| `schneider_b` | 50 000 | **2 463 — 4.93 %** | `[O]` 2 294 · `[H]` 693 | **2463 / 2463** |
| `tpl_b` | 445 115 | **9 505 — 2.14 %** | `[O]` 9 616 · `[H]` 2 346 | **9505 / 9505** |

Attribution is by paired `_b` vs `_u` diff on `r_id`: **`already_in_source` = 0 in all three corpora**,
so every occurrence was introduced by the rebalancing rather than inherited. They land overwhelmingly
on the **LHS** (14 688 vs 175 in `uspto_50k_b`) — inserted *as reagents*. Mechanism matches our planner
finding exactly: redox steps whose reagent the record never specified (`USPTO_8` ketone→alcohol via
`[H].[H]`; `sch_15` oxidative cyanamide via `[O]`).

**Why it is worth reporting.** A generative model trained on `uspto_50k_b` learns that atomic hydrogen
is a purchasable reagent in **one reaction in eight**, and **no conservation metric reveals it** because
those reactions are balanced — a constraint-satisfaction check passes them. Contamination is **worst in
`uspto_50k`**, the field's most-used retrosynthesis benchmark, and mildest in `tpl`.

This **generalises our own 6.79 % planner-step number** from an internal observation to a property of a
published, CC-BY corpus that other groups train on — the first result in this thread that is about
someone else's artifact rather than our own pipeline. Sent to `retro-generation` (`fb916bc` in that
repo) with the filter and the reproduction script.

*(Housekeeping: this entry was first appended to `retro-generation/coordination/synthesis.md` by a
`cd` error and reverted there — `8050085`. A leaf must not carry a `synthesis.md`; it is an
orchestrator artifact.)*

## (C) MEASURED 2026-08-27 — the proposer's error is INDEPENDENT along a route, so accuracy is back

**This reverses the 2026-08-26 reading of the barrier-accuracy result, and the reversal was earned by
one cheap experiment on data we already had.** Owner's question did it: DFT error structure cannot
matter because DFT is not in the planning loop — but the *proposer* is, on every node, and nobody had
measured its error structure.

### Three correlation objects, previously conflated

`retro-pfn/path-correlation/README.md` already distinguished two; the third was missing.

- **(A) similarity correlation of feasibility** — what retro-fallback's latent-GP ξ_f models
  (`_reaction_similarity_kernel` over Morgan FPs, `K(r,r)=1`, `noise_var=1e-6`; marginal hand-set at
  0.5 constant or 0.75 decaying with template rank). **Assumed, never fitted.**
- **(B) path dependence of feasibility** — deflated 2026-06-11 to "the shadow of unrecorded reaction
  conditions". **Stays parked**; its criteria have not been met.
- **(C) correlation of ESTIMATOR ERROR along a route** — the ρ that
  `docs/barrier-accuracy-requirement.md` sweeps. **Never measured. Now measured.**

**(A) does not deliver (C):** steps within a route are dissimilar transformations, so a similarity
kernel correlates *competing alternatives at one node*, not a route's own successive steps.

### The result — ICC ≈ 0.05

Job `11422415`, 2000 PaRoutes n1 reference routes / **5757 recorded steps** (patent-extracted, so every
step is known-feasible by construction — no new ground truth needed), scored with AiZynthFinder's USPTO
expansion policy, the same template classifier retro-fallback builds ξ_f on.

| error definition | ICC over routes | within/between mean \|Δ\| |
|---|---|---|
| surprisal −log p | **0.0477** | 0.9717 |
| log rank | **0.0389** | 0.9818 |
| miss (binary) | **0.0229** | 0.9641 |
| surprisal, found-only | **0.0548** | — |

Within-route step pairs differ by **97–98 %** as much as random cross-route pairs. Censoring is not
driving it. Error is flat in depth (2.703 → 2.205 over depths 0–4), so there is no route-level
"hard route" factor for error to load onto.

### Consequence — accuracy is the binding axis after all

Reading the correct column of the perturbation table at w = 20:

| | 0.84 | 3.80 | 4.73 | 16.70 |
|---|---|---|---|---|
| **ρ = 0 — measured** | **14.4 %** | **40.0 %** | **46.8 %** | **85.0 %** |
| ρ = 1 — assumed on 08-26 | 5.6 % | 5.4 % | 5.8 % | 8.3 % |

A 20× accuracy improvement buys **85.0 % → 14.4 %**. So *"error structure dominates magnitude, do not
chase MAE"* was **conditional on ρ**, and ρ ≈ 0. **Withdraw it for the in-loop estimator.** What
survives from that entry is narrower and still true: within a *reaction family* a functional's error
can be one-signed (PBE0 on 3 pericyclics), but a route mixes families, so that structure does not
propagate to route ranking. `docs/barrier-accuracy-requirement.md` item 1 ("do not build active
learning to reduce barrier error yet") rested on the same assumption and needs re-deriving.

### And it answers the retro-fallback question

Tripp 2024 §6.2, verbatim: retro-fallback's advantage is *"particularly large for the feasibility
models with no correlations between reactions"*, because *"when GP-induced correlations are introduced,
these backup plans disappear … since similar reactions will likely both be feasible or both be
infeasible."* So **GP-ξ_f is not better, it is a different regime** — (A)-correlation destroys the value
of hedging, which is retro-fallback's whole contribution. The correlation structure of ξ_f is the
*problem property* that decides which planning approximation binds: the `sim2science` thesis
instantiated on retrosynthesis, and a candidate answer to that project's conceded HIGH-severity gap
("no real simulator, no native noise").

### Two by-products worth keeping

**AZF USPTO single-step recall on PaRoutes reference steps** — a baseline this tree lacked:
**55.95 % @1**, 76.22 @5, 79.71 @10, **82.65 @50**, **17.35 % miss**, median rank 1 when found.

**A representability bound the tree has never stated:** only **1202/2000 = 60.10 %** of reference
routes have *every* recorded step inside the policy's top-50. For the other 40 % the reference route is
not reachable by *any* search over this policy at k=50. That is a different failure from the
budget-exhaustion finding that seeded `retro-planning`, and it caps what better search can buy.

**Next:** repeat over LocalRetro / Chemformer / ReactionT5 — all already wired into the harness. If all
four give ICC ≈ 0, (C) ≈ 0 is a property of the task and the accuracy axis is settled; if they differ,
(C) becomes a model-selection criterion.

## (C) CONFIRMED MODEL-INDEPENDENT 2026-08-28 — the accuracy axis is settled

Second proposer, paired on the identical 2000 routes / 5757 steps (job `11422605`, 2h56m):
**ReactionT5v2 fine-tuned on USPTO_50k**, a template-**free** seq2seq — the maximally different
architecture from AZF's template classifier, and matched in strength deliberately (the ORD-only base
scores 13.8 % top-1 on USPTO_50k and would not have been a fair contrast; the fine-tuned variant
reports 71.2 %).

| | AZF (template classifier) | ReactionT5 (seq2seq) |
|---|---|---|
| recall@1 | 55.95 % | **61.30 %** |
| recall@5 | 76.22 % | 76.06 % |
| **recall@20** | **81.43 %** | **81.33 %** |
| **ICC, log rank** | **0.0421** | **0.0530** |
| **ICC, miss** | **0.0323** | **0.0413** |

Two unrelated architectures, different training corpora, **within 0.1 pp on recall@20** and both
**ICC ≈ 0.04–0.05**. Variance components rule out a ceiling artifact (ReactionT5 log-rank MSB 2.2937
vs MSW 1.9757 — ample error variance, almost none of it between routes).

**So (C) ≈ 0 is a property of the task, not of a model class.** The ρ = 0 column of
`docs/barrier-accuracy-requirement.md` applies unconditionally, and the 2026-08-26 reading ("error
structure dominates magnitude, do not chase MAE") is **withdrawn** for the in-loop estimator rather
than merely doubted. Accuracy is the binding axis, and at w = 20 the span it controls is
**14.4 % → 85.0 %** top-1 flip.

**The sharper finding, from the paired cross-model comparison** (n = 5757): Pearson **r = 0.3500** on
log-rank error; **433 steps (7.52 %) missed by both** at k=20 against **3.47 % expected under
independence — 2.17× enrichment**; 29.72 % missed by at least one. Stated as the result:

> **Per-step difficulty is real and partly model-independent, but it does not aggregate into a
> route-level factor.**

That is exactly the condition under which a route's feasibility product accumulates independent
errors. The ρ = 0 conclusion now follows from measurement rather than assumption.

**Three consequences beyond the ρ question.**

1. **`docs/barrier-accuracy-requirement.md` item 1 is now actively wrong**, not just unsupported. It
   says "do not build active learning to reduce barrier error yet" because accuracy is second-order.
   Under ρ ≈ 0 accuracy is first-order. The item needs rewriting, and the active-acquisition programme
   — this orchestrator's organising thesis — is *rehabilitated* on its original terms.
2. **Disagreement is now a measured signal, not a rhetorical device.** r = 0.35 means the two models
   disagree on ~65 % of the error variance. `Draslovka/slides` justifies escalation by "tools
   disagreeing with each other" precisely to avoid a calibration claim we could not support; that
   argument now has a number behind it.
3. **A representability floor:** 7.52 % of recorded steps sit outside top-20 for *both* architectures.
   Combined with the 08-27 route-level bound (only 60.10 % of reference routes have every step inside
   top-50 for AZF), the ceiling on this model class is structural and independent of search budget —
   a different failure from the budget-exhaustion finding that seeded `retro-planning`.

**Not run:** LocalRetro and Chemformer need the vendored `RetroCrosstalk` repo, its checkpoints and
their own dependency stacks (DGL pins; a lightning stack). Deprioritised rather than blocked — with two
maximally different architectures already agreeing to 0.1 pp, a third template-ish and a second seq2seq
model would add little. Full record: `retro-pfn/path-correlation/README.md` (`ced0604`).

## OPEN PROBLEM 2026-09-06 — single-step accuracy does not buy search progress; proposals must SHRINK the target

**Status: open, and it is the sharpest mechanistic lead we have on the proposer side.**
Measured while running the Němec MU1700 demo (`Nemec/report/`, RCI
`/mnt/data/resynthesis/NemecChallenge/`). Recorded here because it is cross-cutting:
it constrains `retro-generation`'s generative track, `retro-planning`'s search side, and
any future decision to swap a proposer into the K-P-V harness.

### The measurement

`size_ratio = (largest precursor heavy atoms) / (target heavy atoms)`, over 24 targets
(the Němec five plus benchmark targets), 10 proposals each:

| proposer | n | median | mean | **proposals that GROW the molecule** |
|---|---|---|---|---|
| **ReactionT5v2**-retrosynthesis-USPTO_50k | 180 | 1.11 | 1.34 | **74 %** |
| **AiZynthFinder** uspto template policy | 166 | 1.00 | 0.99 | **36 %** |

On MU1700 specifically (31 heavy atoms): AZF's median precursor is **20** heavy atoms,
ReactionT5's is **39** — *larger than the target*. Its top proposal is MU1700 plus a Boc
group plus an iodine: a sensible reaction step, and a retrosynthetic move in the wrong
direction. Script: `scripts/size_ratio.py`.

### Why it matters

ReactionT5 is **not a weak model** — rektomar reproduced its forward direction at 92.60
top-1 against 92.8 reported, and the retro checkpoint reports ~71 % top-1 on USPTO-50k.
Yet in search it explored **806 k nodes to yield 26 routes**, where AiZynthFinder yielded
**867**. The proposals are chemically good (its Boc protection is better practice than the
ethyl carbamate AZF chose); they simply do not reduce the problem, so the search cannot
converge.

This is a **concrete mechanism for a documented phenomenon**: `hassen2022_retrosynthesis-gap`
and `torrenperaire2024_models-matter` established that single-step top-k does not predict
multi-step solvability, without explaining it. Here is one reason on real targets — a 71 %
single-step model proposes steps that grow the molecule 74 % of the time. It sits alongside
this tree's own (C) result (proposer error is per-reaction, not per-route): both say
**single-step metrics measure the wrong thing for planning**.

Note also the asymmetry in inductive bias: the template stack ships a dedicated
**`ringbreaker`** policy precisely because ring-construction disconnections are
under-proposed. A seq2seq proposer has no equivalent correction, and correspondingly almost
never proposes building a ring system (measured: 0–1 ring-forming proposals per 25 beams on
MU1700 and its intermediates, versus rank 3 / prior 0.045 for AZF's ringbreaker).

### What is open

1. **Does `size_ratio` predict solvability?** We have shown the distributions differ; we have
   *not* correlated it with solve outcomes. That needs searches over a target set with
   recorded solve/no-solve, and it is the experiment that turns this from an observation into
   a usable filter.
2. **Acceptance filter, generation control, or search prior? — partly answered 2026-09-14.**
   Rejecting growing proposals outright is crude: protection steps are legitimately
   size-increasing. Of the three places the signal could live, a `/lit` survey
   ([[sota/control-tokens-in-reaction-generation]]) settles two of them:
   - **Generation-side conditioning is crowded prior art.** `thakkar2023_disconnection-prompts`
     prompts the single-step model with the disconnection *site* (+39 % accuracy, 2× class
     diversity); `westerlund2025_human-guided-prompting` puts bond constraints into
     AiZynthFinder via a broken-bonds score and multi-objective MCTS (75.57 % vs 54.80 % on
     PaRoutes); `sathyanarayana2026_protect-steerable-retrosynthesis` constrains generation
     symbolically by protecting group. Two of the three are by the groups whose tools we run.
   - **The value function / cost-to-go is untouched by all of them.** None puts disconnection
     information into a learned `h`. That is the opening, if there is one.

   **Why `h` is the better organ than generation.** `size_ratio` is a *progress* measure — did
   this step move toward purchasable material — which is definitionally what a cost-to-go
   estimates. Using it as a generation filter mistakes the organ. This also routes the idea to
   **`retro-planning`** (which owns `h`; `retro-pfn` owns ξ_f edge costs), not to
   `retro-generation`, and lands on retro-planning's own binding constraint: the 190-hard wall is
   search guidance, every rejection `ERROR_TYPE_5_INCOMPLETE`, zero feasibility-driven.

   **The gate that must pass first, and it could kill this outright.** The incumbent `h` is
   **SAScore**, which is already complexity- and size-flavoured. If our signal merely re-derives
   it, the feature buys nothing — correlate the disconnection/size features against SAScore before
   any training. The argument that it is *not* redundant: SAScore scores a **molecule** (how hard
   to make), ours scores a **step** (did this reduce the problem). Two nodes of identical SAScore,
   one reached by a reducing step and one by a growing step, are indistinguishable to SAScore and
   different in trajectory. Untested.

   **Status: hypothesis, not a bet.** Recorded so the survey result is not re-derived; not
   resourced, and it should not become a method bet before the SAScore gate runs.
3. **Would it fix a generative proposer?** If yes, it is a cheap correction to bolt onto
   `retro-generation`'s models. If it merely reflects that templates are extracted from real
   reactions and inherently reducing, then the gap is architectural and not filterable.
4. **Caveats before anyone quotes this.** 24 targets; the proxy uses only the largest
   precursor; our ReactionT5 wrapper is homemade (no official syntheseus integration) and its
   mass/echo filter rejects ~40 % of beams, so part of the gap may be our harness rather than
   the model.

## PRIOR ART WE WERE HALF-USING (2026-09-07) — Badowski 2019 already solved diverse route selection

Němec sent us `badowski2019_cost-effective-diverse-pathways` (Chem. Sci. 2019, 10(17),
4640–4651, DOI 10.1039/C8SC05611K, CC-BY-NC; now pooled in `~/agents/library/`). Checking
our awareness of it produced an uncomfortable answer worth recording.

**We were using half of it without knowing.** AiZynthFinder's `RouteCostScorer` docstring
reads verbatim *"From Badowski et al. Chem Sci. 2019, 10, 4640"* — so every `route_cost`
number in the MU1700 work comes from this paper, and the name "Badowski-style cost" entered
our notes from the code rather than from the paper.

**The half we did not have is the half we were working on.** Its second contribution is
diverse route selection by **penalising, during extraction, every reaction sharing the same
product and non-trivial (≥4 C) substrates as the pathway just returned** — then
recomputing costs by modified Dijkstra and taking the next-cheapest path. Their motivating
example is our chemist's complaint verbatim: *"changing an aryl bromide to an iodide"* gives
formally different pathways that are equivalent to a chemist. 2019. Not in AiZynthFinder
(no "diversity"/"penalty" anywhere in `aizynthfinder.context.scoring`), and not in this
pool until today.

**Architectural difference, and theirs is better for the purpose.** We enumerate all routes
then cluster (TED, intermediate-Tanimoto, our disconnection descriptor); they never surface
near-duplicates, because the penalty is inside the objective the extraction optimises. Their
cost: ~0.5 s for 100 pathways on a 12 k-node solution graph.

**Consequences.**
1. **Do not present penalty-based diverse selection as novel.** Our route-diversity metrics
   answer a different question — how far apart two *given* routes are — which is what
   located route 368 against the chemist's published route, and that use stands.
2. The untried and obvious thing: add a Badowski-style penalty to our own extraction so
   routes come out pre-diversified rather than clustered afterwards.
3. **Lesson beyond this paper:** we adopted a scorer from a docstring without reading its
   source. Worth checking what else in the 20 AZF scorers we are using citation-blind.

## PULLED FROM retro-generation 2026-09-15 — STAGE 1 KILLS M2, AND IT REVERSES THE 08-26 "BLOCKER REMOVED" CALL

`outbox.md` 2026-09-11 + `inbox.md` 2026-09-13 (rektomar's stage-1 completion measurement, answered).
Full numbers in `retro-generation/src/rxn_balance/README.md` and
`results/rxn_balance/metrics_stage1.json`. This is the M0 data-assessment result the miniproject
(`MINIPROJECT-conditioning.md` §7) said would gate M2, and it closes M2 with a measured "no."

### The measurement

On the matched USPTO_50k / USPTO_50k_B pair (50,016 records, same reactions, same split — only
the added species differ), classifying what completion actually adds:

| | USPTO_50k_B |
|---|---|
| records where `_u` already covers the product's heavy atoms (spectators/byproducts only) | 48,846 |
| records where completion **fills a genuine LHS deficit** | **0** |
| records where completion edits an original `_u` molecule | 0 |
| LHS additions, by element | O, I, N, F — **no carbon, ever** |
| RHS additions, by element | C, O, Cl, Br, B, I, F, N, S, Si, Mg, Sn, P, Zn, Cu |

**Completion never supplies a missing building block and never touches an original molecule, in
any of 50,016 records.** What looks like added chemistry on the RHS (carbon, halides, boron) is the
leaving/protecting-group fragment of a reactant already present in `_u` (Cbz removal → the LHS
already had the carbamate; ester hydrolysis → the LHS already had the ester) — SynRBL is completing
the *product side of an equation whose reactants already contain the answer*, not discovering a
missing reagent. The LHS gains only water, protons, iodide and (620 records) atomic oxygen — bookkeeping,
not chemistry. Purchasability follow-through, on the full precursor set: **zero records, pre- or
post-gating, transition from not-fully-purchasable to purchasable** — there is no `N->Y` cell in
either table, so "saves a route" is literally 0/50,016. 94 records (pre-gating) transition the other
way, purchasable → **not** purchasable, i.e. completion made the precursor set worse; all 94 sit
inside the 6,270 radical-contaminated records and vanish once those are gated — so even that harm is
a SynRBL-artefact effect, not a real one. `saves_a_route_examples` is an empty list, pre and post.

### The decision — M2 does not run

Per `MINIPROJECT-conditioning.md` §7 ("a well-argued no closes M2"): rektomar recommended stopping,
Chemie approved (`inbox.md` 2026-09-13) — 0 `deficit_filled` records means completion cannot change
*which building blocks a route needs*, so it cannot save a route, full stop. Two open stage-1 items
(coherent-class characterisation, hand-judging) are now moot: the (b)/(c) case sets are empty, so
there is nothing left to characterise. Separately settled: ion-spelling in `_b` merges to the neutral
molecule (option 2 — `[H+].[Cl-]` → `Cl`, only for ions SynRBL itself added), and the 07-27 DOI
(`…22045145`) is corrected to the manifest's `10.5281/zenodo.17297258`.

### This reverses, not confirms, the 2026-08-26 "COMPLETION LAYER... blocker removed" call

`synthesis.md:1506` ("COMPLETION LAYER: MEASURED, AND IT IS AN ADOPT — NOT A BUILD") measured SynRBL
lifting **balance rate** 1.75 % → 80.8 % and concluded from that alone: "rektomar's blocker is
removed... these two facts have sat in separate documents in this tree for a month." That equated
*balances* with *supplies what a corpus of complete reactions needs*, and stage 1 shows those are
different measurements — a record can go from unbalanced to balanced by adding a proton and a water
molecule, which is arithmetic, not the missing reagent a training corpus or a route needs. The 08-26
entry should be read as **superseded on this point**, not merely extended: there was no
missing-building-block blocker for SynRBL to remove, because SynRBL doesn't add building blocks.

**This also reopens the "one component, two/three consumers" convergence claim**
(`synthesis.md:834`, `:940`) rather than settling it. rektomar's own read (`inbox.md` 2026-09-13):
*"rebalanced corpora are not a source of balanced overall reactions for the physics track either —
the balance is water, protons and atomic H, not recovered chemistry."* If that holds, the completion
layer solves neither consumer's real need — M2 needed real precursor sets, the physics track needs a
real elementary step for a TS build, and generic atom-count balancing supplies neither. **FlowER's
elementary steps remain the only real source of balanced complete reactions**, which is consistent
with — and now doubly confirms — the 2026-09-04 finding above (FlowER 250,782 reactions
→ 1,445,189 balanced steps). Whoever owns the numerics/completion handover (still nominally unowned,
see `:948`) should be told directly: stop treating SynRBL-class rebalancing as a path to trainable
complete-reaction data for **either** consumer.

### What's still open on the miniproject

M0's other half (prior-art novelty check) already passed in the 09-04 outbox entries (no corpus
carries both `c` and atom balance; SynBridge/T5Chem are the nearest single-model precedents). With
M2 killed and M0 otherwise clear, the live question is **M1** — the cost-of-generality probe on the
corpus *as it stands* (no completion), at the multi-rung capacity sweep the miniproject's §5 Q1
note demands. No stage-1/M1 result has landed yet for that; nothing in `results/` or `runs/` beyond
the balance-completion measurement above post-dates this pull.

## MILAN ENROLLED, AND THE ENERGY QUESTION GETS A HOME (2026-09-25)

**Enrolment.** `Milan/` is now an owner-operated leaf (ADR 0001 there). The folder had been wholly
gitignored and absent from the inventory: plan, RESULTS, four handovers, two problem framings and
~40 analysis/experiment scripts were unversioned. Split: his code checkout and his Overleaf are a
`collaborator` external and a `paper, flow: in` boundary, never written into; everything else is
ours and tracked. **His GitHub repo was renamed `mlnpapez/MechReact`** (old URL redirects); it is
two commits ahead of our checkout, one "corrected radical moves" (2026-09-24) that touches the
chemistry and the AFM model and is likely his answer to our `bug_radical_moves.md`. Pull and diff
against our `fix/radical-moves` before any new AFM run.

**The energy question, placed.** Discussion of "generate the reaction together with its energy":
the prerequisite is a representation on which energy is a function of what the generator emits.
ΔE is a state function and telescopes over intermediates and routes; a barrier is not and needs a
transition object or a learned transformation-level model. Energy is defined only at Sector states
(step boundaries), not per arrow — Milan's stability check already showed book-keeping states
minimise *lower* than real molecules. AIMNet2 needs coordinates, so it is an oracle we call after
embedding, not a representation for AFM; the AFM-compatible object is a per-state head distilled
from it. Prior art: RMG (enumerate on 2D, price by group additivity + rate rules) is the direct,
never-generative precedent; CGR/Chemprop barrier models, TS generators (OA-ReactDiff, React-OT,
TSDiff) and YARP/Chemoton are the pieces; nobody trains a mechanism generator that carries a
per-intermediate energy. Ladder for *ranking*: distilled 2D ΔE/barrier heads (ms, 2–5 kcal/mol,
in-family) → MLIP ΔE after embedding (s, ~2) → MLIP/generated-TS barrier (min) → DFT NEB (our
measured rung, Spearman 0.90) → ωB97M-V/DLPNO. Route-level ranking needs kinetics near the top
rung on the rate-limiting step (perturbation table, ρ≈0); reaction-level ranking inside AFM's
admissible sets is reachable at the cheap rungs.

**Home: `retro-pfn/flow-ts/`, reactivated by its own falsification probe** — the charter reads
"TS geometry + path + energy profile, FlowER-style + energy-aware; reactivate via falsification
probe", and retro-pfn's placement rule already says an MLIP is a tool we call (ADR 0002) and a
scalar feasibility output goes to `xif/`. The probe: on AFM's admissible candidate sets, is the
recorded mechanism the lowest-energy path under AIMNet2 at Sector states? `Milan/` supplies
candidates, checkpoints and reconstruction code; `retro-physics-validation` runs the MLIP rung
(task via its inbox). Not Milan's folder (his paper, our question), not a new node (retro-pfn's
promotion rule covers that case if the tether to ξ_f is lost). Next: retro-pfn ADR reactivating
`flow-ts/`, then the experiment brief (which states get energies is the design decision).

**Same day, later — stage 1 built and run to the oracle step.** retro-pfn `flow-ts/BRIEF-stage1.md`
+ `stage1/`. Candidates for both checkpoints (433 held-out RMechDB steps, 100 chains, ~1–3 min
CPU), 4,559 unique components embedded, every step routes to `aimnet2-nse` (general AIMNet2 is
closed-shell: 25.5 kcal/mol on BH9's open-shell classes vs 3.9 for NSE, Jindřich's August probe).
Oracle run and a 200-component ωB97M-V calibration (route vs wrong-candidate pools) delivered to
`retro-physics-validation`'s inbox; the 2.2 MB handover tarball is local, not yet transferred.
**Methodological finding, before any energy exists:** with random component energies the
worst-intermediate profile ranks the chemist's route first in **54 %** of informative steps —
the chemist's route is usually the shortest and a max over fewer states is smaller. Chance is
33 %, the model's own frequency ranking 70 %. So stage 1 passes only above 54 %, and matters only
against 70 %. On fine-tuning AIMNet2 to the AFM subset: nothing to fine-tune on (RMechDB has no
energies); if DFT labels are computed for calibration they are the better oracle for these
10-heavy-atom molecules anyway, and the MLIP earns its place on FlowER-size molecules and on
stage 2's label volume.

## FLOW-TS STAGE 1 ANSWERED, AND IT REFRAMES ITS OWN STAGE 2 (2026-09-26)

Oracle complete (RCI job 11707572, 4,369 components, 0 failures). Numbers and caveats in
`retro-pfn/flow-ts/BRIEF-stage1.md`; headline, with random tie-breaking against a matched
noise baseline on the same steps:

| ranking | fine-tuned AFM (236 steps) | released AFM (273 steps) |
|---|---|---|
| summed ΔE, endpoints only | **57.6%** (noise 47.5%) | **69.1%** (noise 36.4%) |
| worst intermediate | 52.6% (noise 48.1%) | 35.7% (noise 33.3%) |
| the model's own log-probability | 70.3% | 18.7% |

**The finding that matters is not the pass.** The profile that reads the intermediates is the one
that fails; the profile that ignores them wins. Summed ΔE is E(emitted) − E(reactant), so what is
measured is **product stability, not energy along a mechanism**. ADR 0003 designed stage 2 as a
per-state energy head over the trajectory — this result gives that design no support, and a
product-stability head would reproduce everything seen here. The mechanism-level framing of the
whole line therefore needs re-examination before stage 2 is built, not after. It also sits
consistently with Milan's measurement that AFM's book-keeping intermediates minimise to *lower*
force-field energies than real molecules: those states are notation, not chemistry, and an energy
read there is reading notation.

**What survives and is worth having:** energy is complementary to the generator rather than
redundant. It is right on 32.1% of the steps the fine-tuned model ranks wrong and on 63.4% of those
the released model ranks wrong, which would take the fine-tuned model from 70.3% to roughly 80%
under a perfect combiner. Breaking the model's ties with ΔE gains nothing, so the combiner has to be
learned — that, not the per-state head, is the defensible stage 2.

**Unverified, and it bounds everything above:** the oracle's scatter on our own species. The
ωB97M-V calibration sits in `retro-physics-validation`'s inbox and has not run, and the AIMNet2
ensemble guardrail turned out not to exist in the installed release, so no per-state flag marks
where the potential is extrapolating.

## A THEORY-ROOTED CONSTRUCTION FOR THE GENERATIVE MODEL, AND ITS GATE PASSES (2026-09-26)

`retro-pfn/flow-ts/THEORY-lambda-flow.md`, ADR 0004, gate in `flow-ts/gate/`.

**The construction.** AFM's move increments cancel identically, which is why conservation is an
algebraic identity — and that property is **linear**. So put a progress vector λ over the k arrows of
a step and let B(λ) = B_reactant + Σ λᵢ Δᵢ. Every point conserves atoms and electrons; the corners of
the cube are the serialised states our stage 1 measured at +80 kcal/mol, and the physical path is the
diagonal. This is what intrinsic-bond-orbital arrows say directly: arrows are concurrent functions of
one path coordinate, so there is no state between arrow one and arrow two. Crucially the randomness
now lives in λ rather than in matrix entries, so Milan's Theorem 1 has no product measure to collapse
and **exactness stops competing with stochasticity**. The generator is then discrete over the arrow
multiset (AFM's own chain, whose order ambiguity becomes irrelevant) and continuous over λ, which is
where a flow or diffusion belongs and where the energy-grounded training machinery already exists for
conformers and has never been applied to a bond rearrangement.

**Gate A, run before building anything, on RGD1's 159,913 barriers with no new quantum chemistry.**
The valence-bond form ΔE‡ = f·G − B survives:

| claim | result |
|---|---|
| the driving-force coefficient is a family constant | **0.50**, interquartile range collapsing 0.32 → 0.009 as families grow |
| the intrinsic term tracks the strength of the broken bonds | **r = 0.64 to 0.66**, slope 0.14 to 0.16 |
| the pooled regression shows the same | **no** — r = 0.27 with unphysical negative coefficients |

The third line is the methodological finding: pooling confounds the driving force with the promotion
gap and gives the wrong answer, and it is the natural first analysis to run. Recorded so nobody
repeats it.

**What the gate could not touch, and it is exactly our chemistry.** Simple hydrogen transfer is **10 of
159,913** reactions, because RGD1 was generated by break-two-form-two enumeration and excludes the
one-bond case by construction. Our own corpus is 99 % radical with abstraction as its largest class.
So Gate B is unchanged in purpose and sharper in design: barriers for a few dozen of our own
abstraction steps, testing the same form with the gap taken as the single broken bond. We already hold
the reaction energies and a separated-fragment estimate of the gap; only the barrier is missing, and
that is the bounded DFT campaign.

**Supersedes** ADR 0003's stage 2. The energy head is a function of λ and the bond-change signature,
conditioned on family, with bond additivity as a prior rather than a parameterisation — r = 0.64
leaves about 60 % of the family intercept unexplained, so it must be learned, not imposed.

## THE KILL TEST KILLED IT — the λ-flow's energy claim is refuted (2026-09-27)

`retro-pfn/flow-ts/gate/RESULT-headtohead.md`. 225 Transition1x reactions, both arms sharing base,
restraint, relaxation budget and energy model, differing only in how a changing bond's length moves
along the path.

| arm | bias-corrected MAE | Spearman | maximum mid-path |
|---|---|---|---|
| geometric, length linear | **25.96** | **0.577** | **98 %** |
| Pauling, length from ln of bond order | 88.20 | 0.311 | 10 % |

**The decisive number is the last column.** The Pauling path puts its energy maximum at an endpoint
in nine cases out of ten. It has no saddle, so it is not measuring a barrier at all; for these
endothermic reactions an endpoint maximum is the reaction energy. It also beats the geometric path on
only 46 % of individual reactions, which is a coin toss.

So the claim that made the construction more than a reparametrisation — that the barrier falls out as
the maximum along the λ diagonal — is refuted on data we already owned, in a controlled comparison,
at a cost of about an hour of cluster time.

**What was not tested, stated so nobody claims more than this.** The run stretched every changing
bond *independently*. Johnston and Parr's actual constraint pairs the breaking and forming bond at the
transferred atom (n₁ + n₂ = 1). For a two-bond-break step this run drove four bonds to half-order
simultaneously and built an over-coordinated structure, which plausibly explains both the +53.9 bias
and the missing saddle. Implementing paired conservation for arbitrary multi-bond steps is much
larger work and would forfeit the cheapness that was the point.

**What survives.** The λ manifold is untouched: it conserves at every point, the randomness lives in
arrow progress rather than matrix entries, and Milan's Theorem 1 still does not apply. That is a
usable generative parametrisation. And Gate A's two-term barrier form still holds — family-constant
driving-force coefficient of 0.50, intrinsic term tracking broken-bond strength at r ≈ 0.64. But the
energy is now a **separately regressed head**, which is what the field already does, not a by-product
of the generator.

**Sequence worth remembering.** Three protocols were tried before the comparison was fair: plain
linear interpolation (the documented strawman at MAE 443), Pauling targets imposed on IDPP frames
without relaxation (measures strain, 531 vs 379), and finally per-image constrained relaxation with
both arms treated identically. The first two would each have produced a confident wrong answer. For
this construction the geometry protocol is part of the claim.
