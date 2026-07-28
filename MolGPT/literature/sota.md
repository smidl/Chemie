> **⚠️ MOVED (2026-07-24).** The reaction-generation line was handed off to the sibling leaf
> **`retro-generation/`**; the unified survey now lives at `retro-generation/literature/sota.md`
> (+ pooled `~/agents/library/sota/generative-reaction-prediction.md`). This file is retained for
> history. MolGPT continues the *molecule*-generation track.

# SOTA — in-context learning for a generative model of reactions (MolGPT)

Consolidated 2026-06-18. MolGPT's primary framing: a **trained, in-context
(support-set-conditioned) generative model that proposes reactions /
disconnections** — the candidate-proposer (T3) of the active-acquisition loop
(propose → retro-pfn's ξ_f validates). This file gathers the in-context SOTA that
was searched and **pooled** (`~/agents/library`) but never consolidated; the
cross-cutting analysis lives in Chemie `coordination/synthesis.md` §"In-context
learning". Reverse-map: `references.md`.

## Bottom line
The broad ideas MolGPT sits on are **taken**: in-context learning of chemical
sequences (Bio-xLSTM), in-context learning *for retrosynthesis* (FusionRetro),
few-shot single-step retro (MHNreact), frozen-LLM in-context for reactions
(ChemLLMBench / BO-ICL), and generative reaction transformers (Molecular
Transformer, ReactionT5, the reaction-pretraining→generation unified model). The
**surviving slice** is the intersection none of them occupy:

> a **trained** (not frozen-LLM) model whose **in-context support set** =
> *disconnection exemplars*, that **generates structured reaction output**, with a
> **σ / frontier-conditioning** token so it proposes where the feasibility
> surrogate is uncertain — i.e. an in-context reaction proposer wired into a
> closed acquisition loop, not a stand-alone predictor.

Each axis below is occupied; the contribution is the *combination* + the loop role.

## Axis map (five strands; ✓ = pooled)
### 1. General ICL + mechanism (substrate, not contested)
✓ `brown2020_gpt3`, `garg2022_transformers-incontext-function-classes`,
`bai2023_transformers-as-statisticians`, `akyurek2023_what-learning-algorithm-icl`,
`dong2024_icl-survey`. ICL = adapt from in-context examples, no weight update;
mechanism debated (induction heads / implicit Bayes / GD-in-forward-pass).

### 2. PFNs / amortized Bayes / neural processes (the target form)
✓ `hollmann2022_tabpfn`, `garnelo2018_conditional-neural-processes`,
`kim2019_attentive-neural-processes`, `chen2022_metarf`. PFNs amortize Bayesian
inference into one forward pass — the calibrated-in-context object MolGPT's
"GPT→PFN" aim points at. **Gap for us:** PFNs target *prediction*; MolGPT's output
is a *structured chemical object*, and a true PFN needs calibrated in-context σ
(still pending).

### 3. ICL for molecules (generation side)
✓ `fifty2024_icl-molecular-property` (in-context molecular property),
`schmidinger2024_bio-xlstm` (**generative modeling + in-context learning of
chemical sequences — owns the broad "in-context generation of chemical sequences"
framing**), `dobberstein2024_llamol` (LLM molecule generation). MolPFN (the
student repo) = in-context/retrieval-augmented **conditional molecule** generation
(MolGPT-style + context-set prefix). **Gap:** these generate *molecules*, not
*reactions*.

### 4. ICL / LLM for reactions (the nearest competitors)
✓ `liu2023_fusionretro` (**in-context learning *for retrosynthesis*** — the prior
work owning the "in-context for reactions" framing; the niche must be argued
against it), ✓ `seidl2022_mhnreact` (few-shot single-step retro), ✓
`guo2023_chemllmbench` + ✓ `ramos2023_bo-icl` (**frozen-LLM** in-context for
reactions / BO), ✓ `jablonka2024_llm-predictive-chemistry`. New top-ups (2024–25
LLM line): `yang2024_batgpt-chem`, `lin2025_llm-dualtask-reaction-retro`.
**Distinction:** FusionRetro is in-context but *predicts* (retro), not a
σ-conditioned proposer; the LLM line is *frozen/fine-tuned*, not trained-in-context
with a structured generative head.

### 5. Generative reaction models, NOT in-context (baselines to beat)
✓ `schwaller2019_molecular-transformer`, ✓ `tetko2020_augmented-transformer-retrosynthesis`,
✓ `irwin2022_chemformer`, ✓ `chilingaryan2022_bartsmiles`, ✓ `liu2017_seq2seq-retrosynthesis`,
+ `sagawa2025_reactiont5-jcheminf` (limited-data reaction T5 — **the journal version, not the
`sagawa2023_reactiont5` preprint**), `qiang2023_rxn-pretrain-conditional-generation`
(**reaction pretraining → conditional generation — closest "reaction-knowledge→generation"
precedent**). All conditional/fine-tuned, none support-set-conditioned. RXNFP
(`schwaller2021_rxnfp`) is *used as code* (reaction featurizer) — concrete shared touchpoint.

> **Baselines corrected 2026-07-28** (this section is retained for history; the live version is
> `retro-generation/literature/sota.md`). Verified by exact reproduction, 40k USPTO_MIT test
> reactions, beam 5: **Molecular Transformer top-1 = 90.4, NOT 88.8** (88.8 is the unreleased
> unaugmented-Baseline row that ReactionT5 and much of the field quote → the standard baseline is
> understated by 1.6 pp); **ReactionT5 = 92.8** in the J. Cheminform. version matching the
> released checkpoint (the preprint's un-fine-tuned number is 0.0 — a different claim). USPTO_MIT
> top-1 is RDKit-version-dependent (41/40,000 flip between 2024.03 and 2026.03), so record the
> RDKit version with any number. Bearing on §2's PFN claim: Molecular Transformer's plain
> likelihood-derived confidence already classifies its own correctness at **ROC-AUC 0.89** — the
> bar any "calibrated in-context σ" claim must clear, set by a non-Bayesian 2019 model.

## Surviving novelty delta (what MolGPT would claim)
A **trained in-context reaction proposer**: support set = disconnection exemplars
→ generates structured reaction SMILES (`>>`/`.`, mass-balanced), with a
σ/frontier token coupling it to retro-pfn's ξ_f in the active-acquisition loop.
Differentiated from: FusionRetro (in-context but predictive, no σ-coupling),
frozen-LLM ICL (ChemLLMBench — not trained, not structured-generative),
Bio-xLSTM (in-context chemical sequences, not reactions / not loop-coupled),
ReactionT5 / Molecular Transformer (generative but not in-context).

## Go / no-go on the reaction re-point
**GO, with the decisive experiment held fixed.** The slice is real but narrow, so
the contribution rests on the **context-redundancy ablation recast for reactions**
(does the in-context disconnection set add signal *beyond* the σ/property
conditioning token?). If the context set adds nothing over the token, the claim
collapses to "conditional reaction generation" (crowded; ReactionT5/Qiang2023) and
we say so. Prereqs (MolGPT inbox 2026-06-15): reaction tokenizer + balance check →
disconnection-exemplar context + σ token → ξ_f coupling. MolPFN machinery (context
prefix, grouped datamodule, binned tokens) is reused as-is.

## Not consolidated before / open
- This is the first MolGPT-local consolidation; the pooled corpus + the
  `synthesis.md` §ICL analysis predated the firm "generative model for *reactions*"
  framing (they were molecule-centric). Top-ups added the 2023–25 reaction lines.
- Paywalled/queued: `lu2022_t5chem`. Verify before citing (global rule).
</content>
