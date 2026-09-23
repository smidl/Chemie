# Our angle — conditioning generation on disconnection type

Core: [[sota/control-tokens-in-reaction-generation]] · local, 2026-09-13, revised after `/lit`.

> **Verdict: the mechanism is taken; the axis is not; and the axis may not be worth a paper.**
> Read this before proposing the work.

## Our question
Can a proposer be asked for a step that *reduces the synthetic problem*, rather than being
re-ranked after the fact?

## Why we care — two measurements of ours, not a hunch
1. **Proposals that grow the target are the failure mode.** Across 24 targets, ReactionT5
   proposes a largest-precursor *larger* than the product in **74 %** of cases (median size
   ratio 1.11) against AiZynthFinder's **36 %** (median 1.00). On MU1700 it explored 806 k nodes
   for 26 routes where AiZynthFinder gave 867 — with chemically *better* proposals. See
   `coordination/synthesis.md` §OPEN PROBLEM 2026-09-06.
2. **Typing works, and typing-by-separate-model is what breaks.** Asking `ringbreaker` directly
   moves the ring-forming disconnection from rank 25 / prior 0.0027 to **rank 3 / prior 0.045** —
   a 17× prior increase, the largest single effect we measured on MU1700. But concatenating that
   policy with `uspto` produced pairwise-**disjoint** route sets across three configurations,
   because the priors are independently normalised.

## What the literature already did — by the two groups whose tools we run
- `thakkar2023_disconnection-prompts` (IBM RXN) prompts the single-step model with an **atom tag
  marking the site**. +39 % accuracy, 2× reaction-class diversity. Same motivation as ours:
  training-data bias toward abundant classes.
- `westerlund2025_human-guided-prompting` (AstraZeneca, **Genheden** — who also wrote the route-TED
  metric we use) put it **inside AiZynthFinder**: frozen-bonds filter, a broken-bonds score, and
  **multi-objective MCTS**. 75.57 % vs 54.80 % on PaRoutes.
- `thakkar2020_ring-breaker` is the separate-model incumbent, and gives the reason typing is needed:
  ring-forming reactions are **4.5–5.8 %** of USPTO/Reaxys.

So "condition the generator, and let the planner ask" is done, published, and shipped in our own
stack. Any proposal of ours starts from there, not from zero.

## The gap we would exploit
Conditioning by **token** rather than by separate model removes the prior-scale failure *by
construction* — one model, one normalised distribution. And the labels are free: our
disconnection descriptor (`NemecChallenge/scripts/disconnection_metric.py`, validated on
textbook reactions: invariant to reagent and leaving-group swaps, correctly refusing to call an
FGI a disconnection) derives `bond` / `ring` / `fgi` from (product, reactants) with no atom
mapping. Any retro corpus auto-labels.

It also fits `retro-generation`'s brief as a new row in its §1 table — *observed* = RHS +
disconnection type, *queried* = LHS — and needs **neither balanced data nor conditions**, the two
things the 2026-09-13 completion result foreclosed.

## The honest size of the remaining gap
All published control is **site-level** — "break these atoms" / "this set of bonds". Nothing
conditions on **structural type**, and neither paper measures molecule size or complexity at all
(0 hits in both full texts). A site request presupposes knowing where to cut; a type request does
not — that asymmetry is real.

But `westerlund2025`'s MO-MCTS would accept a type objective as readily as a bond one, so the
architectural contribution is nil. **The defensible part is not the token — it is the measurement
behind it**: that a 71 %-top-1 proposer grows the molecule in 74 % of proposals and therefore cannot
converge. Nobody in this line measures that. If we pursue this, the paper is the *diagnosis*, with
the control token as the remedy, not the reverse.

## What would kill it
- **The label is too lossy.** Our descriptor returns `other` for additions where oxidation state
  changes at the forming bond (Grignard). If `other` is a large share of USPTO-50k, there is
  nothing clean to condition on. *This is the one cheap measurement that gates everything.*
- **The model ignores the token**, because the type is predictable from the input.
- **The planner cannot decide what to ask for** — a search-policy question we have not posed.
- **The honest baseline beats it.** Enumerate candidate sites and push them through
  `westerlund2025`'s existing multi-objective machinery. If that recovers reducing steps as well as
  a type token does, the token is a convenience, not a contribution. **This is the comparison to
  run first, and we have not run it.**

## Positioning
This is a **generation** idea. It is complementary to the scoring/likelihood line and must not
be used to justify it, or vice versa.
