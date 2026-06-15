---
coord:
  enrolled: true
  role: orchestrator
  owners: [vsmidl]
  modules: [adr, synthesis, messages]
---

# Chemie — chemistry research (coord orchestrator, pilot)

Top orchestrator for the machine's chemistry research. Protocol spec and
behaviour: `~/agents/protocol.md` and `~/agents/AGENTS.md` (tier-0). This file
is canonical; `CLAUDE.md` is a thin delta.

## Enrolled children
- `Synthesis/` — leaf (orchestrator-to-come). K-P-V retrosynthesis + PFN
  reaction-feasibility research.
- `MolGPT/` — leaf. General-purpose molecule model (GPT → PFN).

Not enrolled: `RetroDemo/` (transparent), `datasets/` (shared data artifact).

## What this orchestrator owns (cross-cutting only)
Synthesis and MolGPT are independent today but **overlap on PFN** and will grow
a **shared literature** base. This node hosts only the derived, cross-cutting
picture — never a child's primary framing:
- `coordination/synthesis.md` — the running PFN-overlap picture across children.
- `coordination/adr/` — cross-cutting decisions that bind both children.

Literature pools to `~/agents/library/` (shared, machine-wide) via `/lib add`;
each leaf keeps its own `paper/refs.md` interpretation.

## On session start here
Run `/coord status` — pull children's `coordination/outbox.md`, open messages
addressed here. Write only within this subtree or the `~/agents` board/pool.
