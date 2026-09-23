# Working document — active learning where the noise is REDUCIBLE

**Status: WORKING DOCUMENT, opened 2026-09-21. Direction fixed by the owner; carrier,
oracle and target quantity deliberately open.** Not a plan, not a scope decision. Its
job is to record the evidence a plan would have to respect, and to keep the options
visible while the cheap checks run.

Supersedes nothing yet. `thesis-A-scope.md` (injected label noise) and
`thesis-topics-active-learning.md` §B (cost-aware escalation) both stay live until the
owner and Aymen agree a switch.

---

## 1. The direction, in one sentence

**Stop injecting irreducible noise and start measuring reducible error.** The thing to
be uncertain about is not the label, it is *our own model*: where is the cheap rung
wrong, and is it worth paying for a better one there?

## 2. Why this reframing, and it is the strongest argument this tree has

Four independent attempts to use uncertainty have failed here, and they failed the
*same* way:

| attempt | signal | outcome |
|---|---|---|
| feasibility surrogate | GP posterior σ; 6-member deep ensemble | σ ⊥ \|error\|: ρ **0.042** / **0.144–0.146**; σ-driven acquisition ≈ random or worse (passive 0.7606 vs 0.7377) |
| feasibility classifier | MC-dropout, decomposed | predictive **0.83**, aleatoric **0.82**, random 0.77 — but **epistemic 0.76 ≈ random** |
| search heuristic | σ-as-exploration bonus in MCTS | clean negative, parked |
| in-context generation | context spread | scale not tracked at all; a fixed output floor |

**Every one is a posterior quantity on a problem whose noise is irreducible.** The only
signal that ever beat random was *aleatoric* entropy — which is precisely the wrong kind
for an active-learning thesis, and the tree recorded that openly as "a materially weaker
justification for the loop than the one we set out with."

Rung error is different in kind. It is **reducible by construction**: escalate and it
goes away. That makes this the first setting in which the question Aymen is meant to
answer is well posed.

## 3. The evidence that makes it actionable — the ladder is measured

Costs and errors from this tree's own runs. This table is the asset; the thesis is a
policy over it.

| rung | cost | measured error (barriers unless noted) |
|---|---|---|
| GFN2-xTB | seconds | **14.40** forward barrier / 10.57 reverse / **10.11** reaction energy, all 449 BH9 at reference geometries (job 11680758, 2026-09-21) |
| AIMNet2 | ~43 s (endpoints) | **16.70** general / **4.73** domain-routed on all 449 BH9; **4.76** on 100 Transition1x; reaction energy **2.88** |
| NEB, ωB97X/6-31G(d), 4 img / 25 cyc | ~393 s | **9.89**, Spearman 0.853 |
| NEB, 8 img / 50 cyc | ~1294 s | **8.83**, Spearman 0.902 |
| PBE0-D3BJ/def2-TZVP (autodE + ORCA) | 45–90 min | **3.80** (n=3 vs BH9) |
| ωB97M-V single point on the same geometry | ~4 min | **1.14** |
| DLPNO-CCSD(T) single point | ~11–17 min | **0.84** — reference |
| Skala, reaction energy only | cheap | **4.02**, Pearson **0.996** |

**MEASURED 2026-09-21 — and it changes the shape of the ladder.** GFN2-xTB on all 449 BH9
systems at the reference geometries, separated-reactant referencing, same protocol as the
AIMNet2 measurement so the two are comparable:

| | forward barrier MAE |
|---|---|
| GFN2-xTB, seconds | **14.40** |
| AIMNet2, general, ~43 s | 16.70 |
| AIMNet2, **domain-routed** | 4.73 (in-sample) |

**The bottom two rungs are not distinguishable.** A semi-empirical method that costs seconds
is, if anything, slightly *better* on barriers than an un-routed machine-learned potential
costing forty times more. The accuracy jump on this ladder is not a rung at all — it is the
**routing**, 14.40 → 4.73, and that rule was chosen after inspecting the benchmark, so it is
in-sample and needs an external check before it is believed.

Consequences for the thesis, and they are helpful rather than damaging:
- The ladder as written had a **phantom step**. An escalation policy over four rungs where
  two are equivalent is a different and easier problem than over four distinct ones.
- **The escalation decision may be "which domain am I in", not "which rung do I buy".** That
  is a sharper question and it is closer to reducible error than to cost.
- On reaction energies xTB is clearly worst: **10.11** against Skala 4.02 and AIMNet2-routed
  2.88. Barriers and reaction energies do not rank the rungs the same way, so the policy has
  to be per-quantity.
- **Multi-fragment reactants cost 53 %**: forward barrier 16.88 with two or more fragments
  against 11.04 with one. The same split that breaks geometry construction also degrades the
  energy model.

Caveat carried: these are energies at *reference* geometries, so geometry error is excluded
by construction and real use is worse. Single run, unreviewed.

Two things this table already settles:

- **A DFT-grade oracle is not required.** The owner's instinct is right: AIMNet2 routed
  is 4.73 against a 0.84 reference, at seconds instead of an hour. Whether that is
  accurate *enough* is a requirement question, not a method question — see §5.
- **Shortcuts that skip geometry relaxation do not work.** Skala over an unrelaxed path
  gives **47.72** with +102 % bias. The saddle point has to be searched for.

## 4. Design constraints already known — a plan must respect these

1. **Barriers are not state functions.** Anything composed move-by-move and read off at
   the end is a *reaction energy*, which is path-independent. Reaction energies are
   already cheap and accurate (4.02 / r=0.996). The barrier lives at the saddle and does
   not decompose additively.
2. **Error structure beats error magnitude.** A 16.70 oracle whose error is *common* to a
   route's steps disturbs the chosen route less than a 0.84 oracle whose error *varies*:
   **8.3 % vs 14.4 %** top-1 flips. So a biased-but-consistent cheap rung may be worth
   more than a precise scattered one.
3. **Our own error correlation is unmeasured.** The two arms above are the extremes
   (ρ=0 and ρ=1) and the only real data is n=3, all one sign. This is a gap, and it is
   arguably the single most useful thing the thesis could close.
4. **The task is ranking, not estimation.** Every downstream consumer ranks. Absolute
   accuracy is instrumental.
5. **Mechanistic information ranks barriers well; one pretrained embedding did not.** A
   three-token bond-change fingerprint reaches **0.585** against structural **0.417**;
   FlowER's pretrained embedding reached only 0.24–0.28. The *information* works, that
   *representation* did not.

## 5. The options, kept open

**What is being escalated over** — pick one, they are not equivalent:
- (a) single reactions, to build an error-vs-compute frontier (the cleanest thesis);
- (b) edges inside a planner, where the escalation policy *is* the product;
- (c) steps of a mechanism, if the carrier turns out to be per-move.

**What the carrier is** — genuinely open, and the owner's position is that if the value
function is not it, something else will be:
- a value function / cost-to-go over route nodes;
- an edge-cost model consumed by search;
- a stand-alone error model with no planner in the loop at all (weakest coupling, lowest
  risk, still a thesis).

**What the top rung is** — DFT is *not* assumed. AIMNet2-routed, ωB97M-V single points on
cheap geometries, or a full DFT search are all admissible; the ladder above prices each.

**What the target quantity is** — barrier, reaction energy, or a rank. Given §4.1 and
§4.4, the rank is the most defensible and the reaction energy the cheapest.

## 6. Checks to run before the plan is written

Cheap, on data held, and each can redirect the design.

1. **Finish the yardstick: GFN2-xTB on BH9**, same definition and accounting as the other
   rungs. It is the missing row of §3 and has been outstanding since August. Small,
   bounded, and nothing else is blocked on anything else.
2. **Measure our own error correlation** across reaction families on shared geometries,
   at n ≫ 3. This closes §4.3 and decides whether "escalate where the error is large" or
   "escalate where the error is *uncorrelated*" is the right acquisition. **RGD1** is the
   argument here — 176,992 reactions shipping transition states, barriers, endpoint
   geometries *and* atom mappings — adopt rather than generate.
3. **Does escalation change a decision?** Perturb existing route sets by each rung's
   measured error and count rank flips. If the cheap rung already picks the same routes,
   the loop has nothing to optimise. This is the requirement test, and it is the one the
   post-DFT assessment says must precede any acquisition work.

## 7. Proposed learning ladder (skeleton — to be agreed with Aymen, not imposed)

Modelled on the phased vehicle used for the physics-validation node, which worked.

| phase | what he does | what it teaches | artefact |
|---|---|---|---|
| 0 | reproduce two rows of §3 himself on a held benchmark | the ladder is real, the costs are real | a table he trusts |
| 1 | add the missing xTB row | the accounting discipline; one definition for all rungs | §3 complete |
| 2 | error-vs-compute frontier on one dataset, escalation at random as the baseline | that random is the bar, not a formality | the frontier |
| 3 | one acquisition rule against that baseline: by predicted error, by rung disagreement, by cost-normalised gain | what reducible uncertainty buys, if anything | the thesis result |
| 4 (optional) | couple to a planner decision | that a model matters only up to a decision threshold | the coupling |

**Honest statement to make to him at the outset**, since his own scoping document insists
on it: this may confirm a negative. "When does escalation pay, and how do you know in
advance" is a better thesis than a marginal win, but he should be told now.

## 7b. Reframing (2026-09-23) — epistemic/aleatoric unifies both scope changes

Aymen independently found Zhong 2025's own code repo (`Chemlex-AI/bayesian-reactivity-prediction`)
and is reading toward BNNs on his own initiative. Owner's read, recorded here because it resolves
what looked like a second live framing competing with §1–7:

**It is the same underlying question, not a third one.** §1–7 frame the thesis as *reducible vs
irreducible error* on the oracle ladder (xTB/AIMNet2/DFT). That is the same split as *epistemic vs
aleatoric uncertainty* on the classification side (Zhong's BNN), one level of abstraction up:
- **Aleatoric / irreducible** lives in exactly one place in this whole program: the wet-lab HTE
  label itself. No amount of compute removes it.
- **Epistemic / reducible** is everything computational, including DFT. This is not asserted, it is
  *already measured*: the §3 routing finding (xTB vs AIMNet2-general indistinguishable; the gain is
  knowing which domain you're in, 14.40→4.73) is a model-applicability question, i.e. epistemic
  uncertainty about which regime a cheap model is trustworthy in — closed by a classifier, not by
  more compute. That is structurally identical to what a feasibility BNN's epistemic/aleatoric
  split is trying to isolate.

**One clean sentence for the thesis spine:** everything computational is epistemic and reducible by
the right classifier or the right escalation; only the wet-lab label is aleatoric. Both scope
changes (injected-noise → oracle-ladder → uncertainty-representation) are the same question
answered at different rungs of the same stack, not a drift.

**Boundary, not to blur:** retro-fallback (Tripp 2024) was earmarked for retro-planning (SSP /
search-robustness — uncertainty consumed on the decision side). Aymen reading its uncertainty
*model* (ξf/ξb, SSP as a metric) is legitimate comparison material; building or extending its
*search algorithm* is retro-planning's territory, per the existing pool-vs-frontier line in
`thesis-A-relation-to-sisters.md`. Keep him on the definition, not the algorithm.

**Testing environment already exists.** `retro-pfn/xif/` reproduced Zhong's actual pipeline once
(their DRFP features, their `disentangle_uncertainty` acquisition, Suzuki k_fold_0) but only ran
their `Ensemble` and `MCDropout` — a weak, cheap approximate posterior, not their best model. Their
repo also ships `BNN_SVI`, `BNN_NUTS` (their actual epistemic claim rests on `BNN_NUTS`, scoring
.886/.87/.95 vs MCDropout's .83/.80/.90) and `DKLGP`, all untested by us. Running those through the
same comparison is the single named missing experiment (`docs/mechanistic/tvoi_surrogate_results.md`
line ~171: "Definitive test = run their BNN"). This is Aymen's well-bounded entry point — extend an
existing, working harness by the two/three model classes it's missing, not build anything new.

## 8. Open, and needing the owner

1. **Second scope change.** A → B is the right move on the evidence; it is still his
   second, and that has a cost in his time and confidence. Timing and framing are the
   owner's call.
2. **Repo.** The owner intends one. `Ayman/` is currently a folder inside this
   repository, not a repository — so creating one is a structural change with an
   enrolment consequence, and it should be decided deliberately, not as a side effect.
3. **Which option in §5** he is pointed at. Recommend (a) + stand-alone error model for
   the thesis body, with (b) as the optional final phase — it keeps him unblocked by
   anyone else.
4. **Whether check 3 of §6 runs first.** It can kill the coupling without touching the
   thesis, which is an argument for running it regardless.
