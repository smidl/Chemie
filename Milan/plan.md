# AFM / MechReact — work plan

**Status 2026-09-15.** Paper: `Milan/afm.pdf`, "Arrow Flow Matching for Reaction
Mechanisms", anonymous double-blind draft, 51 pp. Code: `git@github.com:mlnpapez/MechReact.git`
(read-only clone inspected; not yet checked out into this tree — see *Repo home*).
Owner: Milan Papež. Our role: strengthen the paper, not take it over.

---

## 1. What we already measured

**The released benchmark contains no extrapolation.** Full scan of
`flower_new_dataset` (the corpus the paper uses), 1.93 M train / 219 k test steps,
RCI job 11604007. Of 179,679 non-identity test steps:

| unseen step type in training | core arrow pattern | 1-hop template |
|---|---|---|
| steps | 136 | 3,440 |
| share of test | **0.076 %** | **1.91 %** |

63 % of test steps have a core type seen ≥10,000 times in training; the top 100
core types cover 83 % of the training corpus; **67 % of all steps are the same
4-change (two-arrow) pattern**; only 10.3 % exceed six simultaneous changes.

Consequence: "AFM extrapolates better" cannot be shown on the released split —
the split never asks. An extrapolation test must be **constructed**.

Artefacts: `Milan/analysis/signature_novelty.py`,
`Milan/analysis/results/novelty_new.json`,
`Milan/analysis/results/test_bins_new.tsv.gz` (per-test-step bin, all 218,997
lines, join key = line index).

**Prior art the draft is missing.** `ArrowFinder` — Miller, Dashuta, Rudisill,
Van Vranken & Baldi, *JACS* 2025, 147(44):41168–41176, `10.1021/jacs.5c16838`.
Takes reactants **and** products, proposes the arrow-pushing mechanism between
them: enumerate via OrbChain → keep those recovering the product → rank with a
learned scorer. 99.55 % ground-truth recovery on PMechDB; **101/1331 (7.6 %)
"functionally equivalent but representationally different"** — an independent
measurement of exactly the order ambiguity of AFM's Limitation (ii). Not cited,
though Kayala & Baldi 2012 is cited three times. Also absent: YARP (b2f2
bond–electron-matrix enumeration + DE-GSM), GSM, AFIR, Chemoton, Pathfinder.
`DeepMech` (Das 2026, `10.1039/d6sc02809h`) *is* cited.

---

## 2. Compute facts (all verified 2026-09-15)

**MechReact already targets RCI.** `scripts/submit_sizes.py` routes to
`amdgpuextralong` / `amdgpu`, sources `/mnt/appl/software/Anaconda3/2024.02-1`,
conda env `basic` — all RCI-native paths.

**The H200 partitions exist on RCI and we can use them.** They are *hidden* from
plain `sinfo` (identical 18-partition listing from login2, login3 and login4);
`sinfo -a` reveals them:

| partition | time limit | nodes |
|---|---|---|
| `h200fast` | 4 h | h01–h03 |
| `h200` | 1 d | h01–h03 |
| `h200long` | 3 d | h01–h03 |
| `h200extralong` | 21 d | h01–h03 |

Each node: 8 × `nvidia_h200_nvl`, 128 cores, 2.32 TB RAM. All `mixed` (in use).
`sbatch --test-only` succeeds on **all four** under `smidlva1` — h200fast,
h200long and h200extralong would start immediately on h03; h200 queues ~16 h.
`scontrol show partition h200extralong` reports "not found" while `sinfo -a`
lists it, so the partitions are hidden rather than group-restricted.

*Catalog gap:* `~/agents/compute/rci.md` (measured 2026-09-01) records only
V100/A100 and does not mention H200 or the `sinfo -a` requirement. Needs a
tier-0 edit.

**No MechReact artefacts on RCI's `resynthesis` allocation.** Searched
`/mnt/data/resynthesis` for `*mechreact*`, `*flower_cons*`, `*papez*` — nothing;
`admissibility/` is our own retro-fallback work. No `papez` account visible.
Milan's `outputs/` (checkpoints, caches) is gitignored and lives on his own
allocation.

**Job shape from his configs.** 1 GPU, 16 CPUs, **133 GB host RAM** — set by the
DataLoader, not the model (he measured 124.9 GB peaks and was OOM-killed at
125 GB). 100 epochs. Featurisation cache is a **7.2 GB blob keyed by split
digest**, so every new split costs one cache rebuild. `flower_cons` (= AFM) is
in `H200_ONLY` because its roll-out holds a beam of running states and their
O(N²) attention at once — the A100's 40 GB is the reason, so `nano` may still
fit and is worth one test.

**`eval.py` writes aggregate metrics JSON only — no per-step predictions.** But
`data.eval_split` is already a config knob, so a filtered test file
(`test_rare.txt`, `test_hard.txt`) evaluates **with zero code change**. Step
accuracy, validity and conservation are valid on a filtered file; pathway
metrics are not (filtering breaks pathways — `build_pathways` drops components
without a unique source), so report step-level only there.

---

## 3. Work items, prioritised

### P0 — no GPU, no dependency on Milan

1. **Citations + related work.** ArrowFinder (must-cite), YARP, Pathfinder/GSM/AFIR
   as a QM-side paragraph. Frame ArrowFinder's 7.6 % as *support* for
   Limitation (ii), not as a weakness. → `/lib add`, then `/lib sota`.
2. **Order-ambiguity count.** How many admissible orders realise one move
   multiset, distribution over the corpus. Turns Limitation (ii) into a number
   and bounds how much P3.1 could recover. Laptop pilot → `cpufast` at scale.
3. **A→C enumerator ("find B").** AFM's combinatorial core is model-free —
   `retrosyntesis/script/decomposition_check.py` already implements the alphabet,
   admissibility table and ordering search. See §3a for how this is defended;
   the target is **not** the covered corpus but the template pipeline's residue.
   *Risk:* a pathway averages 7.4 steps ≈ 16 moves, and `find_admissible_order`
   permutes within connected move components — this may not be tractable.
   Sample a few hundred pathways before promising anything.

### 3a. How the B-finding task is defended

**Do not compete on ArrowFinder's benchmark.** It reaches 99.55 % on PMechDB
with a learned ranker; our enumerator has none. "We also find B, model-free" is a
weaker form of a solved result.

**Read the paper before positioning against it** — pooled as
`miller2025_arrowfinder` (`~/agents/library/`, digest + full text; metadata
verified from raw Crossref). Two things it says change the argument.

**(A) Lead with 68.86 %, not with radicals.** Their own numbers:

| ArrowFinder input | mechanism recovered |
|---|---|
| curated true reactants **and** products | 1331/1337 = **99.55 %** (exact arrow match 1230 = 92.0 %) |
| its own ensemble's predictions, after atom/charge balance filtering | 1968/**2858** = **68.86 %** |

Their explanation, verbatim: *"the predicted products do not always have a simple
or plausible arrow-pushing mechanism available, and in such cases, it is difficult
for ArrowFinder to propose a matching mechanism."* That is the signature of
**generate-then-filter**: the generator can emit a product with no mechanism
behind it, and 31 % of the time it does. A construction that reaches every state
*by applying admissible moves* cannot have that failure mode. This is an
**architectural** difference, not a scope one, and it does not expire.

**(B) The radical argument is true but has a stated expiry.** From their
Conclusion: *"we are actively expanding coverage to build a master data set that
integrates polar, radical, pericyclic, and combinatorial reactions, with plans to
release future models trained on these broader data sets."* They also cite their
own NeurIPS 2023 radical work. Do not build the case on a gap the competitor has
announced they are closing — keep it as a secondary, dated point.

Also note (B') — **our polar measurement is not a discovery.** PMechDB is polar
*by construction*, so "0 % of polar steps need single-electron moves" restates
the premise their formalism was chosen under. It is a clean quantification of
scope, nothing more. Do not present it as something they missed.

Two structural deltas that survive:

- **The set is guaranteed, not filtered.** ArrowFinder enumerates then *keeps
  those that recover the product*; YARP filters by DFT. Here conservation is an
  algebraic identity and validity a table lookup — exact before anything is
  checked. This is what (A) measures.
- **Exhaustiveness is unconditional.** ArrowFinder is exhaustive only *between
  its predicted source and sink atoms* — a learned restriction. When that
  prediction is wrong the true mechanism is not in the set. Ours has no such gate.

**The regime nobody occupies.** FlowER's Methods: **1,100,105** USPTO-Full
reactions fed to the template pipeline (1,200 templates, 252 classes, 185
mechanisms). Overall reactions in the corpus we hold: **289,024** — so the
pipeline decomposed **26.3 %**, leaving ~810,000 reactions with no mechanism and
no published breakdown of why. That residue is the target: prior methods are
structurally absent from it (FlowER's templates already failed there by
construction), and it is the only **non-circular** test on this data — on the
covered 26 % the ground-truth B *is* template output.

**Triage — RUN 2026-09-15, job 11605039. The fail condition fired.**

USPTO-Full (Lowe grants, `10.6084/m9.figshare.5104873.v1`, now at
`/mnt/data/resynthesis/data/2-raw/uspto-lowe/`), 1,808,937 reactions:

| | count | share |
|---|---|---|
| RDKit-parseable | 1,808,290 | 99.96 % |
| atom-mapped | 1,808,290 | 99.96 % |
| heavy-atom balanced, reactants alone | 61,951 | 3.42 % |
| …and proton-balanced | 43,645 | 2.41 % |
| **runnable as recorded** (mapped + balanced either reading) | **62,319** | **3.45 %** |

Full result: `Milan/analysis/results/uspto_balance.json`; script
`Milan/analysis/uspto_balance.py`.

**The corpus covers 289,024 overall reactions — 4.6× the entire
balanced-as-recorded population of USPTO-Full.** That is proof the template
pipeline *manufactures* balance rather than selecting for it. Two consequences:

1. There is no large "balanced but untemplated" pool. It is at most 62,319, and
   since an already-balanced reaction is strictly easier for the template
   pipeline, most of those are probably inside the covered 26 %, not the residue.
   (Confirming that needs corpus pathways reduced to overall reactions —
   root→terminal with spectator cancellation, per `retro-generation`'s
   `show_pathway.py` — not yet done.)
2. Working the residue requires a balancer in front (SynRBL; venv at
   `/mnt/data/resynthesis/admissibility/.venv-synrbl`) plus a mapper. The
   contribution then reads as a pipeline assembled from other people's tools,
   which is a much weaker claim than a method.

**Re-scope: move the B-finding claim to PMechDB / RMechDB.** Curated from
literature mechanisms rather than template-imputed, so a recovery number there is
non-circular — and **RMechDB is radical**, exactly where OrbChain/ArrowFinder
(polar-only) structurally cannot follow, which is delta #1 above. This is the
honest home for the claim; the USPTO residue is not.

**Both are already on disk — no gated download needed for the scope claim.**
The FlowER corpus carries them as augmentation buckets, labelled in place of the
numeric sequence index: `PM`/`PC` (polar, curated/combinatorial) and `RS`/`RC`
(radical). Radical totals **5,088** against RMechDB's published ~5,300, and `PM`
totals **12,616** against PMechDB's 12,799 curated SMIRKS — so both databases are
effectively present, balanced and atom-mapped. What the conversion drops is the
**curly-arrow annotation**, so arrow-*recovery* still needs the registered
download (name/email/institution + CC-BY-NC-ND); scope and ambiguity do not.
Extracted to `/mnt/data/resynthesis/FlowER/novelty/buckets/{split}_{bucket}.txt`.

### 3b. Measured 2026-09-15 — the structural gap, quantified (job 11605190)

`Milan/analysis/mech_buckets.py` builds the Dugundji–Ugi matrix for both sides of
every bucket step (B_ii = V − q − rowsum; every H is its own mapped atom, so no
implicit term) and reads the parity of the diagonal change. Per the paper, the
two single-electron moves (`HOMOLYSIS`, `COLLIGATION`) "are needed whenever a
step changes a diagonal entry by an odd amount, which pair moves cannot do" — so
parity is a direct test of whether a step needs the fish-hook half of the
alphabet, the half OrbChain does not have.

| bucket | steps | parsed | e⁻ conserved | **needs single-electron moves** | mean moves |
|---|---|---|---|---|---|
| PM polar, curated | 12,616 | 12,545 | 100 % | **0 / 12,545 = 0.00 %** | 2.66 |
| PC polar, combinatorial | 16,399 | 15,110 | 100 % | **0 / 15,110 = 0.00 %** | 1.54 |
| RS radical | 3,569 | 3,569 | 100 % | **3,566 = 99.92 %** | 1.57 |
| RC radical | 1,519 | 1,518 | 100 % | **1,504 = 99.08 %** | 2.11 |

The separation is exact, not approximate: **zero of 27,655 polar steps** need a
single-electron move; **5,070 of 5,087 radical steps** do. Electron conservation
holds at 100 % on every bucket, which independently validates both the corpus's
own claim and our matrix construction. Results:
`Milan/analysis/results/buckets_all.json`.

**The claim this supports, as it would read:** *a pair-move-only formalism is
exactly sufficient for polar chemistry (0 of 27,655 steps need more) and exactly
insufficient for radical chemistry (99.7 % of 5,087 steps need more). The four-move
alphabet is the smallest one covering both.* The paper already asserts this
qualitatively in §5; what is new is the number and the positioning against
ArrowFinder, which the draft does not cite.

### 3c. Stage 2 — RUN 2026-09-15, job 11605500. The alphabet is near-deterministic.

`Milan/analysis/decompose_steps.py` — model-free throughout, no trained network.
Splits the bond-order delta into unit slots, enumerates the three alphabet moves
per slot, keeps assignments whose per-atom diagonal contributions match exactly,
then searches for an ordering admissible at every prefix (permuting only within
connected components of the move graph). The per-element capacity table is
*measured* from the corpus endpoints in a first pass rather than assumed — it
recovers H→2, C/N/O/halogen→8, and hypervalent S→12, P→10 on its own.

All 5,088 radical steps (`RS`+`RC`, train and test):

| | count | share |
|---|---|---|
| **decomposed** (valid move multiset with an admissible order) | **5,052** | **99.29 %** |
| no move assignment matches the electron budget | 15 | 0.29 % |
| ordering not searched (component > 7 moves) | 15 | 0.29 % |
| not searched (> 10 units) | 5 | 0.10 % |

So the true decomposition rate is between 99.29 % and 99.69 %; only 15 steps are
*proven* infeasible. And the ambiguity is the striking part:

| valid move assignments per decomposed step | 1 | 3 | 7 | 9 | 17 |
|---|---|---|---|---|---|
| steps | **4,992 (98.8 %)** | 49 (1.0 %) | 9 (0.2 %) | 1 | 1 |

**98.8 % of radical steps admit exactly one *minimal* mechanism under the
alphabet.** Mean 1.03. Results: `Milan/analysis/results/decompose_radical.json`.

⚠ **"Minimal" is load-bearing** (found while validating against curated arrows,
§3d). The search builds its slots from the bond-order delta, so it only ever finds
decompositions in which no bond is touched twice. Decompositions containing a
cancelling pair — a move and its inverse on the same bond, which the alphabet
permits and chemists sometimes need — are invisible to it. So 98.8 % is uniqueness
*among minimal decompositions*; true ambiguity is higher by an unmeasured amount.
Quote it with that qualifier or not at all.

**What this does and does not license.**

- It *is* a uniqueness claim: where ArrowFinder enumerates candidates and needs a
  learned Siamese ranker to choose among them, here there is usually nothing to
  choose between. No ranker required.
- It is **not** a correctness claim. FlowER's conversion dropped RMechDB's
  curly-arrow annotations, so we cannot check that the unique decomposition found
  is the curated one. That check needs the registered RMechDB download
  (name/email/institution, CC-BY-NC-ND) and is the obvious next step.
- The matched comparison is against ArrowFinder's **99.55 %** row (curated
  endpoints both sides), not the 68.86 % row. On that row: recovery comparable
  (99.29 vs 99.55), ambiguity far lower (1.2 % multi-assignment vs their 7.6 %
  representationally-different) — but those two quantities are not the same
  measurement, and saying so is part of the claim. **Testing the 68.86 % row needs
  a generative model's outputs, i.e. Milan's checkpoints.** That is the experiment
  to run the moment P1's blocker clears.

Polar buckets (`PM`/`PC`, 29,015 steps) queued as job 11605397; `cpufast` was
saturated at submission.

**Loose end:** 1,354 polar steps (1,289 of them `PC`) fail to parse — likely
unkekulisable aromatics or elements outside the valence table. 4.7 % of the polar
set; worth identifying before quoting polar numbers in a paper.

**Byproduct worth keeping.** The `.rsmi` carries a **Year** column, 1976–2016. A
**time split** is the most defensible OOD axis in this field and is better than
the constructed complexity split of P2 — *if* corpus reactions can be matched
back to patent years. That match is the same root→terminal reduction as (1), so
one piece of work unlocks both. Promote to P1 if it turns out cheap.

**The claim, as it would read:** *expert templates decompose 26.3 % of
USPTO-Full; the arrow alphabet, with no templates, no rule engine and no trained
network, decomposes X % of the balanced remainder into mechanisms that conserve
electrons, atoms and protons exactly and pass valence at every intermediate, with
a median of N admissible candidates per transformation.* A large N is not a
failure — it reframes the network's job as **ranking inside a guaranteed-valid
set** rather than generating and hoping.

**What sinks it:** the residue is mostly unbalanced; or X is small; or — the
sharpest objection, and the one to expect from a chemist reviewer —
**valence-admissible is not chemically plausible**. The table gates valence and
octets; there is no energetics in it at all. The only answer is barriers on a
sample, which is the DFT-NEB line already built in
`/mnt/data/resynthesis/retrosyntesis_afm_run` (spec04 converged at 92.4 kcal/mol
while spec05–08 returned `IMPLAUSIBLE_BARRIER` in the same job on the same
stack). Make that connection explicit rather than leaving it implicit.

### P1 — GPU, eval only, needs Milan's checkpoints

4. **Novelty- and complexity-stratified accuracy.** Build `test_rare.txt`
   (1-hop template count < 10: 9,992 steps, binomial SE 0.36 pp) and
   `test_hard.txt` (>6 changes: 18,579 steps) from `test_bins_new.tsv.gz`, then
   `eval.py data.eval_split=...` per model. Four models — `flower_cons`,
   `flower_discrete`, `flower`, `mecht5` — × 2 filtered splits = 8 jobs.
   The three flow models share one body and one width ladder, so the elementary
   event is the only variable between them; that comparison is the result.
   Core granularity gives only 715 steps (SE 1.34 pp) — too weak, use 1-hop.

### P2 — GPU, retraining, small

5. **Complexity-split retrain.** Train on ≤4 changes (78 % of corpus), test on
   >6 (18,579 steps). The only genuinely constructed OOD test, and it probes the
   claim directly: a multi-arrow concerted step is where an entrywise product
   measure is worst placed *and* where AFM's order ambiguity bites hardest —
   genuinely two-sided, it can go against him. Three flow models at `nano` only;
   that is where the paper's claim lives. Budget one cache rebuild.

### P3 — new science

6. **Exact product likelihood** by summing over admissible orders of one move
   multiset, replacing the lower bound (17). The paper's own open direction and
   the plausible fix for the single metric AFM loses (path@1 0.9303 vs 0.9500 for
   Discrete FlowER). Algorithmic work + one retrain to verify.
7. **Capacity-table coverage audit.** T is enumerated against *this* test split's
   observed valences (Appendix E.3). On out-of-corpus chemistry the mask can
   forbid the correct stop state — validity would still report 1.0000 while
   accuracy on those steps goes to zero. This is the guarantee's one empirical
   assumption; better we find the hole than a reviewer. CPU only.

### P4 — stretch, high leverage for ICLR

8. **One non-chemistry demonstration.** The conclusion already claims generality
   ("wherever a hard constraint is a linear functional of a discrete state").
   A reviewer will ask for exactly one toy instance and it costs almost nothing.
   If the target is ICLR rather than a chemistry venue, this outranks P3.
9. Alphabet extension to three-centre / single-electron events (Limitation iv);
   non-local aromatic validity mask. Both large; the J.3 residue is 32 in 400,000,
   so the aromatic case is not urgent. Out of scope for a rebuttal.

---

## 4. Compute allocation

| where | what | shape |
|---|---|---|
| **laptop** | corpus analysis (done), split-file construction, enumerator pilot, order-ambiguity sample, all figures/tables, citation verification | minutes |
| **RCI `cpufast`** | same combinatorics at full-corpus scale — P0.2, P0.3, P3.7 | 32 cores, ≤4 h; the novelty scan took 7 min |
| **RCI `amdgpu`** | P1 eval passes from existing checkpoints | 1 GPU, 16 CPU, 133 GB RAM, 1–3 h/job |
| **RCI `h200long`** | P2 retrains of `flower_cons`; `flower`/`flower_discrete` `nano` can go to `amdgpuextralong` (less contended) | 3 d cap is ample at `nano` |
| **RCI `h200fast`** | smoke tests and cache builds — starts immediately, 4 h cap | |

Rule of thumb: the laptop does everything that is not a GPU forward pass. Nothing
here needs a queue longer than 3 days at `nano` size.

---

## 5. The one blocker

Checkpoints. `outputs/` is gitignored, nothing of Milan's is on the `resynthesis`
allocation, and `eval.py` never wrote per-step predictions. P1 cannot start until
we have either his checkpoint paths with group read, or his per-step predictions
if he kept any. Everything in P0 proceeds regardless.

### Ask for Milan (three items, not a discussion)

1. **Path + group read** on the trained checkpoints — the five `flower_cons`,
   `flower_discrete` and `flower` sizes, at minimum `nano` — and on his
   `data/flower_new_dataset` featurisation cache if it is shareable (saves a
   7.2 GB rebuild).
2. **ArrowFinder** (Miller et al., *JACS* 2025, `10.1021/jacs.5c16838`) — same
   problem, same year, same group as Kayala & Baldi which he already cites. Not
   a criticism: its 7.6 % representational-degeneracy number is independent
   support for his Limitation (ii).
3. **Did he keep per-step predictions anywhere?** `eval.py` persists only
   aggregates. If not, we regenerate from checkpoints on our own allocation — a
   few A100-hours, none of his time.

---

## 6. Repo home — needs a decision

The MechReact clone currently lives only in a session scratchpad. Proposed:
`Milan/MechReact/` as a plain sibling checkout, gitignored here (not a submodule —
it is Milan's repo, we are readers). That is a change to this node's shape, so it
is not done yet.

---

### 3d. Validated against curated arrows — RMechDB, 2026-09-15

The registered RMechDB download arrived by email and keeps what FlowER's
conversion drops: the chemist's curly arrows. So the §3c uniqueness result can be
turned into a *correctness* question — is the alphabet's mechanism the chemist's
mechanism? Data at `datasets/rmechdb_data/` (gitignored; **CC-BY-NC-ND**, cite
RMechDB directly). Script `Milan/analysis/rmechdb_arrows.py`, run locally —
5,426 steps is laptop work and it keeps licensed data off the cluster.

Arrow grammar, read off the data rather than assumed: arrows split on `;`, each
`SOURCE SEP SINK`, a bare map number is a lone-electron slot and a comma pair is
a bond, `-` moves one electron and `=` moves two. The alphabet expands into it
exactly — `LONE_TO_BOND(i→j)` = `i=i,j`, `BOND_TO_LONE(i,j→j)` = `i,j=j`,
`HOMOLYSIS(i,j)` = `i,j-i ; i,j-j`, `COLLIGATION(i,j)` = `i-i,j ; j-i,j` — so
recovered moves and curated arrows are directly comparable. RMechDB maps only the
*reacting* atoms, so the matrix is built over those with the unmapped environment
folded into a per-atom context degree (the reduction afm.pdf itself uses),
checked per row to be a spectator rather than assumed.

| | count | share |
|---|---|---|
| **decomposed** | 5,246 | **96.68 %** |
| **no decomposition found** | **1** | 0.02 % |
| excluded — no bond-order change | 121 | 2.2 % |
| excluded — unmapped context not a spectator | 56 | 1.0 % |
| exact arrow match | 2,058 | 39.2 % of decomposed |
| equivalent, drawn differently | 3,188 | 60.8 % |
| curated uses a bond→bond fish-hook | 2,276 | 42.4 % |

Results: `Milan/analysis/results/rmechdb_arrows.json`.

#### Solid — quote these

**96.68 % decomposed, exactly one outright failure**, on curated literature
radical chemistry with only-reacting-atoms mapping. The search's incompleteness
(below) can only *raise* this, so it is a floor in the safe direction.

**The alphabet emits fish-hooks only in pairs.** `HOMOLYSIS` and `COLLIGATION`
each contribute exactly two, so a decomposition's fish-hook count is always even.
RMechDB's curated steps are **odd-numbered 3,182 times against even 2,244** —
**58.7 % of real radical mechanisms have an arrow count the alphabet structurally
cannot produce.** Together with the 42.4 % that route an electron directly from
one bond into another, this is **Limitation (iv) quantified**: "genuinely
three-centre elementary events would need the alphabet extended". It is not
marginal, and it is a property of the alphabet, not of our search.

Worked example of the gap, from the data: `[O-:1][N+:2]=O >> [O:1][N:2]=O`,
curated arrow `1-2` — one electron hops between lone-pair sets, **no bond order
changes at all**. The alphabet needs two moves for it (`LONE_TO_BOND(1→2)` at
(−2,0,+1) plus `HOMOLYSIS(1,2)` at (+1,+1,−1), summing to (−1,+1,0)), where the
chemist draws one arrow.

#### A floor, not a measurement — do not quote as a result

**39.2 % exact arrow match.** Our enumeration builds slots from the bond-order
delta, so it finds only decompositions in which no bond is touched twice. Any
curated drawing requiring a cancelling pair is unreachable, and the 121
"no bond-order change" rows are excluded for the same reason though the alphabet
can in fact express them (see the worked example above). So an unknown part of
the 60.8 % disagreement is our search's fault, not the alphabet's.

**Decision, 2026-09-15: not fixing this.** Allowing cancellation means searching
over non-minimal decompositions — a materially larger search, not a patch — and
the limitation stays in the paper regardless. Validate what we can; state the
rest as a floor.

#### The claim this licenses

*On curated radical chemistry the four-move alphabet finds a
conservation-exact, valence-valid mechanism for 96.7 % of steps (one outright
failure in 5,426), but reproduces the chemist's own drawing in a minority of
cases: 58.7 % of curated mechanisms have an odd fish-hook count that an
even-only alphabet cannot emit, and 42.4 % route an electron directly bond-to-bond,
a three-centre event outside the four-move set.*

So the honest framing is a **canonical re-drawing, robust and complete, not a
reproduction of chemists' notation** — and the paper's Limitation (iv) now has a
number attached instead of a hedge. That is a stronger position than claiming
agreement we cannot demonstrate, and it is safe against a reviewer who runs the
same check.

---

### 3e. PMechDB polar validation, 2026-09-15 — coverage confirmed, arrow-match abandoned

Ran the §3d comparison on PMechDB's 12,799 manually curated **polar** steps
(`datasets/pmechdb_data/`). The two databases are exact complements: RMechDB is
12,241 fish-hooks and one pair arrow, PMechDB is 26,070 pair arrows and zero
fish-hooks.

| | polar (PMechDB) | radical (RMechDB) |
|---|---|---|
| rows | 12,799 | 5,426 |
| excluded (context not spectator / unparsed / no bond change) | 375 | 179 |
| attempted | 12,424 | 5,247 |
| **decomposed** | **12,377 = 99.62 %** | **5,246 = 99.98 %** |
| failures | 47 | 1 |
| curated uses bond→bond (three-centre) | 30.0 % | 42.4 % |
| exact arrow match | 15.4 % | 39.2 % |

**The headline, and it is the strongest result we have:** across **17,671**
curated elementary steps from both mechanistic regimes, the four-move alphabet
finds a conservation-exact, valence-valid mechanism for **17,623 — 99.73 %,
48 failures total.** Model-free, no network, no learned source/sink prediction.
That is the direct counterpart to ArrowFinder's architecture: the same condition
they report **99.55 %** on (curated endpoints both sides), reached without a
ranker, and the property their **68.86 %** row shows generate-then-filter lacks.

**Arrow-exact-match is abandoned as unmeasurable.** A prediction made before the
run — that polar would match better than radical, since one pair arrow should be
one move — was **wrong**: 15.4 % against 39.2 %. The reason is that PMechDB's
notation is *orbital*-based, not bond-electron-matrix based. Its second column
types every arrow (`sigma_empty`, `lone_sigma*`, …), and the bare atom→atom form
— **9,274 of 26,070 arrows** — is ambiguous between "pair lands on j's lone set"
and "pair forms the bond to j" without that taxonomy. One notation quirk was
fixable and was fixed (a trailing comma, `10=20,`, marks the bond being formed;
1,156 rows, previously rejected outright). The rest needs OrbChain's orbital
semantics implemented, which is real work, not a parse fix.

Per the 2026-09-15 decision — keep the limitation, validate only what we can —
**neither exact-match figure goes in the paper.** Radical 39.2 % is a floor from
our minimal-decomposition search; polar 15.4 % is an artefact of notation
mismatch. They are recorded here so nobody re-derives them and believes them.

**What survives as structural, independent of sink conventions:**

- **Coverage 99.73 %** over both regimes (above).
- **Three-centre bond→bond transfers: 30.0 % polar, 42.4 % radical.** The `i,j=k,l`
  form is unambiguous, so this stands. The alphabet needs two moves for each.
- **Fish-hooks come only in pairs** (§3d): 58.7 % of curated radical steps carry
  an odd arrow count the alphabet cannot emit. Depends only on counting arrows,
  not on interpreting sinks.

Results: `Milan/analysis/results/pmechdb_arrows_curated.json`,
`Milan/analysis/results/rmechdb_arrows.json`.

---

### 3f. Negative control, 2026-09-15 — is "admits a decomposition" discriminating?

The 99.73 % coverage of §3e is evidence for the architectural claim only if the
alphabet **rejects** wrong products. Tested directly.

**Distractors.** Group steps by the (map number → element) signature of the
reactant; within a group, pair step *i*'s reactant with step *j*'s product. Each
such pair is balanced by construction, chemically valid (the product is an
unmodified curated molecule) and almost always wrong — the shape of the
balance-filtered wrong predictions ArrowFinder reports 68.86 % on. Identical
products dropped; over-budget pairs reported apart from rejections.
Script `Milan/analysis/distractor_control.py`.

| | polar (PMechDB) | radical (RMechDB) |
|---|---|---|
| true pairs decomposed | 99.62 % | 99.98 % |
| distractor pairs judged | 34,462 | 11,297 |
| **distractors decomposed** | **55.2 %** | **89.4 %** |
| distractors rejected | 15,440 | 1,198 |
| **discrimination gap** | **44.4 pp** | **10.6 pp** |

**The asymmetry is the finding.** In polar chemistry the alphabet rejects 45 % of
wrong-but-balanced products — genuinely discriminating. In radical chemistry it
rejects 11 %. Chemically that reads correctly: the single-electron moves are
permissive (a lone electron can go almost anywhere), while pair moves need a lone
pair to donate and an octet with room, so far fewer wrong rearrangements survive.

**Three consequences, in order of how much they change what we say.**

1. **"Every emitted product has a mechanism" is a representability guarantee, not
   a plausibility filter.** Do not sell it as the latter. Overall the alphabet
   accepts 29,121 of 45,759 wrong pairs — 63.6 %.

2. **It reinterprets ArrowFinder's 68.86 %, against their own stated
   explanation.** They write that *"the predicted products do not always have a
   simple or plausible arrow-pushing mechanism available"*. On polar chemistry —
   their domain — a mechanism exists for **55.2 % of arbitrary wrong balanced
   products**. So mechanisms are available for the majority even of wrong
   products, and their 31 % failure rate is better read as **OrbChain's narrowness
   plus the learned source/sink bound** than as mechanism non-existence. Caveat
   before using this: their 2,858 were model predictions, ours are swapped
   curated products — different distributions, so this is a caution against their
   interpretation, not a refutation of their number.

3. **For AFM as a generative parameterisation, high acceptance is the point.**
   The model reaches essentially the whole space of balanced rearrangements while
   never leaving validity and conservation. **The guarantee costs no
   expressiveness** — that is the defensible claim, and it is the one the paper's
   own "the bias replaces capacity" result already supports. It is a better
   framing than a discrimination claim the data does not support.

Results: `Milan/analysis/results/distractor_{pmechdb,rmechdb}.json`.

---

### 3g. Bounded cancellation, 2026-09-16 — the uniqueness claim does not survive

`Milan/analysis/cancel_search.py`. The minimal-decomposition search of §3c builds
its slots from the bond-order delta, so it never considers a decomposition in
which a bond is touched twice. This allows **at most one cancelling pair** — a
move and its inverse on the same bond — and asks what that changes. Bounded, not
the open-ended rewrite the 2026-09-15 decision declined.

**L1 — the excluded rows are expressible after all.** Of the 121 RMechDB steps
with **no bond-order change** (resonance and lone-electron shifts, e.g.
`[O-:1][N+:2]=O >> [O:1][N:2]=O`, curated arrow `1-2`), **116 of 121 are
expressible with exactly one cancelling pair**; 5 skipped as too large, **0 not
expressible**. The hand-worked case generalises completely. They were excluded by
our search, not by the alphabet — so §3d's coverage figures are floors, as
labelled.

**L2 / L3 — uniqueness was an artefact of the restriction.**

| | radical (250 sampled) | polar (250 sampled) |
|---|---|---|
| mean valid decompositions, minimal only | 1.00 | 1.00 |
| **mean with one cancelling pair allowed** | **13.55** | **19.94** |

**Retract the uniqueness claim.** "98.8 % of steps admit exactly one mechanism"
(§3c) holds only under a restriction the alphabet itself does not impose. Allow a
single cancelling pair and the same steps admit **13–20** valid decompositions on
average. Nothing in AFM restricts its roll-out to minimal mechanisms — the chain
may take any admissible move sequence up to its budget — so the model's
hypothesis space contains all of these.

**What it means for the paper, and it is useful rather than damaging.**
Limitation (ii) currently says a product can be reached by several admissible
*orders of the same moves*, making the trajectory score a lower bound on
log p(B̂|Br). This measurement says the bound is **looser than that**: the product
is also reachable by many *different move multisets*, not merely different orders
of one. The paper's own open direction — "summing the trajectory likelihood over
the admissible orders of one multiset would give the exact product likelihood" —
would therefore still not be exact. That is worth saying in the paper, and it is
a sharper statement of a limitation Milan already owns.

A chemist would call most of these detours spurious: a cancelling pair creates and
destroys a bond inside the mechanism. So the *minimal* decomposition is plausibly
the chemically meaningful one, and "unique among minimal decompositions" remains
true and quotable **with that qualifier attached every time**. What is dead is the
unqualified claim.

Results: `Milan/analysis/results/L{1,2,3}_cancel_*.json`.

### 3h. FlowER's conversion is lossier than the originals

The queued polar-bucket job (11605397) landed. Decomposition rate on FlowER's
*converted* copies against the originals measured in §3d–3e:

| bucket | FlowER copy | original |
|---|---|---|
| PM polar curated | 97.31 % (train) / 97.62 % (test) | 99.62 % |
| PC polar combinatorial | 91.12 % / 92.01 % | — |
| RS / RC radical | 98.99–99.71 % | 99.98 % |

`Milan/analysis/results/decompose_flower_buckets.json`. The polar gap is the
notable one: ~2–8 points of chemistry decomposes in PMechDB's own release but not
in FlowER's conversion of it. Worth attributing before relying on either — it is
either the conversion or our parse of the converted form, and we have not
separated those.

---

## Running as of 2026-09-16 (inspect when complete)

RCI, all `cpu` partition, queued behind a busy cluster:

| job | what | output |
|---|---|---|
| 11605983 | decompose + move census, 200k sample of corpus **train** — independently checks Milan's own "0.05 % admit no order" filter claim | `e1_corpus_train.json` |
| 11605984 | same on 200k of corpus **test** | `e2_corpus_test.json` |
| 11605985 | distractor control on PMechDB **combinatorial** test (9,587) — does the 55.2 % polar acceptance hold on machine-generated steps? | `e3_distractor_combinatorial.json` |
| 11605986 | **capacity-table cross-check**: table built on 400k corpus train steps, tested against corpus test and PMechDB curated — the guarantee's one empirical assumption | `e4_capacity.json` |
| 11605989 | distractor control on the **corpus** itself; steps of one pathway share an atom set, so distractors are that reaction's own wrong intermediates | `e5_distractor_corpus.json` |

All under `/mnt/data/resynthesis/FlowER/novelty/`.
