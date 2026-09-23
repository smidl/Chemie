---
coord:
  enrolled: true
  role: orchestrator
  owners: [vsmidl]
  modules: [adr, synthesis, messages]
  boundaries:
    - path: ./proposal
      remote: https://git.overleaf.com/69d8ec44bf191779c9ce381a
      kind: paper
      flow: both
      link: repo
    - path: ./briefing
      remote: git@github.com:aicenter/retrosyntesis-knowledgebase.git
      kind: report
      flow: out
      link: submodule
  external:
    - path: ./retro-generation
      remote: git@github.com:aicenter/retro-generation.git
      kind: student
    - path: ./Ayman/retro-activelearning
      remote: git@github.com:aicenter/retro-activelearning.git
      kind: student
    - path: ./retro-physics-validation
      remote: git@github.com:CVUT-students/retro-physics-validation.git
      kind: student
---

# Chemie — chemistry research (coord orchestrator, pilot)

Top orchestrator for the lab's chemistry research. **Pilot, flat** — the Synthesis
orchestrator layer was dissolved on 2026-06-15 (coord flatten). Protocol:
`~/agents/protocol.md`. This file is canonical; `CLAUDE.md` is a thin delta.

## Enrolled children (peer leaves)
- `retro-pfn/` — reaction-feasibility & energetics modeling toward ξ_f (the
  retrosynthesis-feasibility project). **Submodule** (`aicenter/retro-pfn`).
- `MolGPT/` — general-purpose **molecule**-generation model (GPT→PFN). The reaction-generation
  line was split out to `retro-generation/` on 2026-07-24; the two tracks run in parallel.
  Scope after the split is the **molecule** track only — it is no longer the program's reaction
  proposer (that role, ADR-0003 "T3", now sits with `retro-generation`). Declares its own
  external `MolPFN` + `result_coordination` and boundary `phd-proposal`.
- `retrosyntesis/` — the program's **integration** node: the CLOVER pipeline
  (Knowledge → Planning → Validation), planner harnesses, K-P-V benchmark.
  **Reassigned from student-external to owner-operated on 2026-09-01** after
  moczyjor and mollerob left; owners now `[vsmidl]`. Plain sibling checkout
  (gitignored here), remote `aicenter/retrosyntesis` — *not* a submodule like
  `retro-pfn`/`retro-planning`; see the open decision at the end of this file.
  The supervisor hands-off/inbox-only rule no longer applies to it.
- `retro-planning/` — **learned search heuristics** for retrosynthesis planning
  (the search-`h` side). Seeded 2026-06-18 from the status finding that the
  190-hard budget wall is search guidance, not feasibility (SAScore `h` vs a
  learned rank-trained `h`). Sibling to retro-pfn: it owns `h` (which node to
  expand); retro-pfn owns ξ_f (edge costs). They compose on the same syntheseus
  harness. **Submodule** (`aicenter/retro-planning`).
  **Two-track split (2026-07-05, ratified here 2026-07-28):** the domain-agnostic
  *method* half (rank vs regress vs path-consistency, epistemic-`h` + UCB, AND-OR rank
  theory, g/h-calibration + λ) moved to a **root-level peer tree `~/AIC/Planning`**, which
  also holds the paper. This leaf keeps the **chemistry instantiation** (190-hard,
  SeeA\*/KeeA\*/MEEA\* harnesses, RCI compute). Methods flow down, phenomenology flows up.
  See "Peer trees" below — `~/AIC/Planning` is *not* a child of Chemie and must not be
  managed as one.

## External & boundary (declared here — Chemie is the single inventory owner)
- `retro-generation/` — **external** student **reaction-generation** repo (owner rektomar,
  `aicenter/retro-generation`); handoff of the generative-reaction line from MolGPT (2026-07-24).
  Inventory + coordination (inbox/outbox) only.
- `Ayman/retro-activelearning/` — **external** student repo (owner Ayman,
  `aicenter/retro-activelearning`; enrolled 2026-09-21). **Active learning where the error is
  reducible**: the escalation policy over the oracle ladder — which reactions get moved to a more
  expensive rung, and to which. Reframes the thesis away from injected (irreducible) label noise
  toward measured (reducible) model error; rationale and evidence in `Ayman/WORKING-reducible-noise.md`.
  Inventory + coordination only. **Owner handle is a placeholder** pending his account name.
- `retro-physics-validation/` — **external** student **physics-based validation-tool evaluation**
  repo (owner jinrehacek, `CVUT-students/retro-physics-validation`; 2026-07-24). First task = blind
  tool-suitability study on anonymized candidate routes. Inventory + coordination only.
- `proposal/` — **boundary**, Overleaf paper (`flow: both`).
- `briefing/` — **boundary**, the colleague knowledge base
  (`aicenter/retrosyntesis-knowledgebase`, `flow: out`, submodule): the outward
  "what we know / what we tried" digest for expert colleagues.

(MolGPT declares its own external `MolPFN` + `result_coordination` + boundary `phd-proposal`
in its marker; they roll up under this tree.)

## Peer trees (outside Chemie — coordinate, never manage)
- `~/AIC/Planning` — the abstract search/heuristic-learning method node spun out of
  `retro-planning` on 2026-07-05. Root-level **peer**, not a child: Chemie has no authority
  over it and does not pull its outbox as a child. Cross-tree traffic goes through the
  `~/agents` message board. Chemie's interest is one-directional and specific: the *method*
  results it produces are inputs to `retro-planning`'s chemistry instantiation, and the
  190-hard phenomenology flows back up to it. **Already in the tier-0 registry** (added by the
  2026-07-05 `/coord index` rebuild) — `retro-planning`'s outbox claim that it "is not yet in
  the coord registry" is stale.

## Not enrolled — transparent by design (inventory, so a sweep doesn't read them as orphans)
- `Draslovka/` — **active** industrial-partner demo-prep track (HCN/cyanide specialty chemicals;
  `BACKGROUND.md`, `STATUS.md`, `experiments/`). Deliberately unenrolled: `/coord init` when
  Draslovka commits. Its findings are program-relevant (route-validation-as-metric-artifact,
  granularity) and are folded into `coordination/synthesis.md`, not left only in the folder.
- `RetroDemo/` — Manim demo-animation stack (mock data, presentation asset).
- `datasets/`, `datasets.tar.gz` — local data; `_lib-inbox/` — `/lib` staging.

## Personnel & succession (updated 2026-09-01) — read before planning any student work
Two of the four students have **left**; two **stay**.

| who | node | role | horizon |
|---|---|---|---|
| Joris Moczygeba (`moczyjor`) | *(was `retrosyntesis`)* | **integration** — K-P-V benchmark, planner harnesses, learned validators | **left** |
| Robin Molle (`mollerob`) | *(was `retrosyntesis`)* | **numerics** — DFT-NEB, Skala, the oracle ladder | **left** |
| Jindřich Řeháček (`jinrehacek`) | `retro-physics-validation` | **training now**, then **inherits numerics from Robin** | stays |
| Martin Rektoris (`rektomar`) | `retro-generation` | generative reaction modelling | stays |

- **`retrosyntesis` is now owner-operated** (`owners: [vsmidl]`, reassigned 2026-09-01). The
  succession intent above is complete: it *is* the shared place, and it is edited directly rather
  than through an inbox. It remains an **integration** project: when numerics is settled it is
  consumed from there, not developed there.
- **Departure debt, discovered 2026-09-01 while running the Němec demo:** the CLOVER pipeline as
  committed is **not runnable by anyone but Joris** — `script/run_p.sh` and `script/run_v.sh` source
  `/home/moczyjor/retrosyntesis/venv_chimie`, which is `Permission denied` outside that account, and
  no owner env had `aizynthfinder`. A working owner-side env (`conda activate nemec` on RCI) and
  replacement runners exist in `/mnt/data/resynthesis/NemecChallenge/scripts/`. Folding those back
  into this repo is the first task of owner operation.
- **`retro-physics-validation`'s slow start is deliberate** — the Phase 0→6 blind study is a
  *training curriculum* for inheriting the oracle, not an idle node. Do **not** re-charter it or
  install anyone else in it; that would destroy the mechanism the succession depends on.
- **Numerics travels with its owner**: Robin now → jinrehacek at handover. Artefacts that are numerics
  plumbing (e.g. `retrosyntesis/coordination/handover/reaction_complex.py`) move with it rather than
  being relocated in advance.
- **Robin's and Joris's most valuable remaining output is transferability**, not more results.
  Robin's is being handled by the owner in person.

### NEAR-TERM OBJECTIVE — numerics ready for Martin when he needs it
A working, documented, inheritable oracle able to label a **few thousand** reactions, so that
`retro-generation` can be handed **hard negatives** — plausible-but-high-barrier reactions, which no
corpus of successful reactions contains. Note the interface is a **delivered dataset, not a service**:
at ~22 min/reaction physics cannot supply training-scale labels, so `retro-generation` must not be
wired to the oracle and must not be blocked on it. Prerequisites, in order: the endpoint fix
integrated with its test → results and calling conventions on the shared store → the
completion/mapping layer (**still unowned**, see below) → a labelling run.

## What this orchestrator owns (cross-cutting only — never a child's primary framing)
- The **active-acquisition program** (organizing thesis): a calibrated surrogate that
  queries the expensive simulator (DFT/MLIP) only where uncertain + where it matters,
  growing the validated domain from a Suzuki/AIMNet anchor. Spans retro-pfn + MolGPT;
  MLIP-retrain / family-engine questions sit here / with the PFN family.
- The **K-P-V retrosynthesis program** framing — cross-cutting over the feasibility
  leaf (`retro-pfn`) and the external student (`retrosyntesis`); absorbed from the
  dissolved Synthesis layer.
- The **retro-pfn ⋈ MolGPT** convergence (PFN / ICL / generate-and-validate). After the
  2026-07-24 split the generate-and-validate seam is **retro-generation ⋈ retro-pfn**;
  MolGPT contributes molecule-side ICL/PFN evidence to it.
- The **uncertainty-signal question** (2026-07-28): whether *any* usable σ exists for this
  program. Cross-cutting by construction — it has now been tested and failed in all three
  leaves (GP-σ ⊥ error; epistemic-MCTS negative; in-context scale not learnable). No single
  leaf owns the verdict; it lives here.
- The **granularity-and-balance prerequisite** (2026-07-28): validation signals are measurement
  artifacts before they are chemistry (round-trip metric artifacts, lumped multi-step
  transformations, unbalanced/ionic entries). Constrains ξ_f, the oracle ladder, and the
  student validation tracks alike.
All in `coordination/synthesis.md` + `coordination/adr/`.

## On session start
Run `/coord status` — pull children's `coordination/outbox.md` (**retro-pfn, retro-planning,
MolGPT, retrosyntesis**), the two remaining student externals (`retro-generation`,
`retro-physics-validation` — `git fetch` them; their outboxes live on *their* main),
boundary inbound (`proposal`, `briefing`), open messages on the `~/agents` board.
Leaf outboxes go stale — for children, also check `git log` and the **working tree** of the
submodules (uncommitted work is invisible to a pointer pull) and recurse into declared
externals (`MolPFN`, `result_coordination`).
Publish the `briefing` (flow: out) as part of the cycle. Write only within this
subtree or the `~/agents` board/pool.

Literature pools to `~/agents/library` via `/lib add`/`/lib sota`; machine compute
invariant in `~/agents/compute`.

## Open decisions (2026-09-01, from the retrosyntesis reassignment)

1. **Make `retrosyntesis` a submodule?** `retro-pfn` and `retro-planning` are submodules;
   `retrosyntesis` is a gitignored sibling checkout, which was right while it was student-external
   and is now inconsistent with its owned status. Recommend converting, but it is a git-structure
   change with a pointer-tracking consequence — owner's call, not done automatically.
2. **Branch divergence is load-bearing, do not treat it as housekeeping.** `main` carries the full
   validation ladder (`validation_dft.py`, `validation_dft_neb.py`, `validation_energy.py`,
   `validation_kinetics.py`, `validation_skala.py`, `validationaimnet.py`, `validation_forward_ml.py`,
   plus `src/oracle_benchmark/`), and `main_validation.py` wires forward-ML → RDKit → rdchiral →
   MLIP → DFT → energy. The RCI checkout at `/mnt/data/resynthesis/retro-fallback-harness` sits on
   **`retropfn/active-xif`**, a stripped-down retro-pfn working branch with none of that. Any claim
   about "what the pipeline validates" must name the branch — an audit of the RCI checkout alone
   concluded there was no physics rung at all, which is true of that branch and false of `main`.
3. **Owner-side runnability.** See "Departure debt" above. The replacement env and runners live in
   `/mnt/data/resynthesis/NemecChallenge/scripts/`; folding them in is the first integration task.
