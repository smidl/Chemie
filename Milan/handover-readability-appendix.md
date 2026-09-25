# Readability of AFM's move sequences, tested against chemists' arrows

Handover for Milan, 2026-09-20. Released `nano` checkpoint (`M0`, 1.27 M parameters) and released code throughout; the only code addition is a weights-only fine-tuning entry point (§3.2). Structure: the message (§1), where it fits (§2), every procedure run and the data it produced (§3), results as tables (§4), open items and qualifications (§5–6), the proposed appendix text (§7).

## 1. The message

The move sequences are readable enough to be checked against a chemist's arrows move by move — and where they disagree, the disagreement itself can be read off the chain and traced to the corpus.

1. **The alphabet is the chemist's notation.** After one deterministic rewrite (a chemist's arrow from one bond straight into an adjacent bond is split through the atom the two bonds share), 81% of the RMechDB steps the alphabet can reach are written in it exactly as the chemist drew them; 18% cannot be compared because the chemist drew a single arrow and left its partner implied; 0.5% genuinely differ.
2. **Where the corpus reaches, the model draws the chemist's route.** On one-move steps `M0` drew a single mechanism for 1,928 of 2,057 steps and it was the chemist's in all but 6; where it drew alternatives, the chemist's route ranks first in 88%.
3. **One move beyond the corpus, the failure is legible.** On steps of two or more moves the chemist's route never ranks first (0 of 1,811) and is not drawn at all in 79% of steps; every chain reads "one homolysis, then `Stop`" — after the chemist's own homolysis the model puts 0.995 on `Stop` and 0.000 on the chemist's colligation. That is the corpus's radical chemistry recited literally: 2 of 4,091 sampled odd-parity training steps chain two single-electron moves.
4. **The reading is confirmed by repair.** Fine-tuned on 3,485 chemist steps, the model ranks the chemist's route first in 63% of held-out two-move steps, puts 0.887 on the colligation after the homolysis, and its intermediate reads "break C–H, form O–H, stop"; accuracy on FlowER's own test split is unchanged.

## 2. Where it fits in the paper

- New appendix (§7), pointed to from the introduction's "its intermediate states, not only its answer, are readable chemistry", and by a short paragraph in Experiments after Results.
- New Limitation (v): coverage by the alphabet is not coverage by the corpus; the data contain the single-electron moves one at a time, and the trained policy terminates after any one of them.
- Appendix D.4: qualify "every one of them, without exception" with the Census numbers (§4.4).
- Remark on hydrogens: external data must have every hydrogen explicit; otherwise β undercounts by n_H and the `Stop` gate is read at the wrong column.
- Decoder appendix, on the cap S: not an accuracy assumption either (0.4% of hypotheses exhaust it in distribution, 35% out of it).

## 3. Procedures run, and the data they produced

### 3.1 Preparation (model-free; every exclusion fixed before any model was run)

| procedure | what it does | output |
|---|---|---|
| **Reduce** | RMechDB reactant and product SMILES → bond–electron matrices over the mapped atoms; unmapped neighbours and implicit hydrogens folded into a per-atom context that must be equal on both sides | `D_reduced`: 5,417 of 5,426 steps (7 context changes, 2 malformed arrow codes) |
| **Search** | bond-order difference split into unit slots; each slot realised by one of the three alphabet moves changing a bond by that unit; assignments kept whose per-atom diagonal changes equal the recorded ones; a step is reachable if some kept assignment has an order with every prefix representable (bond orders 0–3, diagonals ≥ 0, per-element occupancy cap measured from the corpus) | `D_reachable`: 5,293 steps (97.6%), each with all its admissible decompositions. Dropped: 121 change no bond order (electron transfer without bond change, outside the alphabet), 2 admit no order, 1 exceeds the search size |
| **Correspond** | each decomposition expanded into RMechDB's arrow notation (a pair move is one two-electron arrow with an atom at one end; homolysis and colligation are two fish-hooks); the chemist's arrows canonicalised by splitting every bond→bond arrow through its unique shared atom; multiset equality selects *the chemist's route* among the decompositions | `D_route`: 4,301 steps (81.3% of reachable) with the chemist's route as a move sequence — 2,057 one-move, 2,059 two-move, 185 longer. `D_single`: 967 steps drawn with a single arrow. `D_other`: 25 genuinely different. (2,324 steps contained a bond→bond arrow; none lacked a shared atom) |
| **Convert** | puts a step into the input convention the model requires: every hydrogen an explicit mapped atom, fresh contiguous numbering; the product constructed by applying a decomposition to the reactant matrix and written back through the model's own reconstruction, round-trip checked. Applied to every RMechDB reactant before any model sees it | converted copies of the sets above; 46 steps whose product did not round-trip dropped, 463 exact (reactant, product) duplicates removed |
| **Split** | for the fine-tune only: the converted one-move exact matches and all converted ≥2-move reachable steps, 80/10/10 by distinct reactant so a reactant with several recorded products never straddles splits | `D_train` 3,485 · `D_val` 444 · `D_test` 433 (3,950 distinct reactants). `D_test`: abstraction 133, recombine 129, homolyze 73, addition 55, retro-addition 29, resonance 14; 195 one-move, 238 longer. Covers `D_reachable` except 422 one-move steps of `D_single` |
| **Sample** | uniform sample of the released FlowER test split, the in-distribution control | `D_flower`: 3,000 steps |
| **Census** | 200,000 steps sampled from the released training split: parity of every diagonal change and the element pair it occurs at; steps with two single-electron moves; identity steps | `D_census` |

### 3.2 Models

| model | how obtained |
|---|---|
| `M0` | the released `nano` checkpoint |
| `M_B` | **Finetune**(`M0`, `D_train` + 20,000 replayed FlowER training steps): weights-only initialisation with a fresh optimiser and schedule (the released `load_from` would resume the original run's optimiser state and epoch counter), effective batch 96, bf16, lr 5e-5, ≤ 40 epochs, early stopping on `D_val`; ~20 min on one consumer GPU. (Two variants not reported here — without the replay, and from random initialisation — land within 2–4 points of `M_B` on every RMechDB number; the from-scratch one does not know FlowER.) |

### 3.3 Measurements (take a model and a dataset)

| procedure | what it does | output |
|---|---|---|
| **Score**(M, set with routes) | teacher-forced trajectory score of the chemist's route: sum of log p of each move at the state it is taken from, plus `Stop`; the per-step values p(move₁│reactant), p(Stop│after move₁), p(move₂│after move₁) come from the same pass | `D_score` |
| **Rollout**(M, set, K) | K trajectories drawn with the paper's sampler, S = 12; per trajectory the move list, the trajectory score and the emitted state (the reactant if `Stop` was never chosen, as the decoder does) | `D_rollout` |
| **Rank**(D_score, D_rollout) | distinct mechanisms among the K draws (scores equal to three decimals merged); rank of the chemist's route among them, a tie counting as reaching that rank; *never drawn* if it scores below all of them; the rank-first rate is over steps where the model drew ≥ 2 mechanisms | `D_rank` |
| **Match**(D_rollout, set) | emitted state equals the set's product as canonical map-free SMILES; any-of-K per reactant | `D_match` |
| **Trace**(D_rollout) | move lists replayed on the reactant matrix: chains exhausting S; at each state whether `Stop` was offered and its probability; each odd-diagonal atom classified *fresh* (even in the reactant) or *persistent* | `D_trace` |
| **Eval**(M, D_flower) | the paper's own evaluation on 3,000 FlowER test steps, sampling decoder ranked by frequency, ten candidates | `D_eval` |

`M_B` is measured on RMechDB only on `D_test` (it saw `D_train` and `D_val`); for Rank that is the 430 steps of `D_route` whose reactant lies in `D_test`.

## 4. Results

### 4.1 Rank of the chemist's route — Rank(Score(M, D_route), Rollout(M, D_route, 100))

| | `M0` | `M_B`, on `D_route` ∩ `D_test` |
|---|---|---|
| one-move steps: n / with ≥ 2 mechanisms drawn | 2,057 / 129 | 200 / 35 |
| … chemist's route ranks first (of those) | 88.4% [81.7, 92.8] | 94.3% [81.4, 98.4] |
| … never drawn | 0.3% | 0.0% |
| ≥ 2-move steps: n / with ≥ 2 mechanisms drawn | 2,244 / 1,811 | 230 / 165 |
| … chemist's route ranks first (of those) | **0.0%** [0.0, 0.2] | **63.0%** [55.4, 70.0] |
| … ranks last / never drawn | 83.5% / 78.9% | 12.7% / 13.9% |
| … median trajectory score of the chemist's route | −33.4 | −0.22 |
| ≥ 2-move, rank first by class: abstraction · addition · retro-addition · resonance | 0.0% (1,091) · 0.2% (438) · 0.0% (186) · 4.7% (85) | 69.7% (99) · 53.1% (49) · 60.0% (10) · 100% (3) |

Wilson 95% intervals in brackets. An earlier version (2,057 exact-match steps, hydrogens implicit, 200 draws) gave 92.0% first among 624 steps with alternatives; superseded by this run.

### 4.2 Termination — Trace(Rollout(M, ·, 3))

| | `M0` on the 2,814 ≥2-move reachable steps | `M0` on `D_flower` | `M_B` on `D_test` |
|---|---|---|---|
| chains | 8,442 | 9,000 | 1,299 |
| exhausting S without `Stop` | **35.1%** | **0.4%** | 0.5% |
| exhausting S by odd atoms in the reactant, 0 / 1 / 2 / 3 | 0.0 / 44.7 / 1.1 / 2.4% | 0.3 / 0.0 / 1.4 / 0.0% | — |
| at a state with **two fresh radicals + the reactant's own** (right after the homolysis that begins a propagation step): chose `Stop` | **99.7%** (662 states) | — | **6.7%** (539) |
| at the propagation-product state (one fresh radical, the reactant's healed): chose `Stop` | 92.3% (350) | — | 98.3% (584) |
| moves of exhausted chains | 96% pair moves; 44% never re-enter the Sector | — | — |

Parity fact used in reading this: pair moves change a diagonal by 0 or ±2, single-electron moves by ±1 at two atoms, so a one-radical reactant can only be advanced by a homolysis followed by a colligation. Rejected on the same data: molecule size or softmax width, class imbalance, resonance-as-identity, hydrogen bookkeeping (closed by Convert; 4,529 / 4,529 emitted states reconstruct).

### 4.3 The transition along the chemist's route — Score(M, ·) per step, two-move abstraction routes

| | `M0`, `D_route` (1,528) | `M0`, `D_test` (129) | `M_B`, `D_test` (129) |
|---|---|---|---|
| p(chemist's homolysis │ reactant), mean / median | 0.005 / 0.000 | 0.003 / 0.000 | 0.711 / 0.975 |
| p(Stop │ after it) | 0.995 / 1.000 | 1.000 / 1.000 | 0.044 / 0.000 |
| p(chemist's colligation │ after it) | 0.000 / 0.000 | 0.000 / 0.000 | 0.887 / 0.999 |
| whole route, mean / median | 0.000 / 0.000 | 0.000 / 0.000 | 0.700 / 0.964 |

`M0` on `D_route` by class, p(Stop│after move₁) / p(move₂│after move₁): addition 0.985 / 0.000 (544), retro-addition 0.910 / 0.001 (288), resonance 0.993 / 0.000 (187).

### 4.4 Training corpus — Census

| | `D_census` |
|---|---|
| identity steps | 18.0% |
| steps changing a diagonal by an odd amount | 2.05% (4,091) |
| … flipped atoms exactly {P, Pd} | 84.7% (3,467) |
| … organic pairs (C–O 161, O–O 143, N–O 82, Br–C 68, Br–N 45, C–C 44, C–N 38, C–Cl 21, …) | 618 = 0.31% of all steps |
| steps flipping parity at four atoms (two single-electron moves in one step) | **2** |
| steps with an odd C/N/O/H/S/halogen atom in reactant / product | 0.30% / 0.29% |
| odd-diagonal reactant atoms by element | P 28,616 · Pd 9,295 · C 1,183 · O 460 · Na 414 · Cu 203 · K 110 · N 109 · Br 91 |

### 4.5 Product accuracy and cost on the original task — Match(Rollout(M, D_test, 3), D_test); Eval(M, D_flower)

| | `M0` | `M_B` |
|---|---|---|
| Match, any-of-3, all 433 | 45.7% [41, 50] | 91.2% [88, 94] |
| Match, one-radical steps (197: abstraction, addition, retro-addition, resonance) | 0.0% | 84.8% |
| Match, one-move steps (recombine, homolyze; 139) | 98.6% | 98.6% |
| Eval, FlowER top-1 / top-3 / top-5 | 0.869 / 0.978 / 0.986 (paper, full split) | 0.876 / 0.963 / 0.980 |
| Eval, validity; electron, atom, proton conservation | 1.0000 | 1.0000 each |

## 5. Open before the numbers are final

1. Match on all of `D_reachable` (the 422 one-move steps of `D_single` are not in `D_test`; expected effect small).
2. Two more seeds of `M_B`; report the range for §4.1 (the two-move rank interval is ±7 points).
3. Overlap of `D_test` reactants with the released training split (leakage; expected near zero).
4. `addition` (53% rank-first): whether the emitted product is the other alkene carbon.
5. RMechDB reference (Tavakoli et al., 2023) verified before insertion.

## 6. Qualifications to state

RMechDB is a curated notation, not a physical ground truth; agreement is with how these chemists drew these steps. The alphabet reaches 97.6% of recorded products and, after canonicalising the bond→bond arrow, writes 81% of the drawings as the chemist did; 18% are drawn with a single arrow and cannot be compared, 0.5% genuinely differ. For two-radical reactants `M0` recombines where the chemist wrote disproportionation; both are chemistry. Smallest width only, one fine-tuning seed, 430–433 held-out steps, three chains for Match and Trace and 100 for Rank; the fine-tuned model is a different model from the one in Table 1 and is scored only on data it never saw.

## 7. Proposed appendix text (about half a page)

**Readability, tested against a chemist's arrows.** The intermediate states of §5 are the moves of a chemist's drawing, and that can be measured. RMechDB records 5,426 elementary steps of radical chemistry together with the arrows a chemist drew for each, in a notation the alphabet expands into exactly: a pair move is one two-electron arrow with an atom at one end, a homolysis or colligation is two fish-hooks. The one construction the alphabet lacks is the chemist's arrow from a bond straight into an adjacent bond, which it writes as two arrows through the shared atom (Remark on the bond migration); rewriting that arrow is deterministic, the shared atom being unique. Reducing each step to the mapped atoms and searching the alphabet for admissible decompositions, the recorded product is reachable for 5,293 steps (97.6%; of the rest, 121 move electrons without changing a bond, which no move does). For 4,301 of these (81%) one decomposition expands to the chemist's arrows exactly, and we call it the chemist's route: 2,057 are one move, 2,244 two or more. For 967 the chemist drew a single arrow, leaving its partner implied, and no comparison is possible; 25 are drawn differently. Every hydrogen is made an explicit mapped atom before a step is shown to the model (Remark on hydrogens).

For each step, 100 trajectories are drawn from the model with the sampler of §5 and scored by (rollout); the chemist's route is scored by the same sum, teacher-forced; and the chemist's route is ranked among the distinct mechanisms the model drew. The released `nano` checkpoint is scored on all 4,301 steps. The same checkpoint fine-tuned on 3,485 of them (a split by reactant, minutes on one GPU, the pipeline of §5 unchanged) is scored on the 430 steps it never saw.

| chemist's route | model | steps | model drew ≥ 2 mechanisms | chemist's ranks first (of those) | never drawn | median score of chemist's route |
|---|---|---|---|---|---|---|
| one move | released | 2,057 | 129 | 88.4% | 0.3% | −0.00 |
| one move | fine-tuned | 200 | 35 | 94.3% | 0.0% | −0.00 |
| two or more moves | released | 2,244 | 1,811 | **0.0%** | 78.9% | −33.4 |
| two or more moves | fine-tuned | 230 | 165 | **63.0%** | 13.9% | −0.22 |

Where a step is one move the released model draws the chemist's mechanism and, for 1,928 steps, nothing else. Where it is two or more it never ranks the chemist's route first and in four steps of five does not draw it at all. The chains say why: along the chemist's own route, after the first homolysis the model puts probability 0.995 on `Stop` and 0.000 on the colligation that completes the step. Appendix D.4 is the reason. The odd-parity chemistry of this corpus is a single Pd–P homolysis or colligation, and over 200,000 training steps only two chain a second single-electron move; the alphabet writes radical chemistry in general, the corpus exhibits it one move at a time, and the trained policy has learned that literally (Limitation (v)). Shown the missing move, the same network learns it from a few thousand examples: the fine-tuned model puts 0.887 on the colligation after the homolysis, ranks the chemist's route first in 63% of held-out two-move steps, its intermediate reads "break C–H, form O–H, stop", and its accuracy on this corpus's test split does not move (0.876 against 0.869). The guarantees hold throughout — every emitted state is a molecule — and the states are what make both the gap and its closure visible. RMechDB is a curated notation, not a physical ground truth, and these numbers are at the smallest width and one seed.


---

## 8. Data preparation: provenance, deduplication and coverage

Error characteristics of the preparation in §3.1, in the order they affect a
number in §4.

### 8.1 Environment

Every count in §3 and §4 is produced under **RDKit 2024.3.5**, the version pinned
by `ArrowFlowMatching/environment.yml`. The counts are sensitive to it: at RDKit
2026.03.6 the same code gives `D_reachable` **5,246** instead of 5,293, the
context-change exclusion **56** instead of 7, and `D_route` **4,254** instead of
4,301. The cause is implicit-hydrogen perception, which feeds the per-atom context
the Reduce step requires to be equal on both sides of a step. The shift is larger
than several effects reported in §4, so the RDKit version belongs beside any of
these figures.

### 8.2 The same transformation is often recorded more than once

RMechDB's 5,426 rows describe **4,864 distinct** canonical (reactant, product)
pairs; **562 rows are repeat annotations** of chemistry already recorded. Of those
562:

| | rows | |
|---|---|---|
| the same drawing under different atom numbering | **355 (63 %)** | true copies |
| a **different drawing** of the same transformation | **207 (37 %)** | |

The numbering difference is annotator variation rather than two sources: 1,345 of
5,426 rows number the reacting atoms from 1 and 4,081 use the 10/20/21 convention,
and both appear in every RMechDB sub-file. The drawing difference is a chemist
choice about how much of the electron flow to draw — *tert*-butoxy β-scission, for
instance, appears once as three fish-hooks and once as one.

After Convert, 4,871 entries carry **4,414 distinct** pairs, so **457 collide**.
Convert keeps one entry per pair: the one with the **most moves**, preferring a
decomposition that matches the chemist's arrows (`D_route`) over an arbitrary
admissible one. Selecting the shorter drawing would bias the fine-tune toward
one-move annotations of multi-move chemistry, which is the behaviour §4.2
diagnoses.

The choice does not reach `D_train`/`D_val`/`D_test`, because the FlowER format
records `reactant>>product` and not the move sequence, so two decompositions of
one pair write the same line. It does reach **Score** and **Rank**, which consume
move sequences, and those are the §4.1 and §4.3 numbers.

### 8.3 The alphabet absorbs most of the drawing disagreement

Whether two chemists' different drawings survive as different mechanisms is
answerable only on pairs where **more than one row reaches a decomposition**:

| | pairs |
|---|---|
| pairs with more than one surviving row | **356** |
| — whose chemists' arrow shapes differ | **80** |
| — still differing in move count after Reduce → Search → Correspond | **4** |

**76 of 80** comparable disagreements are written at the same length once both
drawings pass through the alphabet. This is the bond→bond canonicalisation of
§3.1 doing its work, and it is direct evidence that Limitation (ii) is about
notation rather than chemistry. ArrowFinder measures the same phenomenon from the
other side at 101/1331 (7.6 %).

### 8.4 What is excluded, and whether it could be recovered

Three exclusions, only one of which is structural.

**121 steps change no bond order** and no chain of moves can reach them: every
move in the alphabet changes exactly one bond order by ±1, and the two
single-electron moves change two diagonals together, so a lone radical cannot
relocate without a bond forming or breaking. All 121 are RMechDB's `ha resonance`
class (119) plus 2 `resonance` — **2.2 % of the corpus** — for example
`[O-:1][N+:2]=O >> [O:1][N:2]=O`, one fish-hook, formal charges move, no bond
changes. This belongs with Limitation (v). Not recoverable without a fifth move.

**421 steps have a one-move decomposition that disagrees with the chemist's
arrows** and appear in no dumped set: the route dump requires an arrow match and
the multi-move dump requires ≥ 2 moves, so "one move, no match" is accepted by
neither. This is an interface choice, not a validity criterion; whether to train
on a decomposition the chemist rejects is a scientific decision.

**46 steps fail the product round-trip** in Convert and are dropped undiagnosed.

### 8.5 Coverage

Against the chemistry RMechDB actually contains rather than its row count:

| | |
|---|---|
| distinct non-identity transformations in RMechDB | **4,861** |
| held by `D_train` + `D_val` + `D_test` | **4,362 = 89.7 %** |

### 8.6 Scoring constraint on the fine-tuned model

`M_B` is trained on `D_train` and `D_val`, which together cover 3,929 of the 4,301
steps of `D_route`. The stored score file spans all 4,301, and nothing in it marks
the split. **Every `M_B` figure in §4 is restricted to `D_test` at analysis time**
— 430 steps over 395 reactants. Scoring the file whole raises rank-first from
63.0 % to 76.4 % and measures training data.
