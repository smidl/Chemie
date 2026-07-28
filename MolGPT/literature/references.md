# References — MolGPT (local reverse-map)

In-context SOTA for a generative model of reactions. Verified PDFs live in the
machine pool (`~/agents/library`); this is the local reverse-map + annotations.
Analysis: `sota.md`. Cross-cutting ICL picture: Chemie `coordination/synthesis.md`
§"In-context learning". Origin/reading map: `../phd-proposal-notes.md`,
`../molpfn-advice.md`.

### Strand 1–2 — general ICL + PFNs / amortized Bayes (substrate / target form)
| pool key | short | note |
|---|---|---|
| `brown2020_gpt3`, `garg2022_...`, `bai2023_...`, `akyurek2023_...`, `dong2024_icl-survey` | ICL + mechanism | substrate |
| `hollmann2022_tabpfn`, `garnelo2018_conditional-neural-processes`, `kim2019_attentive-neural-processes`, `chen2022_metarf` | PFN / NP / meta | the GPT→PFN target form |

### Strand 3 — ICL for molecules (generation side)
| pool key | short | note |
|---|---|---|
| `schmidinger2024_bio-xlstm` | in-context gen of chemical sequences | **owns the broad framing** |
| `fifty2024_icl-molecular-property` | in-context molecular property | molecule side |
| `dobberstein2024_llamol` | LLM molecule generation | — |

### Strand 4 — ICL / LLM for reactions (nearest competitors)
| pool key | short | note |
|---|---|---|
| `liu2023_fusionretro` | **in-context learning for retrosynthesis** | nearest precedent to argue against |
| `seidl2022_mhnreact` | few-shot single-step retro | — |
| `guo2023_chemllmbench`, `ramos2023_bo-icl` | frozen-LLM in-context for reactions / BO | not trained-in-context |
| `jablonka2024_llm-predictive-chemistry` | LLMs in predictive chemistry | — |
| `yang2024_batgpt-chem`, `lin2025_llm-dualtask-reaction-retro` | 2024–25 LLM retro/reaction | fine-tuned LLM line |

### Strand 5 — generative reaction models, not in-context (baselines)
| pool key | short | note |
|---|---|---|
| `schwaller2019_molecular-transformer`, `tetko2020_...`, `irwin2022_chemformer`, `liu2017_seq2seq-retrosynthesis`, `chilingaryan2022_bartsmiles` | reaction transformers | conditional, not in-context. **Baseline correction (2026-07-28):** Molecular Transformer's USPTO_MIT top-1 is **90.4, not 88.8** — 88.8 is the paper's *unaugmented Baseline* row whose weights were never released; the released model + headline is 90.4 (reproduced exactly at 90.40 by `retro-generation` 2026-07-27). ReactionT5's comparison table and much of the field quote 88.8, understating the standard baseline by 1.6 pp. Also: USPTO_MIT top-1 is RDKit-version-dependent (41/40,000 flip between RDKit 2024.03 and 2026.03 on identical predictions) — always record the RDKit version. |
| `sagawa2025_reactiont5-jcheminf` | limited-data reaction T5 (**J. Cheminform. 2025** — cite THIS, not the `sagawa2023_reactiont5` preprint) | generative baseline. Numbers differ materially between versions: un-fine-tuned USPTO_MIT top-1 is **0.0 in the preprint vs 92.8 in the journal version**, and the released checkpoint matches the journal. Reproduced by `retro-generation` 2026-07-27 at **92.60** (40k test rxns, beam 5). |
| `qiang2023_rxn-pretrain-conditional-generation` | reaction pretrain → conditional gen | closest "rxn→generation" precedent |
| `schwaller2021_rxnfp` | reaction fingerprint | **used as code** (featurizer) |

### Queued / unverified
- `lu2022_t5chem` — paywalled; verify before citing.
</content>
