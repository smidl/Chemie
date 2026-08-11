# Topic A in relation to DecisionBO and Planning

**Date:** 2026-08-11 · Positioning for the proposal, and a boundary agreement so three tracks do not
collide.

## The three ask one question in three settings

| node | its own framing | in the C1–C4 language |
|---|---|---|
| **DecisionBO** (`~/zcu/PFN4BOrevisited/DecisionBO`) | when does better *modelling* improve the *decision*? | **C3 actionability**, for the training objective |
| **Planning** (`~/AIC/Planning`) | how should the guidance function be *trained*, and how should *exploration* be driven, to expand as few nodes as possible? | **C1 estimability** + **C4 set-selection**, in a sequential setting |
| **Topic A** | when does adaptive sampling beat i.i.d.? | **C1–C4**, pool-based, with C2 measurable |

The correspondence is not decorative. **Regret-relevant sufficiency** — DecisionBO's central
result, that model quality stops mattering above a threshold set by budget and search — *is* C3,
proved for one lever (the training objective). Topic A would generalise the same statement to a
different lever (which labels you buy). And Planning's "uncertainty-aware exploration" is the
acquisition problem with the pool replaced by a search frontier and the label replaced by a node
expansion.

So C1–C4 is a candidate **shared abstraction for the whole program**, not just this thesis. That is
worth stating in the proposal: it positions the work inside a research programme rather than as a
one-off application study.

## What each track can and cannot see

This is the substantive part, and it argues for the thesis rather than merely relating it.

**Only Chemie has irreducible label noise.** DecisionBO optimises expensive but *deterministic*
simulators; Planning studies *cheap controllable benchmarks* by design. In both, repeating a query
returns the same answer, so **C2 reducibility is invisible to them** — their uncertainty is
epistemic by construction. Wet-lab HTE data is the only place in the entire machine where a label
can be genuinely, irreducibly noisy.

That is topic A's structural contribution to the programme: **it supplies the noise axis the sisters
cannot study**, and C2 is exactly the condition under which the classical theory says adaptivity's
advantage collapses.

**Only Planning has a real sequential decision.** Its frontier selection is a genuine set-selection
problem under a budget, which makes C4 sharper there than in pool-based AL.

**Only DecisionBO has run the sufficiency sweep at scale.** Its capacity/quality sweep is the
established method for testing C3, and topic A should borrow it rather than reinvent it.

## What A takes, and what it gives back

**Takes.**
- The **sufficiency framing** and the capacity-sweep protocol (C3), from DecisionBO.
- **ADR 0004**, in particular *random is the bar* and the **initial-design pseudo-replication** rule
  (`run seed = base + s + 9973·i`). AL curves are unusually exposed to this, and the existing runs
  here use two seeds.
- From Planning, the finding that objective **structure** mattered where uncertainty machinery did
  not — a prior that A should try to break rather than assume.

**Gives back.**
- **C2, which neither can measure.** If adaptivity fails on noisy labels and succeeds on
  deterministic ones under an identical protocol, that bounds how far both sisters'
  uncertainty-driven results can transfer to any noisy application.
- **An ex-ante diagnostic.** DecisionBO put a question to us on 2026-08-02 and it is still open:
  *is there a cheap ex-ante diagnostic for being below sufficiency, or must it be established by
  sweeping capacity each time?* Topic A's headline deliverable is that diagnostic, generalised
  beyond BO. Answering it discharges a live cross-tree message.

## Boundary agreement — to keep three tracks from colliding

Proposed, and worth recording before the proposal is written:

| | owns | does not touch |
|---|---|---|
| **DecisionBO** | decision-focused **training** | which points to acquire |
| **Planning** | **sequential** selection over a search frontier; how `h` is trained | pool-based acquisition; noisy labels |
| **Topic A** | **pool-based acquisition** under a fixed budget; the noise axis | training objectives; frontier expansion policy |

The sharp line is **pool versus frontier**. If Ayman drifts into choosing which *node to expand*, he
is in Planning's territory and competing with the owner's own line. Pool-based acquisition with a
real noise contrast is unoccupied and is where his comparative advantage lies.

## One risk worth naming early

All three tracks share ADR 0004 and now, if this is adopted, a shared abstraction. That is an
asset — a result in one becomes a boundary test for the others — but it also means **a
methodological error propagates across three trees**. The seeding trap already did exactly that: it
was found in DecisionBO, transferred here, and forced a re-run of a published-to-colleagues number.
Shared standards are only worth having if each tree re-tests them rather than inheriting them on
trust.
