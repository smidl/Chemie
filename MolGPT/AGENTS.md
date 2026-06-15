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

## Role in the active-acquisition program (Chemie ADR 0003)
**Candidate proposer (T3):** a trained, in-context **reaction** generator for the
generate-and-validate loop (propose ↔ retro-pfn's ξ_f validates). The current MolPFN
(in-context *molecule* generation) is the infrastructure; the re-point to *reactions*
(balanced, σ/frontier-conditioned) is the expansion-phase direction — see
`coordination/inbox.md` (2026-06-15). The primary framing above predates ADR 0003 and
is being re-pointed accordingly.
