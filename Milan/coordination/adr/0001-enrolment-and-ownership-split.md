# ADR 0001 — Enrol the Milan folder as a leaf; split ownership between Milan and us

**Date:** 2026-09-25. **Status:** accepted.

## Context
The folder held substantial owner-authored work (plan, results, handovers, analysis and
experiment scripts) but was wholly gitignored and absent from the Chemie inventory, so a
sweep read it as an orphan and none of the notes were versioned. It also holds two checkouts
that are Milan Papež's: his code repo (GitHub `mlnpapez/MechReact`, formerly
`ArrowFlowMatching`) and his Overleaf paper.

## Decision
- Enrol `Milan/` as an owner-operated **leaf** (owners `[vsmidl]`, modules `adr, messages`).
- Declare the Overleaf checkout as a **boundary** (`paper`, `flow: in`) and the code checkout
  as an **external** of kind `collaborator` (owner `mlnpapez`). Neither receives coordination
  files; neither is tracked here.
- Track our documents and scripts in the Chemie repo. Keep results, data (RMechDB-derived,
  CC-BY-NC-ND), the virtualenv and the backup folder ignored.
- Keep the checkout folder name `ArrowFlowMatching` so paths in existing notes stay valid.

## Consequences
- The AFM measurements become versioned and visible to `/coord status`.
- The energy-ranking study (AIMNet2 vs AFM) is placed in `retro-pfn/flow-ts/`, not here;
  this node is its input supplier.
