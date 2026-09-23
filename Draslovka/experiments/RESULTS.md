# Draslovka pipeline probe — results & honest read

*What our current RCI stack actually delivers on 6 Draslovka products. Written to be
honest, including where the tools fail — this is demo-prep, and the failure modes are
the pitch.*

## The three probes
1. **Route to product** (`draslovka_eval.py`) — target removed from the 23M eMolecules stock.
2. **Feasibility of the proposed step** (`draslovka_feasibility.py`) — ReactionT5 forward round-trip.
3. **Feedstock-restricted deep routes + full audit** (`draslovka_deep.py` + `draslovka_feas_deep.py`)
   — force multi-step routes from bulk feedstock, then feasibility-audit *every* step.

## What we learned (in order of importance)

### 1. Route existence is trivial / uninformative
5 of 6 targets are **purchasable commodities** (they *are* the stock). With the target removed,
all solve in **1 step**. Standard value net and L\* are indistinguishable here. → The pitch is not
"can we find a route."

### 2. With realistic feedstock, the planner recovers genuinely Draslovka-relevant chemistry — a real positive
Restricting stock to bulk feedstock (HCN, acetone, cyanide, urea, benzil…) produced **chemically
meaningful** routes in places:
- **acetone cyanohydrin ← acetone + HCN** — the *correct industrial route*, and the feasibility
  audit **confirms it SOUND**. ✅
- the standard arm's hydantoin route goes **through acetone cyanohydrin** — the real Draslovka
  intermediate.
- L\* is **more search-efficient** where routes deepen (EDTA: **21 vs 49** expansions) — though not
  uniformly (hydantoin 5 vs 4 steps). Modest, non-uniform; don't oversell.

### 3. The routes contain one clearly-wrong step — plus a subtler thermo-vs-practical case
- **EDTA ← ethylenediamine + acetate** is **chemically wrong** (acetate can't alkylate the amine);
  audit correctly flags it **FAIL**. ✅
- hydantoin route's **methacrylic acid + water → 2-hydroxyisobutyric acid** is **NOT unsound**:
  xTB gives **ΔE ≈ −23 kcal/mol (thermodynamically favorable)**. It's a *valid but non-standard*
  prep (Markovnikov hydration, needs strong acid). So the T5 FAIL here is **not** a clean catch —
  it's the **"favorable ΔE ≠ practical feasibility"** case (thermodynamics vs kinetics/conditions),
  not a wrong reaction. (Corrected 2026-07-24.)

### 4. ⚠️ The off-the-shelf feasibility judge is TOO NOISY on their chemistry — high false-negative rate
This tempers my earlier "the feasibility layer catches the bad" line. As a per-step gate, ReactionT5
round-trip **rejects correct specialty chemistry**:
- **MMA ← methacrylic acid + methanol** (Fischer esterification) → wrongly FAIL
- **phenytoin ← benzil + urea** (the classic **Biltz** synthesis) → wrongly FAIL
- **chlormequat ← Me₃N + 1-bromo-2-chloroethane** (Menshutkin quaternization) → wrongly FAIL
- nitrile hydration (cyanohydrin → amide) → wrongly FAIL

Of 6 route verdicts, ~3 are misleading **false negatives**. The tool catches gross errors but also
rejects textbook-correct reactions — precisely the reactions central to Draslovka (esterification,
name-reaction condensations, quaternization, nitrile chemistry), which are under-represented or
condition-sensitive for a generic USPTO-trained forward model.

## Bottom line for the pitch (honest)
- **We have:** a working **search** stack (recovers real Draslovka intermediates from feedstock) +
  L\* search-efficiency + a feasibility **framework**.
- **We do NOT have (yet):** a feasibility judge that is *trustworthy on their chemistry* — the
  off-the-shelf single model is roughly a coin-flip as a gate on their specialty reactions.
- **Therefore the deliverable = the thing to build together:** a **multi-signal, condition-aware,
  mechanism/physics-anchored feasibility layer tuned on Draslovka reaction data.** The false
  negatives here (Biltz, esterification, Menshutkin) are exactly the domain/condition gaps their
  data + our mechanism-kernel/physics-oracle work would close.

This is the "**this is standard → here's where it breaks on your chemistry → with your data we build
the trustworthy layer**" ladder — now evidenced, warts and all, on their own molecules.

## Files
`results/{standard,lstar_retro,lstar_seea}.json` (probe 1), `results/feasibility.json` (probe 2),
`results/deep_{standard,lstar}.json` + `results/feas_deep_{standard,lstar}.json` (probe 3).
RCI home: `/mnt/data/resynthesis/draslovka/`.
