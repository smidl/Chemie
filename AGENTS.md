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
---

# Chemie — chemistry research (coord orchestrator, pilot)

Top orchestrator for the lab's chemistry research. **Pilot, flat** — the Synthesis
orchestrator layer was dissolved on 2026-06-15 (coord flatten). Protocol:
`~/agents/protocol.md`. This file is canonical; `CLAUDE.md` is a thin delta.

## Enrolled children (peer leaves)
- `retro-pfn/` — reaction-feasibility & energetics modeling toward ξ_f (the
  retrosynthesis-feasibility project). **Submodule** (`aicenter/retro-pfn`).
- `MolGPT/` — general-purpose molecule model, GPT→PFN; reaction-generator direction.
- `retro-planning/` — **learned search heuristics** for retrosynthesis planning
  (the search-`h` side). Seeded 2026-06-18 from the status finding that the
  190-hard budget wall is search guidance, not feasibility (SAScore `h` vs a
  learned rank-trained `h`). Sibling to retro-pfn: it owns `h` (which node to
  expand); retro-pfn owns ξ_f (edge costs). They compose on the same syntheseus
  harness. **Submodule** (`aicenter/retro-planning`).

## External & boundary (declared here — Chemie is the single inventory owner)
- `retrosyntesis/` — **external** student route-generation/validation repo (inventory only).
- `proposal/` — **boundary**, Overleaf paper (`flow: both`).
- `briefing/` — **boundary**, the colleague knowledge base
  (`aicenter/retrosyntesis-knowledgebase`, `flow: out`, submodule): the outward
  "what we know / what we tried" digest for expert colleagues.

(MolGPT declares its own external `MolPFN` + boundary `phd-proposal` in its marker;
they roll up under this tree.)

## What this orchestrator owns (cross-cutting only — never a child's primary framing)
- The **active-acquisition program** (organizing thesis): a calibrated surrogate that
  queries the expensive simulator (DFT/MLIP) only where uncertain + where it matters,
  growing the validated domain from a Suzuki/AIMNet anchor. Spans retro-pfn + MolGPT;
  MLIP-retrain / family-engine questions sit here / with the PFN family.
- The **K-P-V retrosynthesis program** framing — cross-cutting over the feasibility
  leaf (`retro-pfn`) and the external student (`retrosyntesis`); absorbed from the
  dissolved Synthesis layer.
- The **retro-pfn ⋈ MolGPT** convergence (PFN / ICL / generate-and-validate).
All in `coordination/synthesis.md` + `coordination/adr/`.

## On session start
Run `/coord status` — pull children's `coordination/outbox.md` (retro-pfn, MolGPT),
boundary inbound (`proposal`, `briefing`), open messages on the `~/agents` board.
Publish the `briefing` (flow: out) as part of the cycle. Write only within this
subtree or the `~/agents` board/pool.

Literature pools to `~/agents/library` via `/lib add`/`/lib sota`; machine compute
invariant in `~/agents/compute`.
