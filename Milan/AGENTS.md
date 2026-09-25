---
coord:
  enrolled: true
  role: leaf
  owners: [vsmidl]
  upstream: AIC/Chemie
  modules: [adr, messages]
  boundaries:
    - path: ./6aaa41c163a3372f92488d74
      remote: https://git.overleaf.com/6aaa41c163a3372f92488d74
      kind: paper
      flow: in
      link: repo
  external:
    - path: ./ArrowFlowMatching
      remote: git@github.com:mlnpapez/MechReact.git
      kind: collaborator
      owner: mlnpapez
---

# Milan — Arrow Flow Matching (AFM), collaborator track

Leaf of the Chemie tree, enrolled 2026-09-25. Canonical here; `CLAUDE.md` is a thin delta.
Parent orchestrator: `~/AIC/Chemie`. Protocol: `~/agents/protocol.md`.

## Primary framing (this node owns it)
**Measurement and strengthening of Milan Papež's Arrow Flow Matching** — a mechanism
generator over the bond–electron matrix whose elementary event is one curly arrow, so
electron, atom and proton conservation hold as an identity and validity is a table lookup.
Our role: characterise the released models and benchmark (extrapolation, alphabet coverage,
concertedness, termination, intermediate stability, human plausibility), find what the paper is
missing, and hand the findings to Milan. **We strengthen the paper; we do not take it over.**

The live plan is [`plan.md`](plan.md); collected numbers are in [`RESULTS.md`](RESULTS.md);
problem framings are `problem01-validity.md` and `problem02-termination.md`; handovers to
Milan are the `handover-*.md` files.

## Ownership split (the reason this node exists)
- **Milan's, never written into, no coordination files inside:**
  - `ArrowFlowMatching/` — checkout of his code repo. The GitHub repo was renamed
    **MechReact** (`mlnpapez/MechReact`; the old `mlnpapez/ArrowFlowMatching` URL redirects to
    it). Our branches (`filter-only`, `fix/radical-moves`) live on the `bayes` and `rci`
    remotes, not on his. Gitignored here.
  - `6aaa41c163a3372f92488d74/` — his Overleaf paper ("Arrow Flow Matching for Reaction
    Mechanisms", double-blind draft; `afm.pdf` is a snapshot). Boundary, `flow: in`: we pull and
    read, we do not push. Gitignored here.
- **Ours, tracked in the Chemie repo:** every note, plan, handover, analysis and experiment
  script in this folder.
- **Ours but not tracked (results live on RCI / in the pool, not here):** `experiments/*/results/`,
  `analysis/results/`, `experiments/*/data/` (contains RMechDB-derived fine-tune data, licence
  **CC-BY-NC-ND**, must never be committed), the experiment virtualenv, `_backup_20260921/`.

## Where the energy question lives
The AIMNet2-versus-AFM ranking experiment (does an energy along a generated mechanism rank
admissible candidates?) is **not** this node's science. It is the falsification probe of
`retro-pfn/flow-ts/`; this node supplies the candidate sets, checkpoints and reconstruction
code it consumes, and `retro-physics-validation` runs the MLIP rung. See Chemie
`coordination/synthesis.md`, 2026-09-25.

## Coordination
- Findings for Milan: a `handover-*.md` here plus a message to him outside the tree (email);
  nothing is written into his repo or Overleaf.
- Outward-relevant findings for the program → `coordination/outbox.md` (Chemie pulls it on
  `status`). Directives from Chemie → `coordination/inbox.md`. Local decisions →
  `coordination/adr/`.
- Inbound from the boundary: pull the Overleaf checkout on `status`; surface changes we did not
  author.
