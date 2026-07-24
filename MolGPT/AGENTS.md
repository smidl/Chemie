---
coord:
  enrolled: true
  role: leaf
  owners: [vsmidl]
  boundaries:           # declared, never managed; we pull, we do not own
    - path: ./phd-proposal
      remote: https://git.overleaf.com/69c939021526657f4e385f9d
      kind: proposal
      flow: in           # advising only — pull literature/prose, never push
      link: repo
  external:             # registered, never managed (inventory only)
    - path: ./MolPFN
      remote: git@github.com:rektomar/MolPFN.git
      kind: student
---

# MolGPT — general-purpose molecule model (GPT → PFN)

Leaf node of the Chemie tree. Canonical here; `CLAUDE.md` is a thin delta.
Parent orchestrator: `~/AIC/Chemie`. Protocol: `~/agents/protocol.md`.

## Primary framing (this node owns it)
A general-purpose generative model of molecules, **starting from a GPT
architecture and aiming toward a PFN** (prior-data fitted, in-context). This is
the long-run research line; it overlaps with `retro-pfn/` on PFN (the
cross-cutting picture lives at the Chemie root, `coordination/synthesis.md`),
and retro-pfn may become a downstream use later — not yet.

## External & boundary (managed, not owned)
- `MolPFN/` — **external** student repo (`rektomar`): "A PFN-like model for
  conditional molecule generation based on molecular properties." Inventory
  only; never write into it. Advisory overview: `molpfn-advice.md`.
- `phd-proposal/` — **boundary** (Overleaf), the student's PhD thesis proposal;
  we advise only (`flow: in`), never push or write coordination files into it.
  Inbound flow: relevant **literature → the pool** (`/lib add`), relevant
  **prose → local notes**. We pull only the **transformer-based generative
  models** part (MolGPT + PFN chapters); the **probabilistic-circuits (PGC)**
  part is out of scope and ignored. Transformer-part import: `phd-proposal-notes.md`.

## Coordination
Leaf with no enrolled children. `coordination/` is live: outward-relevant findings →
`coordination/outbox.md` (Chemie pulls on `status`); directives from Chemie arrive in
`coordination/inbox.md`. Cross-cutting PFN/convergence items also surface in the root's
`coordination/synthesis.md`.

## Reaction-generation line — handed off to `retro-generation/` (2026-07-24)
The **reaction**-generation direction (in-context reaction proposer for the
generate-and-validate loop) has been **moved out** to the sibling student leaf
**`retro-generation/`** (owner rektomar) — see `retro-generation/HANDOVER.md` and
`retro-generation/coordination/adr/0001`. **MolGPT continues the *molecule*-generation
track** (GPT → PFN); the two tracks run **in parallel**, with any retirement decided later
based on which proves more promising. `MolPFN/` stays here as the molecule-generation
infrastructure. (Earlier notes casting MolGPT as the reaction proposer / ADR-0003 T3 are
superseded by this split.)
