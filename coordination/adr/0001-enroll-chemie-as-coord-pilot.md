# ADR 0001 — Enroll Chemie as the coord pilot orchestrator

Date: 2026-06-06 · Status: accepted · Owners: vsmidl

## Context
Chemie is the first tree to adopt the machine-wide `coord` protocol (the
registry named it the pilot). An earlier homegrown coordination experiment
lived inside `Synthesis/` and was fused to one project's specifics.

## Decision
Enroll `~/AIC/Chemie` as the **top orchestrator**, with `Synthesis/` and
`MolGPT/` as enrolled **leaves**. Chemie root owns only cross-cutting science;
each leaf owns its primary framing. `RetroDemo/` and `datasets/` stay
unenrolled.

## Why (confirmed with owner, 2026-06-06)
Synthesis and MolGPT are at different stages but already overlap on PFN and
will share literature soon; a common orchestrator is the right home for that
derived, cross-cutting picture and for joint-literature synthesis. Synthesis
will itself become an orchestrator later (it will enroll children of its own).
