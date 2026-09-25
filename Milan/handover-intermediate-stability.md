# Are AFM's intermediate states molecules, and are they stable ones?

Handover for Milan, 2026-09-18. Companion to the readability note; same released `nano` checkpoints (AFM and DiscreteFlowER), same released code.

## What the paper claims, and what is measured here

Proposition 2 guarantees that the *emitted* state is in the Sector, hence a molecule for the checker. Limitation (iii) says the intermediate states "conserve electrons and are representable, but need not be molecules, since the table gates only the stop move"; the bridge appendix shows book-keeping intermediates (a hydrogen bonded to two atoms, a carbon holding four and a half pairs) and says these are "not claims about a reaction coordinate". The question here is quantitative: of the states a self-sampled chain actually passes through, how many are molecules, how many can be built in three dimensions, how strained are they, and does the guarantee on the emitted state hold on data the model never saw. DiscreteFlowER, same body and featurisation with no admissibility on intermediates, is the control for "would any model's intermediates look this way".

## Method

For each reactant, three chains are sampled from the model with the paper's sampling decoder (S = 12 moves for AFM; 10 Euler steps for DiscreteFlowER). Every state along a chain is scored in four tiers, kept apart:

1. **In the Sector** — the `Stop` class was offered at that state, the paper's own operational "is a molecule". (AFM only; DiscreteFlowER has no Sector.)
2. **Reconstructs** — the released reconstruction turns the matrix into a molecule the checker reads back.
3. **Embeds** — RDKit ETKDGv3 (fixed seed, random coordinates) produces a 3D conformer.
4. **Force field converges** — MMFF94 where parameters exist, else UFF, 500 iterations, converged flag; the minimised energy per heavy atom is recorded as a strain proxy.

Positions: *intermediate* = every state after a move except the last one of a chain that chose `Stop`; *emitted* = the state a stopping chain emitted. A chain that exhausted S has no emitted state (the decoder returns its last stoppable state, which for wandering chains is the reactant). Chains that stopped at once (zero moves) are counted but have no states to score.

Data: 1,000 reactants sampled uniformly from the released test split (in distribution; molecules of 60–150 atoms); the 433 held-out RMechDB test steps of the readability note (out of distribution for the released model, 15–30 atoms), scored for the released model and for fine-tune B.

## 1. In distribution: released test split, 1,000 reactants

### 1.1 AFM

3,000 chains; 558 stopped at once, 2,442 took moves: 1 move 134, 2 moves 1,693, 3 moves 257, 4 moves 196, 5–12 moves 162, of which 9 exhausted S.

| states | n | in Sector | reconstruct | embed | FF converges |
|---|---|---|---|---|---|
| intermediates, all | 3,822 | 30.9% | 59.4% | 59.2% | 34.8% |
| — after move 1 | 2,308 | 10.8% | 52.8% | 52.4% | 32.7% |
| — after move 2 | 615 | 79.3% | 82.0% | 82.0% | 41.6% |
| — after move 3 | 358 | 38.5% | 60.3% | 60.3% | 29.6% |
| — after move 4 or later | 541 | 56.4% | 61.4% | 61.4% | 39.6% |
| — in chains that exhausted S | 108 | 51.9% | 61.1% | 61.1% | 39.8% |
| emitted states | 2,433 | 100.0% | 100.0% | 100.0% | 63.7% |

Cross-tabulation of the intermediates: in Sector and reconstructs 1,180; not in Sector yet reconstructs 1,090; neither 1,552; in Sector and fails to reconstruct **0** — the table and the reconstruction agree exactly, as they are built to. The 1,090 are the paper's book-keeping intermediates that the checker happens to accept (a carbocation and a carbanion after a bond→lone, for instance); the 1,552 are the ones it does not (a hydrogen with two bonds, a five-coordinate carbon).

The position profile is the migration signature of the bridge appendix: the typical two-move step is bond→lone then lone→bond, and the state between them, a pair parked as a lone pair, is a molecule in 11% of cases; after the second move the chain is back in the Sector 79% of the time.

### 1.2 DiscreteFlowER (control)

3,000 chains of 10 Euler steps; every step scored.

| states | n | reconstruct | embed | FF converges |
|---|---|---|---|---|
| Euler step 1 | 3,000 | 84.9% | 84.9% | 57.2% |
| step 2 | 3,000 | 74.5% | 74.5% | 49.4% |
| step 3 | 3,000 | 66.9% | 66.9% | 44.2% |
| step 4 | 3,000 | 62.2% | 62.2% | 41.0% |
| step 5 | 3,000 | 59.6% | 59.6% | 38.9% |
| step 6 | 3,000 | 60.8% | 60.7% | 39.4% |
| step 7 | 3,000 | 64.2% | 64.1% | 41.6% |
| step 8 | 3,000 | 70.9% | 70.8% | 46.1% |
| step 9 | 3,000 | 81.5% | 81.5% | 52.6% |
| all intermediates | 27,000 | 69.5% | 69.5% | 45.6% |
| emitted (step 10, arg-max) | 3,000 | 97.4% | 97.3% | 63.1% |

The U-shape is the entrywise bridge: early steps have switched few entries and are nearly the reactant, late steps nearly the product, and the middle carries the wrong electron count. 30.8% of DiscreteFlowER's intermediate states are string-identical to the chain's own emitted product. Its intermediate percentages are therefore not evidence of readable intermediates; the comparable row is the emitted one, where AFM's 100.0% against 97.4% is Proposition 2 against no guarantee.

### 1.3 Strain proxy

Minimised force-field energy per heavy atom (kcal/mol), over reconstructed states with parameters available (78–85% of states in distribution; the rest contain elements MMFF/UFF do not parameterise):

| | median | q25 | q75 |
|---|---|---|---|
| AFM intermediates | 1.67 | −0.65 | 2.72 |
| AFM emitted | 1.74 | 0.46 | 2.69 |
| DiscreteFlowER intermediates | 1.83 | 0.88 | 2.69 |
| DiscreteFlowER emitted | 1.75 | 0.58 | 2.73 |

Indistinguishable between intermediates and products and between models. The proxy does not separate a book-keeping intermediate from a molecule once both embed; the tier that does is the Sector / reconstruction one.

Force-field convergence at ~63% for both models' emitted states, which are all molecules, is entirely the 500-iteration cap, measured: re-minimising 159 MMFF-parametrised AFM emitted states with the same embedding, convergence is 100% below 40 heavy atoms, 74% at 40–79 and 0% at 80+ with 500 iterations, and **100% in every size class with 2,000** (fragment count irrelevant once size is fixed). "Not converged" here means "gradient threshold not yet met on a large molecule", not "strained"; on RMechDB's 15–30-atom molecules the same proxy converges at 95–97%. The convergence column therefore carries no chemical information beyond molecule size and should be dropped or re-run at 2,000 iterations before anything is quoted from it; the energy-per-heavy-atom medians are the informative part of this tier.

Conditional on reconstruction, the fair comparison across the two models (same 1,000 reactants): emitted states, AFM 76.0% converged given MMFF parameters, median 1.74 kcal/mol per heavy atom; DiscreteFlowER 76.5%, 1.75 — indistinguishable. AFM's reconstructing intermediates split into molecules (in the Sector: 80.7%, 1.84) and book-keeping states the checker accepts (71.5%, 1.62); DiscreteFlowER's into copies of its own product (44% of them; 79.0%, 1.73) and near-copies (77.2%, 1.88). A book-keeping intermediate embeds 99% of the time and minimises to a *lower* energy than a real molecule: the proxy grades geometry, not electron bookkeeping, and the readable tier is the Sector.

## 2. Out of distribution: RMechDB held-out test, 433 steps

| model | chains with moves | intermediates | in Sector | reconstruct | FF converges | emitted | emitted in Sector / reconstruct | emitted FF converges |
|---|---|---|---|---|---|---|---|---|
| AFM released | 1,221 (280 exhausted S) | 3,788 | 11.9% | 14.1% | 13.9% | 941 | 100% / 100% | 95.5% |
| AFM fine-tuned B | 1,297 (7 exhausted S) | 789 | 81.0% | 81.4% | 79.6% | 1,290 | 100% / 100% | 96.9% |

By position, released: after move 1 (430 states) 37% in Sector; after move 2 (384) 16%; after move 3 (358) 25%; later (2,616) 5%. In chains that stopped, intermediates are in the Sector 45% of the time; in chains that exhausted S, 8%. Fine-tuned B: after move 1 (681 states) 90% in Sector; the few chains that go longer than two moves degrade as before (68% / 25% / 9%). Cross-tabulation, in Sector but fails to reconstruct: 0 for both models.

Strain proxy on RMechDB (parameters available for 96–99% of states): released intermediates median 1.73 (q75 3.43), released emitted 1.19; fine-tuned intermediates 1.21 (q75 1.87), emitted 1.31. The fine-tuned model's intermediates are as unstrained as its products; the released model's wandering intermediates carry the high-strain tail.

Reading: the intermediate of a correctly executed two-move radical step (X• + H–C → after homolysis, three radicals) is a molecule for the checker and embeds; the released model's low numbers are the product of chains that never terminate, applying polar pair moves to a radical they cannot pair up (readability note §3). Proposition 2 holds without exception on new data once hydrogens are explicit (4,529 of 4,529 emitted states in the earlier full run; 941/941 and 1,290/1,290 here).

## 3. Earlier readings this supersedes

Two numbers circulated earlier are artefacts of counting: "final reconstructs 47–61%" counted the twelfth state of a chain that never chose `Stop` as an emitted product (such states reconstruct 2%); "mid-mechanism reconstructs 14–22%" on RMechDB measured intermediates of chains that were 87% out of distribution and wandering. Neither says anything about the construction.

## 4. What this supports, in the paper's terms

- The emitted state is a molecule on every sample, in and out of distribution (Proposition 2, measured: 2,433 + 941 + 1,290 + 4,529 of as many).
- In distribution, about a third of the states a chain passes through are molecules and three fifths reconstruct; the rest are the book-keeping intermediates of Limitation (iii), concentrated at the parked-pair state of a migration. The paper's wording is accurate and could carry the number.
- The control does not have readable intermediates in any useful sense: its high percentages are copies of endpoints.
- Force-field strain does not distinguish book-keeping intermediates from molecules; the Sector does. This is worth one sentence where Limitation (iii) is stated.

## 5. Open

1. Per-move-type breakdown of which intermediates leave the Sector (expected: the bond→lone half of every migration; homolysis intermediates should stay in) — one more replay.
2. A per-class in-distribution split (pericyclic, proton transfer, metal-centred) — the released data have no class labels; would need a template match.
3. Scaling the FF iterations, or a semi-empirical proxy (xTB), to remove the 63% convergence ceiling on large molecules before quoting a strain number.
4. A physical test of a small number of intermediates (DFT/NEB on one pathway) is the only way to speak about a reaction coordinate; the paper is right not to, and this note does not either.
5. More seeds and the full 3,000-reactant sample (only the first 1,000 were scored).
