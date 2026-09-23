# Retrosynthesis tooling assessed on MU1700

**A blind run, the chemist's published route, and what the difference tells us**

V. Šmídl et al. · 2026-09-03 · target: MU1700, ALK1/2 chemical probe
Full routes and methods in the appendices.

*Written to be read by both sides. It records where the software was useful,
where it failed, and where the published route rests on knowledge the software
had no way to represent. Neither the software nor the chemist is the benchmark
here — the disagreements are the content.*

---

## 1. Method

MU1700 (C₂₆H₂₂N₄O, 31 heavy atoms, achiral, SA 2.57) was run through our stack
**blind**: no knowledge of its origin, its designer, or any published route.

| | |
|---|---|
| Planner | AiZynthFinder MCTS, USPTO template policy (± ringbreaker), 1000 iterations, depth 8 |
| Second planner | ReactionT5 (transformer) via syntheseus — **in flight**, not in this report |
| Stock | 313,458 purchasable eMolecules compounds; target excluded |
| Knowledge layer | ORD + patent index, 1,048,347 products |
| Scoring | 7 open-source AiZynthFinder route scorers |
| Diversity | tree edit distance (Genheden 2021) and intermediate-Tanimoto |

**The knowledge layer returned 0 hits for MU1700.** Every disconnection came from
a USPTO-trained model. The 2024 *J. Med. Chem.* paper is not in that corpus, so
Part I below is genuinely uninformed.

---

## 2. Part I — what the tools produced blind

**63 distinct routes**, 4–13 steps. Filtering with either diversity metric
collapses them to **13–26 genuinely different** strategies (16 pairs differed
only in which bromo-furopyridine they started from).

The consensus, stable across configurations:

> Buy a **bromofuro[3,2-b]pyridine**; brominate it with **NBS** to a dibromide
> (46 of 63 routes use NBS); install the quinoline and the
> 4-(piperazin-1-yl)phenyl group by **two Suzuki couplings**.

Best-ranked blind: two 5-step routes (ranks 3/4), found by 3 independent
configurations, best-in-set on `route_cost` (18.7) and `max_transform`.

**Two concerns we raised blind, before seeing anything:**

1. **Chemoselectivity is asserted, never reasoned.** The consensus route couples
   a *symmetric* dibromide `Brc1cnc2c(Br)coc2c1` — two C–Br bonds, one is
   selected, and nothing in the pipeline asks whether that selectivity is
   achievable.
2. **The protecting-group order is inverted** — deprotect the piperazine, then
   run the final Suzuki with a free secondary amine present.

A third, unresolved blind: **36 of 63 routes *build* the piperazine ring** from
bis(2-chloroethyl)amine and an aniline rather than buying it.

---

## 3. Part II — the chemist's actual route

From Němec *et al.*, *J. Med. Chem.* **2024**, 67, 12632–12659, Figure 1A
(verified via Crossref; V. Němec is first author). Six steps:

| # | transformation | conditions |
|---|---|---|
| 1 → 2 | iodination of 5-chloropyridin-3-ol | NaHCO₃, I₂, H₂O |
| 2 → 3 | Sonogashira + cyclisation → TMS-furo[3,2-b]pyridine | TMS-acetylene, PdCl₂(PPh₃)₂, CuI, Et₃N, dioxane |
| 3 → 4 | TMS removal | KF, MeOH |
| 4 → 5 | bromination at C-3 | 1. Br₂/CCl₄ 2. DBU/toluene |
| 5 → 6 | Suzuki at **C–Br** (quinolin-4-yl) | R³B(OR)₂, Pd, base |
| 6 → MU1700 | Suzuki at **C–Cl** (4-(piperazin-1-yl)phenyl) | R⁶B(OR)₂, Pd, base |

Three things our tools never did:

- **He builds the bicycle** from a cheap chloropyridinol rather than buying it.
- **He designs in orthogonal reactivity**: intermediate **5** is
  `Clc1cnc2c(Br)coc2c1` — **Br and Cl**, not Br and Br. The two couplings are
  chemoselective *by construction*, sequential and controlled.
- **He buys the piperazine** as the boronic acid.

Note intermediate 5 differs from our consensus dibromide by **one atom**. Our
tools found the right disconnection topology and the wrong halogen pattern — and
the halogen pattern is the entire point.

---

## 4. Did the software find this route independently? Much of it, yes.

**This section previously said "no". That was measured on a badly truncated
corpus and is corrected here.** The first runs were wall-clock-capped at 600 s
against a 1000-iteration request and returned 63 routes; run to their actual
budget the same blind configuration returns **867**. Nothing about the
configuration changed — no tuning, no knowledge of his route.

| overlap with the published route | 63-route corpus | **867-route (proper budget)** |
|---|---|---|
| his 6 steps reproduced exactly | 0 | **2** |
| his 10 molecules reached | 2 | **7** |
| routes that **construct** the bicycle | 1 (1.6 %) | **33 (3.8 %)** |
| routes with **orthogonal halogen handles** | 3 | **240 (27.7 %)** |
| TED to nearest of our routes | 13.57 | **8.89** |
| intermediate-Tanimoto to nearest | 0.504 | **0.213** |

Which of his molecules are reached matters more than the count. At proper budget
the software independently produces his compound **2** (the iodo-chloro-
pyridinol), **4** (6-chlorofuropyridine), **5** (the 3-bromo-6-chloro key
intermediate) and **6** (the quinolinyl-chloro intermediate) — the backbone of
his route — plus both of his boronic acids. What it does not reach is the
**Sonogashira leg**: compound **1**, compound **3**, and TMS-acetylene.

So the honest statement is now: **the software independently reproduces most of
his route's intermediates and its final two couplings, but not the way he builds
the ring system.** The route it favours still buys the bicycle; the 3.8 % that
construct it do so by a different disconnection.

The strategic agreement stands and is stronger than before: both arrive at
installing quinolin-4-yl and 4-(piperazin-1-yl)phenyl onto a **3,6-dihalo-
furo[3,2-b]pyridine** by two Suzuki couplings, and the closest route uses **both
of his boronic acids**.

## 5. Is the one-atom difference significant?

Our consensus intermediate `Brc1cnc2c(Br)coc2c1` and his `Clc1cnc2c(Br)coc2c1`
differ by one atom. The honest answer is **yes as a design principle, but our
version is unproven rather than proven wrong.**

**Why it matters.** Oxidative addition of Ar–X to Pd(0) follows I > Br > OTf ≫ Cl.
A **Br/Cl** substrate therefore has a wide, well-established reactivity window:
couple at C–Br under ordinary conditions, then force the C–Cl with a more active
catalyst. The selectivity is a property of the substrate, not of the conditions,
and it is standard medicinal-chemistry practice.

**Why our version is not automatically wrong.** In a **Br/Br** substrate the two
handles sit in electronically very different rings — C-3 on the electron-rich
furan, C-6 on the electron-poor pyridine. Positional selectivity is plausible and
may well work. But it is a narrower margin than a halogen difference, it depends
on conditions, and **nothing in our pipeline checked it or could have.**

So this is not "the software was wrong". It is: the software produced a substrate
whose viability turns on a selectivity question it cannot pose, while the chemist
chose a substrate where the question does not arise. **This is the single most
useful disagreement in the report, and one sentence from a synthetic chemist
settles it.**

For completeness: mixed Br/Cl species do appear in our output, in 3 of 63 routes
(ranks 50, 57, 59), all single-configuration and low-ranked. The concept is
present in the search space but marginal.

## 6. Where the two approaches genuinely differ in merit

Not all of this runs one way.

**In favour of the published route:** it engineers the chemoselectivity away, it
starts from four cheap and available materials, and it is demonstrated — the
compound exists.

**In favour of the software's routes, and this deserves a real answer:** both
bromofuro[3,2-b]pyridine regioisomers **are in the eMolecules catalogue today**.
If that bicycle is genuinely purchasable at a sensible price and scale, then
buying it and doing 2–3 steps may be faster and cheaper than four steps of ring
construction. The published route dates from work done years earlier, when
availability may have been different. **We do not know whether the software's
"just buy the core" strategy is naïve or simply newer**, and that is a question
for the chemist, not for us.

## 7. Where the tooling actually failed

### It is not a data gap
**All four of his starting materials are in our 313,458-compound stock**,
including 5-chloropyridin-3-ol and TMS-acetylene. His route was fully reachable.

### It is not a ranking gap
Scored with our own seven scorers and inserted into our 63:

| scorer | his value | rank among 64 |
|---|---|---|
| `n_precursors` | 4 | **#1** |
| `n_precursors_stock` | 4 | **#1** |
| `frac_in_stock` | 1.000 | **#1** |
| `route_cost` | 20.9 | #20 |
| `n_reactions` | 6 | #26 |
| `state_score` | 0.956 | #26 |
| `max_transform` | 6 | #34 |

**Had the route been generated, our ranking would have put it first on three
independent criteria.** We had been treating ranking as the weak link; on this
evidence it is not. The qualifier matters: this is one route on one molecule, and
it says the scorers would have surfaced *this* good route, not that they order
routes well in general.

### It is a search / prior gap, **not** a capability gap

This was originally written up as a generation gap. That was wrong, and a direct
probe of the single-step policy overturned it.

Asked point-blank for disconnections of his intermediates, the template policy
**does** propose constructing the ring system — every time:

| molecule | policy | best ring-forming disconnection | prior |
|---|---|---|---|
| **4** 6-chlorofuropyridine (his) | uspto+ringbreaker | rank 25 of 100 | 0.0027 |
| **4** same | **ringbreaker alone** | **rank 3 of 50** | **0.0454** |
| **5** 3-Br-6-Cl (his key intermediate) | uspto+ringbreaker | rank 11 of 100 | 0.0085 |
| our Br/Br dibromide | uspto+ringbreaker | rank 18 of 100 | 0.0040 |
| bare core | uspto+ringbreaker | rank 8 of 100 | 0.0049 |

And the specific disconnection matters. Under the `ringbreaker` policy, compound
**4** is disconnected at rank 38 to:

```
C[Si](C)(C)C#Cc1ncc(Cl)cc1O
```

— the TMS-alkyne on the chloropyridinol, i.e. **the uncyclised Sonogashira
product from Němec's own step 2.** The exact disconnection he used is present in
the template library and is proposed on request.

**So no amount of the route was unreachable in principle.** What happened is a
ranking problem inside the search: ring-forming disconnections carry priors around
0.003–0.009 while the Suzuki disconnections that dominate our 63 routes carry
priors one to two orders of magnitude higher. An MCTS with 1000 iterations over a
100-action branching factor never expands rank 25.

Two mechanisms compound it:

1. **Prior scale is not comparable across policies.** AiZynthFinder concatenates
   each selected policy's actions and raw priors *without renormalising*, and each
   policy's priors are normalised over its own template library. The same
   disconnection is rank 3 / prior 0.045 under `ringbreaker` alone and rank 25 /
   prior 0.0027 once uspto's templates are concatenated in front of it.
2. **A stock containing the bicycle makes buying it a local optimum** the search
   has no reason to leave.

**Tested, and the answer is priors — decisively.** Four jobs separated budget from
prior scale: 10,000 iterations at default weights, and 1,000 iterations with
`ringbreaker` priors scaled ×20 (plus ×20 and ×100 at 10,000). A
`--policy_weights` knob was added for the purpose.

| arm | outcome |
|---|---|
| `budget10k` — 10,000 iters, default priors | **TIMEOUT at 20 h** |
| `rbw20-10k` — 10,000 iters, ringbreaker ×20 | **out of memory at 18.8 h** |
| `rbw100-10k` — 10,000 iters, ringbreaker ×100 | **TIMEOUT at 20 h** |
| **`rbw20` — 1,000 iters, ringbreaker ×20** | **completed, 11.2 h** |

At the **same budget** that previously produced 1 core-constructing route in 63,
rescaling one policy's priors gives:

| | before (default priors) | after (ringbreaker ×20) |
|---|---|---|
| routes | 63 | **550** |
| routes that **construct** the bicycle | **1** | **505** |
| Němec's key intermediate `Clc1cnc2c(Br)coc2c1` reached | no | **yes** |
| TMS-acetylene (his Sonogashira reagent) reached | no | **yes** |
| mixed Br/Cl furopyridines | 3, all low-ranked | 6 |

**The strategic move went from vanishingly rare to dominant without spending a
single extra iteration** — and every arm that tried to buy the same outcome with
10× the budget failed to finish. So §7's heading is right and the mechanism is
now identified: the two-policy concatenation puts independently-normalised priors
on one scale, and that, not search effort, is what buried the disconnection.

**Two honest limits.** We still do not reproduce Němec's route: his compounds
**1**, **2** and **4** remain unreached, and the planner builds the bicycle by a
different disconnection (`C=C(Cl)C=O` + an aminofuran, a ring-forming
condensation) rather than his Sonogashira/cyclisation. And 505 of 550 routes
constructing the core is as suspicious as 1 of 63 was — a ×20 thumb on the scale
is a hyperparameter we chose to make a known answer appear, not a calibration.
The honest statement is that the *strategy* is reachable and prior scale controls
whether it is reached; **the weight itself needs to be set by something principled
before any of these 550 routes is quoted.**

### The "representation gap" claim is withdrawn
This section previously argued that nothing in our stack has any notion of
orthogonal halogen reactivity, on the evidence that only 3 of 63 routes used a
mixed Br/Cl handle. At proper budget **240 of 867 routes (27.7 %) carry
orthogonal halogen handles on the core**. The planner reaches that design
routinely; it was the truncated corpus that hid it.

What survives is narrower and still true: **no scorer among the twenty available
rewards it**, and it is not a route-topology property, so the tree-based diversity
metrics cannot see it either. The tools *propose* orthogonal handles; nothing in
the stack knows to *prefer* them, so they are not surfaced to a user.

### It answers the two questions we had drafted for him
- **Buy or build the piperazine?** He buys it, as the boronic acid. Our **36 of
  63** build-it routes do not match practice. Whether double alkylation of an
  aniline would *work* here is a separate question we cannot answer; what we can
  say is that no chemist chose it.
- **Which bromo-furopyridine?** The question was malformed — he starts from
  neither, because he constructs the bicycle.

---

## 8. What we will change

1. **Fix the precedent scorer.** `avg_template_occurrence` returns 0.000 for all
   63 routes because our pipeline discards template-occurrence metadata. It is the
   one available scorer measuring literature precedent — plausibly what a chemist
   weights most — and it is dead by our own bug.
2. **Report a build-vs-buy axis.** "Does this route construct the core scaffold?"
   is a one-line property, was true for 1 of 63 routes, and would have surfaced
   the relevant one immediately.
3. **Put policy priors on a common scale before they reach the search.**
   Concatenating raw priors from independently-normalised policies is what buries
   ring-forming disconnections (§7). A `--policy_weights` knob now exists; a
   principled renormalisation should replace it.
4. **Report a scaffold-construction flag** per route, and check it is not empty —
   1 of 63 should have been a visible warning, not something we found by
   comparison with a paper.
5. **Do not invest further in route *ranking*** on current evidence. The evidence
   points at what the search *expands*, not at how the results are ordered.

---

## 9. Open questions — for the chemist, not for us

These are the points where the software's output is undecidable from our side and
one sentence of chemical judgement settles it.

0. **Nothing here is settled until the prior/budget experiments return** (§7).
   The conclusion that the tooling "missed" this route may weaken to "was
   configured badly", which is a much more fixable finding.
1. **Would a sequential Suzuki on the symmetric Br/Br dibromide work?** (§5) If
   positional selectivity between the furan C-3 and pyridine C-6 is reliable, a
   large part of our route set becomes viable and shorter than the published
   route. If not, that set is dead and we have learned the single most useful
   constraint of this exercise.
2. **Is the bromofuro[3,2-b]pyridine core practically purchasable?** (§6) It is in
   the catalogue we search. If it is genuinely available, "buy the core" is a
   legitimate modern strategy rather than a naïve one.
3. **Would you ever build the piperazine on the molecule?** 36 of our 63 routes do.
4. **What would you have wanted the software to show you** that none of the seven
   scorers reports? Our best guess is literature precedent per step, which we
   currently compute as zero through a bug of our own (§8).

---

## 10. Limits of this assessment

Single molecule, and an easy one — achiral, well-precedented Suzuki chemistry.
The ReactionT5 arm is still running and is not included. ASKCOS is not installed
and is not represented. No reaction conditions, no computed barriers, and no
experimental validation anywhere in this report. The comparison rests on one
published route by one chemist; it shows our tools missed *his* solution, not
that the 63 alternatives are unworkable.

---

## Appendices

- [**A** — Němec's published route](APPENDIX-A-nemec-route.md), full structures, SMILES and conditions
- [**B** — our top-ranked routes](APPENDIX-B-our-routes.md), full trees, plus the one route that builds the bicycle
- [**C** — scorer values for all 63 routes](APPENDIX-C-scores.md)
- [**D** — diversity metrics](APPENDIX-D-diversity.md): thresholds, agreement, distance to his route
- [**E** — provenance](APPENDIX-E-provenance.md): environments, code fixes, reproducibility caveats
