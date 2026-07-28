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
    - path: ./retrosyntesis
      remote: git@github.com:aicenter/retrosyntesis.git
      kind: student
    - path: ./retro-generation
      remote: git@github.com:aicenter/retro-generation.git
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
- `retrosyntesis/` — **external** student route-generation/validation repo (inventory only).
- `retro-generation/` — **external** student **reaction-generation** repo (owner rektomar,
  `aicenter/retro-generation`); handoff of the generative-reaction line from MolGPT (2026-07-24).
  Inventory + coordination (inbox/outbox) only.
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
MolGPT**), the three student externals (`retrosyntesis`, `retro-generation`,
`retro-physics-validation` — `git fetch` them; their outboxes live on *their* main),
boundary inbound (`proposal`, `briefing`), open messages on the `~/agents` board.
Leaf outboxes go stale — for children, also check `git log` and the **working tree** of the
submodules (uncommitted work is invisible to a pointer pull) and recurse into declared
externals (`MolPFN`, `result_coordination`).
Publish the `briefing` (flow: out) as part of the cycle. Write only within this
subtree or the `~/agents` board/pool.

Literature pools to `~/agents/library` via `/lib add`/`/lib sota`; machine compute
invariant in `~/agents/compute`.
