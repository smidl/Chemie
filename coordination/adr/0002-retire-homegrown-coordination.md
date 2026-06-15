# ADR 0002 — Retire the homegrown thread-based coordination

Date: 2026-06-06 · Status: accepted · Owners: vsmidl

## Context
Synthesis had grown a full homegrown organizational + coordination scheme:
- `coordination/PROTOCOL.md` — a bespoke proposal/objection/resolution thread
  protocol, with one live thread `pfn-retro-handoff`.
- `README_ORGANIZATION.md`, `STATUS.md`, `PROJECT_DEPENDENCIES.md` — a
  navigation index, status board, and a `{project}-phase{N}` naming rule +
  "communication protocol" (notify upstream/downstream).

## Decision
Adopt `coord` in its place across the whole scheme:
- Migrate the live thread into `Synthesis/coordination/synthesis.md` (+ open
  item preserving the 2026-06-19 review).
- **Remove** `coordination/PROTOCOL.md` + thread folder, and the three org
  docs above.
- **Drop the `{project}-phase{N}` convention** entirely; re-express work in
  descriptive vocabulary (student validation track: baseline validation →
  route generation → feasibility-validator integration; PFN research track:
  feasibility-model training / validation, baseline feasibility methods).
- Keep `COMPUTE_AND_DATA.md` (infrastructure reference, not protocol) and all
  science/content docs.

Live state extracted before deletion: the phase snapshot → `coordination/
outbox.md`; the cross-track dependency → `coordination/synthesis.md`
(research-track internal detail lives in `retro-pfn/xif/PLAN.md`).

## Why (confirmed with owner, 2026-06-06)
The bespoke protocol could not generalise across trees; coord's
outbox/inbox/synthesis/ADR model supersedes it. Phase numbers were
uninformative bookkeeping. Scientific content is preserved, not lost.
