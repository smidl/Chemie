# Problem 02 — Chains that never stop: the paper's odd-parity sector is one move deep, and the model has learned exactly that

Status 2026-09-18. Supersedes the "mid-mechanism gap" reading in
`problem01-validity.md` (see §0). All numbers: `afm_nano` checkpoint,
unmodified `models/afm.py` (`filter-only` lineage), sample decode, 3 chains
per reactant, `S = max_moves = 12`, RMechDB reactants in FlowER's own
convention (every hydrogen an explicit mapped atom, `fully_explicit_atom_map`).
Paper references are to `6aaa41c163a3372f92488d74/main.tex` by section label
and line.

## 0. What is settled before any hypothesis

**There is no reconstruction problem. There is a termination problem.**

| quantity | value | source |
|---|---|---|
| chains that chose `Stop` on their own → emitted state reconstructs | **4,529 / 4,529 = 100.0%** | `fully_explicit_stability.jsonl` |
| chains that hit the 12-move budget without ever choosing `Stop` | **2,960 / 8,442 = 35.1%** (35.7% in the earlier run) | `instrumented_rmechdb.jsonl` |
| the same roll-out on FlowER's *own* test reactants (3,000 × 3) | **35 / 9,000 = 0.4%** | `instrumented_flower.jsonl` |
| chains stopping at the reactant (identity), RMechDB / FlowER | 10.7% / **19.4%** (data: 18.5% identity steps, main.tex 861–862) | same |

Proposition 2 (validity, main.tex 714–719) holds exactly on the new data
once the input convention matches. The "final reconstructs 60.9%" of
problem01 counted the 12th state of a never-stopped chain as a "final
product" (those reconstruct 2.1%, as the paper predicts for book-keeping
intermediates), and every "mid-mechanism reconstruction" number measured
intermediates the paper explicitly does not claim to be molecules
(Limitation (iii), 962–963; Remark on migration 2645–2663; App. "Where the
table is checked" 3707–3717). Both were shadows of one fact: a third of the
chains never terminate, and under the paper's decoder they emit "the last
state at which [they were] allowed to stop" (842–843, 4180–4186) — for 44% of
them, the reactant itself.

The in-distribution control shows the decoder and the S=12 budget are sound
where the paper tested them ("at a mean of 2.24 moves per step the roll-out
usually terminates after three or four", 4261–4262: on FlowER we see 2 moves
as the mode and 0.4% budget exhaustion). Whatever stops the chains on
RMechDB is out-of-distribution behaviour of the *learned* policy, not of the
construction.

## 1. Review of the theory: what is guaranteed, and what is left to the policy

The construction, in the paper's own order:

1. **State space.** `Sector` (eq. sector, 671–677): one global linear
   equation `N(x) = N(B_r)`, site capacity `x_ij ≤ 3`, and `N` local
   conditions `(a_i, x_ii, β_i(x)) ∈ Tab`. `β_i` is a row sum because every
   hydrogen is explicit (Remark nh, 1441–1448) — the condition problem01
   restored by preprocessing.
2. **Alphabet.** Four moves (table at 539–550), each changing `(x_ii, x_jj,
   x_ij)` by `(δ^ii, δ^jj, δ^ij)` with `δ^ii + δ^jj + 2δ^ij = 0` (eq. rowsum,
   553). Two are pair moves (`±2` on one diagonal), two are single-electron
   moves (`±1` on both diagonals).
3. **Guarantees.** Prop. 1 (683–688): `N` is conserved surely. Prop. 2
   (714–719): a chain that may *terminate* only at `x ∈ Sector` terminates
   in `Sector`. Remark "closed under inversion" (2799–2807): no reachable
   state has an empty candidate list, so the masked softmax (eq. head,
   795–797) is always well defined.
4. **What `Tab` gates.** Only the `Stop` class (738–751, 3707–3717). Chosen
   so pericyclic jams dissolve; the price, stated: an intermediate "need not
   be a state the reconstruction would accept".
5. **Training.** The bridge is the family of prefixes of one pre-drawn
   admissible order (eq. movebridge, 771–772); `K ~ Unif{0,…,m}`; the
   target is the next move or `Stop` (eq. loss, 811–815). "Stopping is an
   ordinary class of an ordinary softmax … the model learns when the
   mechanism is over by the same mechanism it learns what to do next"
   (819–821). Fig. bridge caption: "the network is never asked at sampling
   time about a state it was never trained on" (4063–4065).
6. **Decoding.** Roll-out (eq. rollout, 828–832); `S = 12`; a hypothesis
   that has not stopped emits its last stoppable state (842–843); "the cap
   is a compute knob and not a correctness assumption" (4186).
7. **The odd-parity sector of the data.** App. "Single-electron moves"
   (2784–2797): 12.1% of test reactants carry an odd diagonal, on P (1379
   atoms), Pd (571), Na (34), Ce (16); 2.17% of steps change a diagonal by
   an odd amount, and "every one of them, without exception over 4000 test
   steps, is a single palladium–phosphorus bond breaking with one electron to
   each atom, or the same bond forming from two such electrons".
8. **Identity steps.** 18.5% of steps have `m = 0` and contribute only the
   `Stop` target (780–782, 4437).

What the theory does **not** promise, each a place a policy trained on (7)–(8)
can fail on data that violates them:

- **(N1) Reachability.** Prop. 2 is conditional on termination. Nothing
  bounds the number of moves to the next `Sector` state, and Remark
  inversion guarantees an *undo* exists, not that the policy assigns it
  mass. The fallback makes validity total; it says nothing about accuracy.
- **(N2) Off-bridge states.** The claim in 4063–4065 is true along the
  bridge. One sampled move that is not a prefix of any training order puts
  the chain in a state the network was never trained on, and the loss
  (811–815) contains no term that pulls it back (standard exposure bias).
- **(N3) A parity invariant the paper does not state.** From the alphabet
  table: pair moves change each `x_ii` by 0 or ±2, single-electron moves by
  ±1 on exactly two atoms. Hence the set of odd-diagonal atoms is *fixed*
  under pair moves, and its size changes by 0 or ±2 under single-electron
  moves. Corollary: a reactant with one radical centre can never reach a
  closed-shell state by any admissible chain, and the radical can only be
  moved by a homolysis–colligation pair. This is chemistry (spin is
  conserved), but it is also the exact reason the FlowER corpus contains no
  one-radical → one-radical step: its only odd chemistry is a single Pd–P
  bond, `0 → 2` or `2 → 0` radicals, `m = 1`.
- **(N4) The stop head is a learned function of the pooled molecule**
  (`models/afm.py` 791–798: mean-pool + max-pool + time embedding). The
  paper's guarantee is that `Stop` is *offered* only in `Sector`; when it is
  offered, the choice is the network's, trained on (7)–(8).
- **(N5) `Sector ⊋ chemistry`.** `Tab` admits every state the checker
  accepts (Remark algebraic, 3545–3555; hydrogen's non-staircase, 3536–3543;
  `C_a = ∞` for 45 elements, 3527). A state with three unpaired electrons is
  a valid emission.

## 2. Hypotheses, tests, status

Each hypothesis is stated with its anchor in the paper or code, a
falsifiable prediction, the test that decides it, and its status against the
runs in §3. "Confirmed"/"refuted" refers to these runs, at `nano`, 3 chains
per reactant.

### H1 — The odd-parity sector is out of training support (anchor: 2784–2797, (N3))
*Prediction.* The policy has never seen an organic radical, a `Stop` target
with one fresh radical, or a step with two single-electron moves. Failure
should concentrate on reactants whose reaction *requires* moving a radical
(exactly one radical centre in `B_r`), not on size, class label, or `n_H`.
*Tests.* (a) Corpus census on `train.txt` (`corpus_census.py`, RCI job
11645418): elements ever odd; element pairs of odd-Δ steps; `Stop` targets
with an organic odd atom. (b) Stuck rate by number of odd-diagonal atoms in
`B_r`. (c) `p(Stop)` by radical signature (fresh/persistent), `analyze_parity.py`.
*Status.* **Confirmed** by (b): stuck rate **0.0% / 44.7% / 1.1% / 2.4%** for
0 / 1 / 2 / 3 radical centres in the reactant (87 / 6,570 / 1,290 / 495
chains). Every other split — size (30–42%), reaction class, stage — is a
projection of this one: Initiation (0 → 2 radicals) 0.0%, Termination
(2 → 0) 2.1%, Propagation (1 → 1) 37.8%. (a) pending; the paper's own
test-split statement is what (b) predicts.

### H1′ — "One single-electron move is a whole step" (anchor: 2793–2795 + (N3); the sharp form of H1)
*Prediction.* After any homolysis the model puts ≈1 on `Stop`; a
homolysis→colligation route has ≈0 probability; the sampler emits
two-fresh-radical "products".
*Tests.* Teacher-force the chemist's two-move routes
(`teacher_forced_route.py`); parity table at sampled states; count emitted
states with two fresh radicals (`analyze_accuracy.py`).
*Status.* **Confirmed, decisively.** Teacher-forced, 1,528 `abstraction`
routes: at `x_1` (after the chemist's homolysis) **p(Stop) = 0.995 (median
1.000)**, **p(chemist's colligation) = 0.000**; whole-route probability
mean 0.0000. Addition 0.985/0.000, retroaddition 0.910/0.001, resonance
0.993/0.000. Sampled: at states with signature (2 fresh, 1 persistent) the
model chose `Stop` **660 / 662 = 99.7%**; 651 of 6,570 one-radical chains
(9.9%) emit a triradical. In the FlowER control, (2 fresh, 0 persistent)
states stop 100% (56/56) — and there that is *correct*.
It also barely proposes the right first move: **p(chemist's homolysis | B_r)
= 0.005** (median 0.0000) for abstraction. The homolysis head was trained on
Pd–P bonds.

### H2 — Exposure bias: off-bridge wandering with no return pressure (anchor: (N1), (N2), eq. loss 811–815)
*Prediction.* Stuck chains leave `Sector` early and rarely re-enter; the
moves they take are the in-distribution (polar) kind; undo moves are rare
despite being admissible.
*Tests.* Per-position `Stop`-offered flag, last `Sector` visit, inverse-move
rate (`analyze_instrumented.py`).
*Status.* **Confirmed as the mechanism of staying stuck, downstream of H1′.**
Stuck chains have `Stop` offered at 17.7% of positions; **44% never re-enter
`Sector` after position 0**; their moves are **96.3% pair moves** (49.1%
lone→bond, 47.2% bond→lone), 34% touching a hydrogen (polar proton/hydride
chemistry on a radical substrate); immediate undo only 4.9% of moves (1.5%
in stopped chains). In-distribution the same statistics are 0.4% stuck and
0.0% undo. The chain is applying FlowER's polar prior to a molecule whose
one radical it cannot pair up (N3) and cannot recognise as final.

### H3 — Softmax dilution / size (anchor: eq. head 795–797, one pooled `Stop` logit vs `|Allow(x)|` classes; `AddHs` triples `N`)
*Prediction.* `p(Stop)` falls with `|Allow(x)|` and `N`; stuck rate rises with `N`.
*Test.* `p(Stop)` binned by admissible-class count and by `N`; stuck rate by `N`.
*Status.* **Refuted.** `p(Stop|B_r)` *rises* with `N` (0.09 at `N<15` → 0.21
at `N≥50`); stuck rate is flat in `N` (30–42%, no trend); `p(Stop)` vs
`|Allow|` is non-monotone (0.53 at <20 classes, 0.23 at 60–89, 0.33 at 130+).
The stop head's max-pool (code 792–794) does what its comment says.

### H4 — Identity-step prior misapplied (anchor: 780–782, 4437; 18.5% `m = 0`)
*Prediction.* One-radical reactants where "nothing polar is happening" get
`Stop` at `K = 0`.
*Test.* Fraction of chains with 0 moves, by radical count; compare to FlowER.
*Status.* **Minor contributor.** 10.7% of RMechDB chains stop at `B_r`
(15.7% of one-radical chains), never correct there; 19.4% on FlowER, where
it matches the data. Real, but it accounts for a sixth of the one-radical
failures, not the stuck 44.7%.

### H5 — Parity jam: the policy prefers a state it cannot reach (anchor: (N3) + learned `p(Stop)`)
*Prediction.* `p(Stop)` is high at closed-shell states and low at one-radical
states, so a one-radical chain keeps moving; stuck chains end with exactly
one radical.
*Test.* `p(Stop)` by odd-atom count at offered states; final odd count of stuck chains.
*Status.* **Supported.** `p(Stop)`: closed shell **0.93**; one persistent
radical **0.21**; two **0.03**; three persistent **0.00**. Final state of
stuck chains has exactly one odd atom in **2,904 / 2,960**. Note the model
*does* stop at the correct propagation signature when it reaches it — (1
fresh, 0 persistent): `p(Stop) = 0.92`, 350 states — the problem is that it
reaches it in 4% of chains, because getting there requires the route H1′
assigns zero mass.

### H6 — Class imbalance (rare Termination/recombine classes) (from problem01's split)
*Status.* **Superseded.** Termination is the class the model *handles*:
two-radical reactants → recombination product in **1,231 / 1,290 = 95.4%**
of chains (one colligation, then `Stop`), stuck 1.1%. The earlier
"recombine reconstructs 3.3% mid" was the intermediate-state artefact of §0.

### H7 — Checker leniency lets nonsense terminate (anchor: 3536–3555, (N5))
*Prediction.* Some emitted states are valid only because `Tab` is looser than chemistry.
*Test.* Scan stopped finals for `c_i` beyond the algebraic cap (hydrogen `b ≥ 4`, etc.).
*Status.* **Open, low priority.** The 651 triradical emissions are inside
even the algebraic table; validity as defined cannot see them.

### H8 — RMechDB "resonance" steps are FlowER identity steps
*Prediction.* Canonical SMILES of `B_r` and `B_p` coincide; correct answer is `Stop` at `K=0`.
*Status.* **Refuted.** Radical position changes the canonical string; the
chemist's product differs from the reactant; the class behaves like every
other one-radical propagation step (stuck 51.9%, teacher-forced route
probability 0).

### H9 — More radical training data via the `_radical_moves()` fix (`bug_radical_moves.md`)
*Prediction.* Recovering dropped odd-parity training steps improves RMechDB.
*Status.* **Cannot help this failure.** By 2793–2795 the recovered steps are
Pd–P single moves; they teach more of H1′, not less. Pending the census for
confirmation on `train.txt`.

### H10 — Hydrogen bookkeeping (`problem01-validity.md`)
*Status.* **Closed.** With every hydrogen explicit, `n_H ≡ 0`, and Prop. 2
holds 100.0%.

## 3. The metric the paper grades by, on RMechDB

Exact canonical match of the emitted state to the chemist's product
(`analyze_accuracy.py`; a never-stopped chain emits `B_r`, as the decoder does):

| reactant radical centres | chains | = chemist product | recombination of the two radicals | stopped at reactant | 2 fresh radicals, then Stop | stuck → fallback | other |
|---|---|---|---|---|---|---|---|
| 0 (initiation) | 87 | **55.2%** | — | 2.3% | 35.6% | 0.0% | 6.9% |
| 1 (propagation) | 6,570 | **0.6%** | — | 15.7% | 9.9% | 44.7% | 29.1% |
| 2 (termination) | 1,290 | 0.7% | **95.4%** | 0.1% | 1.9% | 1.1% | 0.8% |
| 3 (e.g. R• + O₂) | 495 | 0.2% | — | 0.0% | — | 2.4% | 97.4% |

By class: `abstraction` 0.0% (1,692 reactants), `retroaddition` 0.0%,
`addition` 1.4%, `resonance` 2.4%, `homolyze` 59–75%. Two readings that must
be kept apart:

- For **two-radical reactants** the model's answer is a legitimate
  alternative (radical recombination where the chemist wrote
  disproportionation). Whether RMechDB records the recombination as a
  separate entry is the branch-aware question of App. "What makes the
  comparison fair" (4554–4562) — a test, not a verdict.
- For **one-radical reactants** — 78% of the corpus, and the only case
  where a radical must be *moved* — the model is at 0.6% with the chemist,
  and its three failure modes (fallback to reactant, identity, triradical)
  are all consequences of H1′ + H5 + H2.

This also reconciles the earlier human-plausibility result
(`afm-human-check.md`): there the chemist's route was a *single* homolysis
or colligation, and the model ranked it first in 99.9% of the unique-answer
cases. That is consistent with everything above — one single-electron move
is precisely the sector the model knows.

## 4. What it says about the paper

The guarantees are intact and did their job: every emitted candidate on
new data was a molecule, and the thing that went wrong is visible *because*
the intermediate states are readable. Read literally, the chain says "break
the C–H bond, done" — the FlowER corpus's radical chemistry (2793–2795),
recited on a substrate where it is one move short. The limitation is in the
data, and the paper's own appendix names the sector; what it does not say is
that this sector has depth one, or that a per-atom `Stop` gate cannot
distinguish a finished radical step from a half-finished one (N3, N5).

## 4b. Census of the training split (`corpus_census.py`, 200,000 steps sampled from `train.txt`, RCI job 11645418)

| quantity | value |
|---|---|
| identity steps | 18.0% (paper: 18.5%) |
| steps changing some diagonal by an odd amount | **2.05%** (paper, test: 2.17%) |
| … of which the flipped atoms are exactly {P, Pd} | **84.7%** (3,467 / 4,091) |
| … of which organic element sets (C–O 161, O–O 143, N–O 82, Br–C 68, Br–N 45, C–C 44, C–N 38, C–Cl 21, …) | 15.1% (618) — **0.31% of all steps** |
| steps flipping parity on **four** atoms (two single-electron moves in one step) | **2 / 200,000** (`O O O O`, `P P P Pd`) |
| steps whose reactant carries an odd C/N/O/H/S/halogen atom | 0.30% |
| steps whose product carries one | 0.29% |
| identity steps with an organic radical | 11 |
| odd-diagonal atoms in reactants, by element | P 28,616 · Pd 9,295 · **C 1,183 · O 460** · Na 414 · Cu 203 · K 110 · N 109 · Br 91 |
| atom count per step | median ≈ 70, mode 60–80 (RMechDB: 15–30) |

So the paper's test-split statement ("without exception … Pd–P", 2793–2795)
is slightly too strong for the training split: about one training step in
three hundred is a genuine organic single-electron step, and organic radicals
do appear as reactants and products at the 0.3% level. What is exact is the
*depth*: **99.95% of odd-parity training steps are a single homolysis or
colligation**; a step that breaks one bond homolytically *and* forms another
in the same event occurs twice in 200,000. Every RMechDB propagation step is
of that second kind. H1′ stands as stated, and is now a fact about
`train.txt`, not an inference from the test split. The 618 organic
single-move examples are also why the sampler *can* propose homolysis and
colligation on C/O at all (93% of its moves on RMechDB) while never chaining
them.

## 5. Tests still to run

1. ~~Census on `train.txt`~~ — done, §4b.
2. **Branch-aware scoring** for the two-radical class: does RMechDB contain
   the recombination as an alternative entry for the same reactant?
3. **Where does the sampled homolysis go?** For one-radical reactants the
   model rarely homolyses the chemist's bond (`p = 0.005`); tabulate the
   bond types it does homolyse (element pair, bond order) against the corpus.
4. ~~The only fix is data.~~ **Done — and it is a corpus limitation, not an
   architectural one.** Fine-tuned on 3,485 RMechDB steps (grouped split,
   `experiments/finetune/`), `afm_nano` goes from 0% to 85–90% exact match on
   held-out one-radical `abstraction` steps, stuck chains from 21.6% to
   <1%, and after the chemist's homolysis p(colligation) from 0.000 to
   0.887 while p(Stop) falls from 1.000 to 0.044. A `nano` trained from
   scratch on the same 3,485 steps reaches 82%, so the depth-two radical
   step is learnable by this architecture from a few thousand examples; the
   FlowER pre-training adds 2–4 points and helps most on the rarest class.
   Full table in `afm-human-check.md` § Track 2.

## 6. Files

- `experiments/human_plausibility/instrumented_rollout.py` — per-step log
  (move, atoms, `Stop` offered, `p(Stop)`, admissible classes, odd atoms);
  `results/instrumented_rmechdb.jsonl`, `results/instrumented_flower.jsonl`
  (3,000 FlowER test steps sampled from RCI `test.txt`, `data/flower_test_sample.txt`).
- `analyze_instrumented.py`, `analyze_parity.py`, `analyze_accuracy.py`,
  `teacher_forced_route.py` — the tables above.
- `corpus_census.py` — training-split census (RCI, `outputs/corpus_census_train.json`).
- `fully_explicit_stability.py`, `analyze_mid_gap.py` — the earlier runs
  whose reading §0 corrects.
