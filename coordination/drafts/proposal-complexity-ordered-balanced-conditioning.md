# Proposal under scrutiny — complexity-ordered balanced sequences for retro-direction conditioning

**Status: DRAFT, not sent. SUPERSEDED IN PART — see the redirect below.** Owner's idea, 2026-09-20.

> **Redirect, 2026-09-20 (same day, after the prior-art result in §4).** The owner has dropped two
> of the three design commitments scrutinised here:
> - **Complexity ordering is no longer insisted on** — *some* sensible order is wanted, not
>   specifically a complexity-descending one. §3.1 and §3.5 therefore apply to a design choice that
>   is now open rather than fixed, and Test 1 (§5) becomes a measurement about the *shrink-the-target*
>   assumption in general rather than a gate on this proposal.
> - **Arbitrary-subset conditioning is dropped** as too complicated and probably unnecessary here.
>   §3.2's objection (a fixed order is directional and fights arbitrary conditioning) is therefore
>   moot — the directionality is now acceptable, even intended.
>
> **The live target is: variable conditioning with marginalization capacity.** A menu of useful
> conditioning patterns, over a joint model whose unobserved components can be integrated out —
> giving marginals and a likelihood for a *partial* equation. That second property is the
> discriminator against the Zipoli-style task-token seq2seq in §4.1, which supplies conditionals
> for a fixed menu but not, on the face of it, a coherent joint.
>
> A full `/lit` SOTA sweep against that refined target is running. **What survives from this
> document is §3.3 (the retro-direction regularisation objection), §3.4 (leakage), §3.6 (define
> quality before the run), and the tests in §5.** The rest is history of how we got here.

---

## 1. The proposal, restated

Martin is training on SynRBL-balanced data hoping conservation is learned implicitly. The model
is meant to be used later in the arbitrary-conditioning way — condition on the main product,
generate the inputs. The proposal makes that concrete:

- Serialise the **whole balanced reaction as one sequence**: main product, byproducts, reactants,
  reagents — every molecule, atoms conserving exactly.
- **Order the molecules by decreasing complexity, starting from the main product.** The most
  complex molecule (the target) comes first; each subsequent molecule is simpler.
- **Mark each molecule explicitly as input or output** — the side assignment is a token, not a
  position.
- At retrosynthesis time: feed the main product, decode forward, read off the inputs.

Two claims are being made, and they are separable:

- **(C1) Regularisation.** Jointly generating the byproducts regularises the model internally, so
  the proposals are better than an unbalanced model's.
- **(C2) Monotonicity.** The sorting order guarantees the proposed inputs are simpler than the
  product.

The objective: check whether the proposed reactions are of **better quality** than an unbalanced
model's.

## 2. Why this is worth taking seriously

Three real connections, not enthusiasm:

1. **It attacks the standing open problem head-on.** `synthesis.md` §OPEN PROBLEM 2026-09-06: a
   71 %-top-1 proposer (ReactionT5) proposes a largest-precursor *larger* than the product in
   **74 %** of cases, median size ratio **1.11**, against AiZynthFinder's **36 %** / **1.00** —
   and therefore cannot converge. Every remedy considered so far has been a filter or a re-rank.
   This proposal would make shrinkage **structural**.
2. **It is a concrete answer to two of the miniproject's open questions.** `MINIPROJECT-conditioning.md`
   Q3 asks whether exchangeability should be built in or learned, and lists *canonical ordering*
   as one of three options. This picks canonical ordering — and picks a **semantic** order rather
   than an arbitrary one. Q2 asks for the masking unit: this answers *molecule-level, with marks*.
   The marks are literally the brief's `ℓ : S → {LHS, RHS}`.
3. **The data already exists.** Martin built the balancing layer himself (`src/rxn_balance/balance.py`,
   2026-09-17): USPTO-MIT at **95.3 %** balanced, Lowe's USPTO-full at **84.2 %**, plus SynRXN's
   `uspto_50k_b`. No new data work is required to test any of this.

## 3. Scrutiny — six objections, in descending severity

### 3.1 The monotonicity claim (C2) is probably false in the data, and it bakes in a rejection we already know is wrong

The order guarantees the model *emits* molecules in decreasing complexity. It does not guarantee
the emitted molecules are correct precursors — it constrains syntax, not chemistry.

**And on the prior-art pass it turned out not even to constrain syntax.** A decreasing-complexity
order is a *soft data convention*: the model is trained on sequences that happen to obey it, and
nothing at decode time stops it emitting a precursor more complex than the target. The claim
"structurally cannot propose a more complex precursor" is false as stated — it is a learned
tendency, not a guarantee. Making it a guarantee means a **constrained decoder** (mask the
candidate set at each step), which is exactly what `CompleteRXN` does for atom balance. See §4.2.

Worse, the constraint is one this tree has already flagged as crude. `synthesis.md` §OPEN PROBLEM,
*What is open* item 2: **"Rejecting growing proposals outright is crude: protection steps are
legitimately size-increasing."** A hard monotone order bakes that rejection into the
*architecture*, where a filter can be tuned off and an ordering cannot.

And the chemistry says violators are common, not rare. Read in the retro direction, the precursor
of a **deprotection** is *larger* than the product — the protecting group is still on. Same for
any step whose product is the smaller fragment (hydrolyses, cleavages). These are not edge cases
in USPTO. **If a material fraction of records has an LHS molecule at least as complex as the main
product, the "guarantee" is a fiction for that fraction, and the model is being trained to
mis-order exactly the steps the open-problem note said must not be rejected.** This is cheap to
measure and it gates everything — see Test 1.

### 3.2 A single canonical order is directional — "arbitrary conditioning" and "fixed order" are in tension

If the sequence is always [most complex … least complex], prefix-conditioning buys exactly **one**
query cheaply: give the product, continue the suffix — retrosynthesis. Forward prediction asks for
the *most* complex molecule, which under this order sits at the **front**: that is prefix
infilling, not suffix continuation, and it is a strictly harder decode. So the fixed order
privileges retro and handicaps forward — in tension with the brief's founding premise that one
model subsumes forward, retro, condition prediction and scoring by choice of conditioning set.

The proposal has to pick one:

- **(a)** Accept this is a **retro model with a byproduct auxiliary loss**. Narrower, honest,
  testable, and still interesting.
- **(b)** Train order-agnostically (any-order AR), at which point complexity ordering is no longer
  a structural guarantee — just one order among many, and C2 evaporates.

**(a) is the honest version**, and it should be stated as such rather than presented as a step
toward arbitrary conditioning, which it partly works against.

### 3.3 In the retro direction the byproducts are near-constant fillers — which is where the regularisation claim (C1) is weakest

Stage 1 measured this exactly: `_b`'s **LHS additions are only water, protons, iodide and atomic
O — never a real building block, in 0 of 50,016 records.** So "jointly generating byproducts" in
the retro direction largely means emitting a small, nearly reaction-independent set of fillers. A
regulariser that can be satisfied by a near-constant output carries little gradient signal about
the disconnection.

The regularisation story is far more plausible in the **forward** direction, where the RHS
additions carry leaving- and protecting-group fragments that genuinely encode reaction class — and
that is precisely where Martin measured his gain (69.8→76.1, 86.3→88.7, 79.7→82.9). **The proposal
inherits a forward-direction result into the retro direction, where the mechanism that plausibly
produced it is absent.** This is the deepest scientific objection and it deserves an explicit
answer before any training run.

### 3.4 The leakage caveat carries over unchanged

Martin's own 2026-09-17 outbox line: *"part of the accuracy gain may be leakage from SynRBL's
product-aware additions."* SynRBL computes what is missing by looking at **both** sides of a known
record. At genuine retro deployment you have the product and want the precursors — you cannot run
SynRBL to enrich the input, because that needs the answer. Any gain tracing to the enrichment does
not transfer. The proposal does not address this and inherits it whole.

### 3.5 Complexity ties make the canonical order unstable — and likelihood is an intended output

Two molecules of near-equal complexity flip order under a tiny perturbation, making the sequence
likelihood discontinuous in the input. `MINIPROJECT-conditioning.md` §2.3 is explicit that a
permutation-sensitive likelihood is "not merely inelegant, it is wrong", *because* scoring is one
of the intended outputs. Canonical ordering fixes that only if the canonical map is **total and
stable**. Requires a deterministic tie-break chain (complexity → heavy-atom count → canonical
SMILES) and a report of how many records reach the tie-break.

### 3.6 "Better quality" must be operationalised before the run, not after

Exact-match cannot carry this: the **18.5 pp** likelihood-accept vs top-1-exact-match gap was
measured on this very corpus (`MINIPROJECT-conditioning.md` §4). The instrument this tree already
believes in is the **size-ratio distribution** from the open-problem work, with ReactionT5's
74 %/1.11 and AiZynthFinder's 36 %/1.00 as existing reference points. Define quality as that
distribution plus precursor purchasability, and fix it **before** the runs.

## 4. Prior art — RESULT 2026-09-20. Most of the proposal is taken, and one finding lands on M0, not on this proposal

Metadata below verified through Crossref / arXiv raw responses per the citation protocol. **The
interpretive claims still need checking against the full texts before any of this is sent.**

| # | Question | Verdict |
|---|---|---|
| 1 | molecule-level ordering of reaction serializations | **partially taken** — sorting yes, by complexity no |
| 2 | complexity-monotonic generation | **open** — but see the correction below |
| 3 | byproduct/balanced emission as auxiliary signal | **partially taken** |
| 4 | role / side marker tokens | **taken** |
| 5 | arbitrary-subset conditioning on reactions | **taken — and it lands on M0** |

### 4.1 The finding that matters is not about this proposal — it is about the miniproject

**`zipoli2024_partial-chemical-equations`** — Zipoli, Ayadi, Schwaller, Laino, Vaucher,
*Completion of partial chemical equations*, *Machine Learning: Science and Technology*
**5(2):025071** (2024), Crossref-verified. One transformer that predicts any missing molecules at
arbitrary positions, using explicit `[forward]` / `[retro]` / `[rsc]` / `[unspecified]` task
tokens, and reported by the search as explicitly framed as *"a generalization of the forward
reaction prediction and retrosynthesis models, since both can be expressed in terms of incomplete
chemical equations"*, with per-task numbers for explicit vs unspecified tokens.

That is designs 4 and 5 of this proposal, published. It is also, read literally,
`MINIPROJECT-conditioning.md` §7's **M0 stop criterion**: *"Stop if prior art already covers
variable-conditioning reaction models with per-pattern numbers."*

**This paper is absent from `retro-generation` entirely** — zero hits across `literature/`,
`reviews/`, `MINIPROJECT-conditioning.md` and `coordination/` (checked 2026-09-20). The 2026-09-04
outbox entry concluded *"the nearest prior art is now MechSMILES, whose four task signatures are
fixed, so M0's stop criterion is not triggered"* — a verdict reached without this paper in view.

**Do not act on this until the full text is read.** The metadata is verified; the reading is
second-hand. What has to be confirmed directly: whether the conditioning set is genuinely a free
variable (arbitrary subsets) or a fixed menu of task modes, and whether the reported per-pattern
numbers are comparable. Those two facts decide whether M0 actually stops. Note also that IBM RXN
is `thakkar2023`'s group — the same group already occupying the generation-side conditioning axis
in our control-token survey.

### 4.2 The rest

- **Ordering (Q1).** `RETROSPECT` (arXiv:2606.07181, verified) canonically **fragment-sorts**
  augmented multi-fragment reactants "to reduce output-order variance", motivated by 70.7 % of
  training reactions having two precursor fragments. `wang_order-matters-retrosynthesis`
  (arXiv:2602.13136, verified) measures ordering effects at atom/node level. R-SMILES (Zhong,
  Song, Feng, Liu, Jia, Yao, Wu, Hou, Song, *Chem. Sci.* 13(31):9023–9034, 2022, Crossref-verified)
  is atom-level root alignment but implicitly fixes fragment order via product alignment, so it
  partly pre-empts the mechanism. **Nobody sorts by complexity, and nobody reports an
  ordering-only ablation.** That is the gap.
- **Complexity constraints (Q2) — open, with a correction that kills C2 as stated.** SCScore
  (Coley, Rogers, Green, Jensen, *JCIM* 58(2):252–261, 2018, Crossref-verified) is used as an RL
  reward and as a planner-side expansion heuristic, not to constrain a single-step decoder. But
  the search returns a blunt and correct objection: **decreasing-complexity ordering is a soft
  data convention, not a constraint — nothing stops the decoder violating it, so "structurally
  cannot propose a more complex precursor" is false as stated.** The published machinery for doing
  it properly exists: `CompleteRXN` (arXiv:2605.00222, verified) masks tokens during beam search so
  decoding terminates only when atom-balanced. Hard decode-time constraints on a conserved quantity
  are published — for **mass**, not complexity. Converting C2 into an actual constrained decoder
  along those lines would be new; leaving it as an ordering convention is neither new nor a guarantee.
- **Byproduct emission as regularisation (Q3).** `RETROSPECT` trains a differentiable atom-balance
  auxiliary loss and reports top-1 45.83 → 47.37 (+1.54) — but **bundled** with Pre-LayerNorm and
  EMA, so not disentangled. `AutoTemplate` (Chen & Li, *J. Cheminform.* 16:74, 2024, verified)
  curates balanced data and measures downstream accuracy; SynRBL (Phan et al., *J. Cheminform.*
  16:82, 2024, verified) rebalances; FlowER (Joung et al., *Nature* 2025, DOI
  10.1038/s41586-025-09426-9, verified) is conservation-by-construction. **Not found: a controlled
  A/B of "emit byproducts too" vs "main product only" on identical reactions, reported as a
  regularisation effect.** That is the second gap — and it is exactly Martin's `_u`/`_b`
  experiment, in the retro direction.

### 4.3 What is genuinely unoccupied

Two things, both narrow: **(i)** ordering a balanced reaction's molecules by decreasing complexity
*and ablating it*, and **(ii)** a clean regularisation A/B for byproduct emission. Everything else
— role tokens, arbitrary-subset conditioning, atom-balance auxiliary losses, balance-constrained
decoding — is published, most of it by IBM RXN and the CompleteRXN group. The honest baseline for
(i) is **RETROSPECT's canonical fragment sorting**, not an unsorted model.

**Caution on RETROSPECT:** 2026 ICML workshop preprint from Mstack AI, unreplicated, and it shares
an author (Sathyanarayana) with the unverifiable "Protect*" entry already filed under *Dead ends*
in `~/agents/library/sota/control-tokens-in-reaction-generation.md`. Treat its numbers as
unreplicated. Pooling candidates if wanted: arXiv:2605.00222, arXiv:2606.07181.

### 4.4 What our own survey already said

`docs/sota/control-tokens-in-reaction-generation.md` (2026-09-13) found, in both full texts of the
site-level control papers, **zero** mentions of molecule size or complexity: *"All published
control is site-level… neither paper measures molecule size or complexity at all."* That holds up
— the complexity axis survives this search too. It is just much narrower than the proposal.

## 5. How to validate quickly — four tests, ascending cost

### Test 1 — no GPU, ~1 day. Does the monotonicity assumption survive contact with the data?

On the balanced corpora that already exist (`uspto_50k_b`, `uspto_mit_b`, `uspto_full_b`): in what
fraction of records is **every** LHS molecule strictly simpler than the main product? Run it under
three measures — heavy-atom count, SAScore, SCScore — to show the answer is not measure-dependent,
and break the violators down by reaction class where a label exists.

**This is the cheap falsifier and it should run before anything else.** A large violation rate
does not merely weaken C2 — it says the ordering would train the model to mis-rank precisely the
protection/cleavage steps that must not be rejected. Reuses the `stage1.py` / `compare_pair.py`
machinery; one CPU job.

### Test 2 — cheap GPU, reuses the existing pipeline. Ordering ablation with a semantic control.

Same balanced data, same 5.7 M model, same splits, three serializations:

1. dataset-native order,
2. **canonical fragment sorting** (sort by canonical SMILES string — deterministic but
   semantically meaningless),
3. complexity-descending order.

**Arm 2 is what makes this test worth running, and after §4 it is no longer just a control — it is
the published baseline.** RETROSPECT already canonically fragment-sorts "to reduce output-order
variance". So arm 2 *is* prior art, and the only question the experiment can answer is whether
arm 3 beats it. Without arm 2, any gain from arm 3 gets misattributed to *complexity* when it may
only be "a fixed order is easier to learn than a noisy one" — the Vinyals *Order Matters* result,
a re-derivation rather than a finding. If (2) ≈ (3), the complexity story is dead for a few
GPU-hours. Multiple seeds, per the standing rule.

### Test 3 — isolate the regularisation claim (C1) in the direction that matters.

Retro direction, same balanced records, two arms: target = precursors only, vs target = precursors
+ byproducts. Score **only the real precursors**, with the Stage-1 spectator list (`O`, `[H+]`,
`[I-]`, `[O]`, `[OH-]`) stripped from both arms before matching. Report stripped and unstripped
numbers side by side so the size of the scoring artefact is visible rather than assumed away.

### Test 4 — measure quality, not accuracy.

Run both models over the target set used in the 2026-09-06 open-problem measurement and compare
**size-ratio distributions**, against the existing 74 %/1.11 and 36 %/1.00 reference points. If the
complexity-ordered model does not shift that distribution, the mechanism did not fire, whatever
top-1 says.

## 6. Recommended framing for the message to Martin

**The proposal is no longer the most important thing in this document.** Order the message:

1. **Zipoli et al. 2024 first, as a question, not a verdict.** It is missing from his survey and it
   sits directly on M0's stop criterion, which he closed on 2026-09-04 without it. He owns the
   novelty verdict — the brief says so explicitly — so the right move is to hand him the reference
   and ask whether it triggers the stop criterion, not to announce that it does. **Read the full
   text on our side first** (§4.1): if the conditioning set turns out to be a fixed menu of task
   modes rather than a free variable, this is a strong neighbour rather than a stop, and sending it
   as a stop would be a false alarm on a student's main project.
2. **Then the surviving gaps**, which are narrow but real: complexity ordering with an ablation
   against RETROSPECT's canonical fragment sorting, and the clean byproduct-regularisation A/B —
   which is his own `_u`/`_b` experiment carried into the retro direction, where §3.3 says the
   mechanism may not survive.
3. **Then Test 1**, which stands regardless of any of the above and costs a CPU day.

Our own control-token survey already concluded, about a structurally similar idea: *"the paper is
the **diagnosis**, with the control token as the remedy, not the reverse."* That verdict now
applies twice over. If monotonicity fails in a large minority of real reactions, the measurement —
*how often real chemistry violates the shrink-the-target assumption* — is a finding about the open
problem and a more defensible contribution than the serialization scheme, which is mostly taken.
