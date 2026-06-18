# Outbox — Chemie (orchestrator)

Append-only, skimmable. Outward-relevant findings this node wants its parent
(tier-0) to be able to pull. One line per entry: `YYYY-MM-DD — summary`.

<!-- Program log migrated from the dissolved Synthesis layer (2026-06-15). Leaf-level
     detail lives in retro-pfn/coordination/outbox.md; these are program-level entries. -->
2026-06-06 — Student baseline validation complete: Retro-Fallback on PaRoutes (212 targets) — 35% coverage, 95% precision; Medium 43–58% vs Deep OOD 0%; bottleneck = budget exhaustion.
2026-06-10 — Coord channel with student repo (retrosyntesis) established (enrolled, outbox/inbox on their main).
2026-06-10 — Student route-generation results in (5 approaches); reference-match FP/FN flagged UNSOUND for ξ_f calibration; students re-tasked with sound discriminators (round-trip, Retro-BLEU, SSP, RetroTrim).
2026-06-12 — COMPUTE_AND_DATA reconciled against tier-0 compute catalog (ADR 0001); machine RCI invariant referenced from ~/agents/compute, project layout kept.
2026-06-12 — Route-B metric REFRAMED (significant): SSP is confounded (correlation removes backups → rewards weak correlation, not accuracy) → calibration (primary) + correlation-specific test; student 190-SSP scale-out HELD.
2026-06-13/14 — Mechanism-kernel ξ_f recalibrated (clean marginal banked); decisive hard-target (c) test handed to student track; AIMNet2-Pd scope-checked (Suzuki-only, gated GO, use-not-retrain).
2026-06-14 — STRATEGIC DIRECTION (owner-originated) → adopted by Chemie: active-acquisition thesis as the program's organizing direction (calibrated surrogate queries DFT/MLIP only where uncertain + where it matters, grown from a Suzuki/AIMNet anchor). MLIP-retrain / family-engine questions routed to Chemie + PFN family.
2026-06-15 — coord RESTRUCTURE: flattened to pilot-flat — Synthesis orchestrator layer dissolved; retro-pfn + MolGPT now direct Chemie leaves; briefing (retrosyntesis-knowledgebase) added as flow:out boundary; all externals/boundaries declared at Chemie.
2026-06-18 — NEW LEAF `retro-planning` seeded: student 190-hard deliverable showed the hard/OOD wall is SEARCH GUIDANCE, not feasibility (failures 100% budget-exhaustion ERROR_TYPE_5, 1664/1664; SAScore is the cost-to-go `h`). Two-knob split: retro-pfn owns ξ_f (edge costs), retro-planning owns `h` (learned, rank-trained, uncertainty-aware cost-to-go). Same syntheseus harness; shared 190-hard benchmark; metric budget-to-solve/stratum. First obligation: SOTA lit pass (rank-loss heuristics / Retro* successors) before build. Surfaces 3 convergences (rank-not-estimate both sides; σ-as-exploration reframes σ⊥error; PFN/DecisionBO fit).
