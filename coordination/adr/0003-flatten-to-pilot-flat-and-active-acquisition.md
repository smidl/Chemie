# ADR 0003 — Flatten Chemie to pilot-flat; active-acquisition program; briefing boundary

Date: 2026-06-15 · Status: accepted · Owners: vsmidl

## Context
The tree had grown **top-heavy**: three coordination surfaces (Chemie, Synthesis,
and a leaf — `retro-pfn` — whose `coordination/` was generating program-level
theses) sat over essentially **one active research locus**. The coordinator-to-work
ratio was inverted; program strategy was accreting in a leaf for lack of a
horizontal home. Scope is a **pilot** before larger involvement, with new projects
expected.

## Decision
1. **Flatten to one coordinator.** Dissolve the Synthesis orchestrator layer.
   `retro-pfn` and `MolGPT` are **peer leaves directly under Chemie**. Chemie is its
   own git repo (`smidl/Chemie`); project repos are **submodules** (`retro-pfn`,
   `briefing`); externals/boundaries are declared at Chemie (single inventory owner).
   Synthesis's content was re-homed: cross-cutting → Chemie `coordination/`;
   prior-art notes + plans → `retro-pfn/docs/`; loose PDFs → `_lib-inbox/` for `/lib add`.
2. **Structure rule (role, not depth).** A layer earns itself only by **span ×
   genuine cross-child synthesis**. *Default: a new project is a peer leaf under
   Chemie.* Introduce a program layer **only when a cluster reaches ≥2 peer projects
   with live cross-coordination** — created then, populated, not in anticipation.
   Science branches freely as **folders inside a leaf**; promote a branch to a **node**
   only when it crosses an **actor boundary** (own external/boundary/children) — down
   (a child of the leaf) or out (its own node).
3. **Active acquisition = the organizing program** (cross-cutting at Chemie): a
   calibrated surrogate queries DFT/MLIP only where uncertain + where it matters,
   growing from a Suzuki/AIMNet anchor. Loop = propose → surrogate(σ) → acquire →
   oracle → absorb. Owners: surrogate+oracle = `retro-pfn`; candidate proposer =
   `MolGPT` (expansion); acquisition engine + in-context absorption = **PFN family**
   (`PFN4BOrevisited`, `~/AIC/PFNs`), woven at join points. MLIP-retrain question is
   program-level (Chemie + family), deferred.
4. **Briefing = `flow: out` colleague boundary** (`aicenter/retrosyntesis-knowledgebase`,
   submodule): a two-axis KB — **what-we-know** (prior art, via `/lib sota` cores +
   digests, cited by DOI) and **what-we-tried** (experiments + outcomes incl.
   negatives, from outboxes/result docs). A signpost to the substance.

## Why (confirmed with owner, 2026-06-15)
Role-based recursion: the layers weren't earning their span; flattening matches
coordination to actual breadth, gives the program a proper home (so it stops
accreting in a leaf), and keeps the pilot light. Re-introduce a program layer the
moment a second peer project in a cluster is real.

## Consequences
- One coordination altitude (Chemie) over peer leaves; 3 surfaces → 1.
- `retro-pfn` local commits (docs absorb + marker) and the briefing seed are **not yet
  pushed**; the Chemie superrepo points at local submodule commits → push submodules
  before/with the superrepo.
- Supersedes the Synthesis-layer routing in ADR 0001/0002's structural assumptions
  (their literature/compute decisions still hold).
