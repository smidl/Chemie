# Draslovka — partner background check & axes of interest

*Prepared for a potential industrial-partner demo. Company facts are from Draslovka's
own site + independent press/Wikipedia (sourced below) — treat self-descriptions as
marketing until confirmed in a call. The **axes** section is our own mapping onto the
Chemie retrosynthesis/feasibility program.*

## 1. Company snapshot
- **Draslovka Holding a.s.** — Czech specialty-chemicals group, HQ **Kolín**, **founded 1906**;
  **family-owned**, with **Oaktree Capital** as a financial partner (~$150M partnership).
- **What they are:** the **world's largest producer of solid sodium cyanide (NaCN)** and a global
  leader in **hydrogen-cyanide (HCN) based** specialty chemistry. Century of HCN know-how.
- **Scale-up by acquisition (2021–22):** Chemours Mining Solutions (**$521M**), Sasol's NaCN
  business (**$95M**), and Australia's **Mining & Process Solutions (MPS)** — the latter brought
  proprietary **Glycine Leaching Technology (GLT)**. Revenue reportedly ~4× post-Chemours.
- **Footprint:** Czech Republic, South Africa, Australia, New Zealand, India; operations across
  Europe, the Americas, Australasia.

## 2. Three divisions & core chemistry
| Division | What | Chemistry that matters to us |
|---|---|---|
| **Specialty chemicals** | HCN-derived intermediates for pharma / agro / cosmetic / food | **nitriles, cyanohydrins, aminonitriles, amino acids (N-substituted glycines), hydantoins** (Bucherer–Bergs), chelating agents, methacrylate-adjacent |
| **Mining solutions** | NaCN + **GlyCat™** (glycine+cyanide dual-lixiviant) / **GlyLeach™** (base metals) for gold/Ni/Cu/Co | reagent chemistry; **greener-reagent substitution** |
| **Agricultural solutions** | Fumigants/biocides — **EDN™ (ethanedinitrile)**, Bluefume, fertilizers, chlormequat | small-molecule process chemistry |

**Their R&D self-description:** "a strong research team capable of taking molecules **from
laboratory to industrial production**" — i.e. process/route development and scale-up is a stated
core competence, not just commodity manufacturing.

## 3. Strategic DNA (what they actually value — the demo hook)
1. **Green-reagent substitution as a business model.** Their flagship innovation (**GlyCat**)
   replaces most NaCN with a benign amino acid (glycine) — **80% cyanide reduction at comparable
   gold recovery**, now commercial with **Barrick Gold**. They have *proven appetite and revenue*
   from "same product, better/greener pathway."
2. **Lab→industrial route/process development** for HCN-platform specialty molecules.
3. **Feedstock valorization** — turning a cheap C1/nitrile platform (HCN) into higher-value
   specialties.
4. **Cost + sustainability + regulatory** are their decision axes (mining reagents, fumigants).

## 4. Axes of potential interest — mapped to our project (ranked)
Our program owns: an **AND-OR retrosynthesis planner** (Retro\*/AiZynthFinder/syntheseus), a
learned **cost-to-go heuristic** `h`, a per-reaction **feasibility model ξ_f** (mechanism-kernel,
calibrated, barrier-anchored), **physics oracles** (DFT/MLIP barriers — AIMNet2, Skala), a
**forward round-trip / route-validation** harness, and an early **generative reaction proposer**.

| # | Axis | Why it fits Draslovka | What we'd demo | Maturity / honest caveat |
|---|---|---|---|---|
| **A1** | **Feasibility-aware route design for specialty targets** | They do custom lab→industrial synthesis of nitrile/cyanohydrin/hydantoin/amino-acid molecules | Retrosynthesis to a Draslovka-relevant target, **routes ranked by our ξ_f + forward round-trip** (not just "a route", but "a *plausible* route") | Planner+validation are the most mature pieces; **template models are USPTO/Pistachio-trained → organic-pharma-biased**, see §5 |
| **A2** | **Green/cheaper pathway search (GlyCat generalized)** | *Exactly their DNA* — "same product, better reagent/route" | Given a target + a reagent/cost constraint, search alternative disconnections and score feasibility; frame as "computational GlyCat-finding" | Compelling narrative; needs a cost/greenness objective bolted onto search — research, but directly on-message |
| **A3** | **First-principles feasibility under real conditions** | Process viability = yield/T/catalyst/solvent, not just "does a template exist" | Physics-oracle **barrier** prediction (AIMNet2/Skala) + condition-aware ξ_f to say "this step is/ isn't kinetically feasible" | Strong *differentiator* vs generic retro tools; earliest-stage on our side (oracle + conditions work in progress) |
| **A4** | **Feedstock valorization from the HCN platform** | Monetize their cheap C1/nitrile building blocks | Generative proposer + retrosynthesis seeded on **their feedstock** → candidate high-value targets reachable from cyanide chemistry | Generative line (MolPFN) is pre-reaction stage — aspirational, flag as roadmap not demo |

## 5. The honest domain-match caveat (must say this in the demo)
Our retrosynthesis/feasibility models are trained on **USPTO/Pistachio** reaction corpora —
**organic, pharma/medchem-biased**. Draslovka's core is **HCN/cyanide/nitrile process chemistry
and mining/fumigant inorganics**, which those corpora underrepresent. Implications:
- The **template-based planner** may have thin coverage of *their* exact chemistry → don't
  overpromise route *completeness* on cyanide-platform molecules.
- The **transferable strengths** are the *method-level* ones: the **feasibility/mechanism model**,
  **forward round-trip validation**, and **physics-oracle barriers** — these don't depend on
  template memorization and generalize better to their space. Lead with those.
- A credible collaboration would likely start by **fine-tuning/adapting on a slice of their
  reaction data** (a natural first joint deliverable, and a reason for them to share data).

## 6. Recommended demo spine
Lead with **A2 (green-pathway framing)** wrapped around a concrete **A1** demo (route-find +
feasibility-rank a Draslovka-relevant target), with **A3 (physics-oracle feasibility)** as the
"why we're different from AiZynthFinder/ASKCOS" differentiator. Keep A4 as roadmap. Open the §5
caveat proactively — it doubles as the ask (their data → a tuned model).

## Sources
- [Draslovka — About](https://www.draslovka.com/about-us) · [Specialty chemicals](https://www.draslovka.com/specialty-chemicals) · [GLT](https://www.draslovka.com/glt) · [GlyLeach](https://www.draslovka.com/glyleach)
- [Draslovka completes $521M Chemours Mining Solutions acquisition](https://www.draslovka.com/draslovka-completes-521-million-acquisition-of-chemours-mining-solutions-business-8)
- [Wikipedia — Draslovka Holding](https://en.wikipedia.org/wiki/Draslovka_Holding)
- [Barrick Gold to roll out GLT worldwide — Mining Technology](https://www.mining-technology.com/contractors/analysis/draslovka/pressreleases/barrick-gold-glycine-leaching-technology/)
- [Draslovka goes commercial with GlyCat at Barrick's Bulyanhulu — International Mining](https://im-mining.com/2024/02/29/draslovka-goes-commercial-with-glycat-leaching-at-barricks-buylanhulu/)
- Czech Embassy Pretoria — [Draslovka acquires Sasol's NaCN business](https://mzv.gov.cz/pretoria/en/economic_and_commercial_information/czechia_based_draslovka_aquires_sasol_s.html)
