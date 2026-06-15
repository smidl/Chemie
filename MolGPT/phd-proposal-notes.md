# phd-proposal — transformer-part import (advisory)

Local notes pulled from the student's PhD thesis proposal (`phd-proposal/`, an
Overleaf **boundary**; we advise only, never write into it). Imported
2026-06-07. The proposal has two parts; **only the transformer-based generative
models part is in scope here** — the probabilistic-circuits (PGC) part is
deliberately ignored.

## Scope pulled
- `src/introduction.tex` — molecular representations (graphs vs strings, SMILES)
- `src/molgpt.tex` — autoregressive SMILES generation + conditional MolGPT
- `src/pfn.tex` + `src/appendix_b.tex` — Prior-Fitted Networks, in-context molecular generation
- Ignored: `src/pgc.tex`, `src/appendix_a.tex` (probabilistic circuits / sum-product networks)

## Transformer-part content (what the proposal argues)
**Representations.** A molecule has no single numerical form. Matrix/graph forms
pair with PGCs/GNNs; **string forms (SMILES, Weininger 1988) pair with
autoregressive transformers** — the basis for the GPT/PFN chapters. SMILES is
non-unique (traversal-dependent) and token-by-token generation does not enforce
valency/grammar, so strings may decode to invalid molecules.

**MolGPT chapter.** Treat a molecule as a token sequence; model with the
standard left-to-right AR factorization via a **decoder-only transformer**
(Vaswani 2017; scaled up as in GPT-2/GPT-3). Conditional generation prepends a
conditioning object **c** (scaffold, property vector, spectrum) as tokens —
no architectural change. Four ways to inject continuous properties **y**:
1. **MolGPT (baseline)** — single property-embedding token prepended.
2. **Property tokens** — one embedding token per property.
3. **Additive modulation** — layer-wise embedding added to hidden states.
4. **Concatenative modulation** — layer-wise embedding concatenated + projected.
5. **Binned property tokens** — discretize each property into bins, one shared
   token per bin. *This variant is explicitly flagged as the one closest to the
   prior-fitted networks of the PFN chapter.*
Experiments: unconditional generation on QM9 and Zinc250k (GPT vs intractable/
tractable DGM baselines).

**PFN chapter (the bridge to MolGPT's GPT→PFN aim).** PFNs (Müller 2022)
amortize Bayesian inference: train one transformer over a prior treated as a
data generator, so the posterior predictive is produced in a single forward
pass (in-context learning, no test-time inference). The proposal's novel
direction is **in-context *molecular generation*** — modelling
`p(m | c, D_ctx)` with a small context set of (molecule, condition) pairs.
Three goals: (i) uncertainty-aware generation, (ii) chemical soundness
(valency/ring rules, extrapolation), (iii) variance reduction from c + D_ctx.
Three departures from standard PFNs: structured combinatorial output (needs an
AR/graph decoder, not a softmax head); a **chemically-informed prior** (samples
are valid (m, c) pairs); and structured molecular inputs on both context and
query sides.

## Advisory relevance (for MolGPT)
- The **binned-property-tokens → PFN** thread is the concrete bridge for our
  GPT→PFN line; worth tracking in the student's work.
- The **in-context molecular generation** framing is PFN-for-molecules and
  overlaps with `Synthesis/`'s PFN use — a cross-cutting PFN item for the Chemie
  root `coordination/synthesis.md`.

## References imported to the pool (`~/agents/library/`)
Pooled now (open, verified `.bib`):
- `vaswani2017_attention` — Attention Is All You Need (transformer)
- `radford2019_gpt2` — GPT-2 (Language Models are Unsupervised Multitask Learners)
- `brown2020_gpt3` — GPT-3 (Language Models are Few-Shot Learners)
- `muller2022_transformers-bayesian-inference` — PFNs (Transformers Can Do Bayesian Inference)

Queued (paywalled — see `~/agents/library/paywalled.md`):
- `bagal2021_molgpt` — **the canonical MolGPT paper** (open ChemRxiv "LigGPT" preprint grabbable by hand)
- `weininger1988_smiles` — SMILES (1988 ACS, no OA)
- `tomczak2024_deep-generative-modeling` — DGM book (also: undefined in the student's `main.bib`)

Already in pool (related, not re-added): `hollmann2022_tabpfn`,
`benhicham2026_tabpfn-molecular`.

## ICL literature pull (2026-06-12)
Ran `/lit` on in-context learning for molecules + foundational ICL. **23 seminal
references added to the pool** (22 PDFs + 1 web-only `.bib`, Olsson induction
heads); **TabPFN v2** queued paywalled (`~/agents/library/paywalled.md`). Strands:
general ICL, ICL mechanism/theory, PFNs/amortized-Bayes/neural-processes/meta-
learning, ICL-for-molecules, ICL-for-reactions. Cross-cutting picture + the
bidirectional MolGPT↔Synthesis transfer policy: Chemie root
`coordination/synthesis.md`. Optional/⚠ candidates (Schaeffer, Dai, Elhage,
Garnelo-NP, Grant, Gordon, Guo-MetaMGNN, Bio-xLSTM, Llamol, Schwaller Molecular
Transformer, ChemCrow, Dinh-LIFT) were **not** pooled — ask if any are wanted.
