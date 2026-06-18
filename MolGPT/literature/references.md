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
| `schwaller2019_molecular-transformer`, `tetko2020_...`, `irwin2022_chemformer`, `liu2017_seq2seq-retrosynthesis`, `chilingaryan2022_bartsmiles` | reaction transformers | conditional, not in-context |
| `sagawa2023_reactiont5` | limited-data reaction T5 | generative baseline |
| `qiang2023_rxn-pretrain-conditional-generation` | reaction pretrain → conditional gen | closest "rxn→generation" precedent |
| `schwaller2021_rxnfp` | reaction fingerprint | **used as code** (featurizer) |

### Queued / unverified
- `lu2022_t5chem` — paywalled; verify before citing.
</content>
