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
retro-pfn is GP-stage on ξ_f. Reaction→molecule feedback already live: retro-pfn's
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
- **MolGPT (T3 proposer): DIVERGENT (substance) / PARTIAL (infra)** — in-context *molecule*
  generation now; role needs in-context *reaction* generation, balanced, σ-frontier-coupled. Infra
  reusable; reaction I/O + balance + σ-conditioning absent; its 3 advisory docs assert the
  superseded molecule-gen framing. Re-point: reaction tokenizer + dataset/balance (prereq) →
  disconnection-exemplar context + σ-token → loop coupling; recast the redundancy ablation for
  reactions. Expansion-phase, not blocking.
- Parked charters (`flow-ts`, `path-correlation`): peripheral to the loop; leave parked.

**Common thread:** the surrogate *substrate* is built; what's missing program-wide is the loop's
**connective tissue** — the acquisition primitive (σ→query selection), the oracle-on-demand
interface, and a reaction proposer — not the components themselves.

_(Awaiting the first shared experimental result to record a derived finding.)_
