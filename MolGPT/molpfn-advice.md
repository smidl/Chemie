# MolPFN — advisory overview (for advising the student)

Local, advisory notes only. `MolPFN/` is an **external** student repo
(`git@github.com:rektomar/MolPFN.git`); we never write into it. This file is
the overview information needed to advise the student — keep it current as the
student's work and our guidance evolve.

## What MolPFN is (grounded in the code, 2026-06-12 pull)
A **decoder-only SMILES transformer** (`models/clm.py` base, MolGPT-style) with a
**context-set prefix**: C "context" molecules are prepended and attended to
bidirectionally (prefix-causal mask in `models/pfn.py`), then the query SMILES is
generated autoregressively. The context set is the **C nearest-by-property
neighbours** (`datamodules/datamodule_grouped.py` sorts by property, picks the
closest). Conditioning = MolGPT's **binned property tokens**; a `no_prop` variant
conditions on the context set alone. Trained by plain next-token MLE on
QM9/Guacamol; evaluated with MOSES validity/uniqueness/novelty + target-property
hit. In one line: **in-context / retrieval-augmented *conditional molecule
generation***. PyTorch + Lightning + Hydra; entry `train.py` / `train.sh`.

## Why it matters here
It is the concrete PFN-on-molecules experiment closest to MolGPT's GPT→PFN aim.
Lessons from MolPFN (in-context conditioning on properties, grouped datamodules)
feed MolGPT's direction, and PFN behaviour shared with `Synthesis/` belongs in
the Chemie root `coordination/synthesis.md`.

## Open advising threads

### 2026-06-12 — Literature positioning review (novel vs reinventing?)
Reviewed against the pooled ICL/PFN/molecule literature. Verdict: the **current
implemented core is a recombination** of established pieces — MolGPT property-token
conditioning (`bagal2021_molgpt`) + an in-context support-set prefix (neural-process
/ retrieval / PFN-flavoured). The **narrow genuinely-new slice** is doing this for
*conditional generation* with a **property-similar support set**.

**PFN framing — keep it (owner decision).** The "PFN" name is the *destination*, not
a description of today's code: the route there is **adding predictive uncertainty**
(toward a posterior-predictive / amortized-Bayesian object). Current code is the
**generative waypoint**; do not reframe. Worth stating this trajectory explicitly in
the writeup so reviewers read "PFN" as the goal, not a claim about the MLE model.

**Closest prior art to confront (now pooled — both read in full 2026-06-12):**
- `schmidinger2024_bio-xlstm` — **READ.** Its `Chem-xLSTM-icl` *already does*
  in-context support-set-conditioned generation: concatenates a set of molecules from
  one **domain/assay** as context and generates a new molecule of that distribution,
  no fine-tuning, MLE-trained, evaluated on **unseen domains**; beats SMILES-GPT on
  FCD. Differs from MolPFN on: (i) **domain-imitation** (set chosen by domain
  membership/random) vs MolPFN's **property-targeting**; (ii) **no property tokens /
  target value** at all; (iii) **xLSTM** recurrent (cheap 4096-tok context) vs MolPFN's
  O(L²) transformer prefix. ⇒ the broad framing "in-context generation from a support
  set" is **pre-empted** — cite, and ideally benchmark against, Chem-xLSTM.
- `dobberstein2024_llamol` — **READ.** *Not* the support-set idea: "Stochastic Context
  Learning" is **condition-dropout during training** over numeric properties + one
  optional scaffold fragment for the **single** target molecule. No exemplar set ⇒ no
  threat to MolPFN's in-context slice; prior art (with MolGPT) for the property/scaffold
  **conditioning tokens** only.
- `fifty2024_icl-molecular-property` — the in-context **prediction** dual (MolPFN is
  the generation dual; a clean contrast to draw).
- `schimunek2023_mhnfs` — context/retrieval-enriched few-shot molecular modeling.

**Net effect of the full reads on the novelty story (2026-06-12): tightened, not
collapsed.** Bio-xLSTM removes "in-context support-set-conditioned generation" as a
claimable novelty — it exists. What survives is narrower and sharper: **property-
targeted** in-context generation (neighbour-by-property selection + explicit binned
property token), vs Chem-xLSTM's domain-imitation (no property target) and Llamol's
single-target multi-conditioning (no exemplar set). This makes the **context-redundancy
ablation the whole ballgame** — it is exactly what separates MolPFN from Chem-xLSTM
(no property token ⇒ its context carries all signal) and from Llamol (property token,
no context). Required: cite + benchmark Chem-xLSTM; frame the contribution as
property-targeting + the uncertainty→PFN trajectory, never as inventing in-context
generation.

**Key empirical hinge (already on the student's plan):** the context set is the
property-nearest neighbours *while the same property is also a token* → risk the
context is **redundant** with the property token. The `no_prop` variant + a
context-vs-no-context ablation decide whether there's a contribution. Lead with it.

**Cross-link to Synthesis:** MolPFN is the **generation-side** PFN; retro-pfn's
`xif/PLAN.md` model-class-3 ("PFN-as-correlated-ξ_f") is the **prediction-side** PFN
— same in-context-vs-amortized-Bayesian object from two ends. Bidirectional transfer
recorded in Chemie root `coordination/synthesis.md`.
