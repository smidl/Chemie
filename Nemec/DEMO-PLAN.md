# Demo plan — the Němec 5 through our actual stack

Written 2026-09-01. Purpose per owner: **find where our tooling is blind.** Not a
planner bake-off; not a dump of every arm. One route per target, assessed as far
up the ladder as the ladder actually goes, and an honest map of where it stops.

---

## 1. Do we have a plan? Yes — it is CLOVER, and it has run this exact shape

`/mnt/data/resynthesis/retro-fallback-harness` (conda env `rfb`) implements
precisely the workflow described: take a molecule → build its stock → plan →
validate in layers → emit a per-route report.

```
main.py --config_dir config/ --targets config/target_X.json \
        --models {aizynthfinder,g2g,retroxpert,askcos} --iterations 100 --depth 5
```

Per-target config is two fields (`name`, `smiles`), optionally plus hand-injected
knowledge actions (`target_paracetamol_custom.json` shows the format). It has been
run end-to-end on **aspirin, ibuprofen, naproxen, paracetamol, salbutamol**, and
the artifacts are on disk: `/mnt/data/resynthesis/data/<target>/` containing
`stock_k.txt`, `temp_config.yml`, `raw_plan_aizynthfinder.json`, and a
`report_aizynthfinder_route_N.md` per route with ACCEPTED/REJECTED and a reason.

So the machinery exists. The demo is not a build; it is **a run plus a diagnosis.**

### But the ladder is shorter than the reports claim — check this first

The aspirin report on disk says:

```
###  Validation
* **RDKit (Physical/Stock):** 7 accepted
* **RDChiral (Stereochem):** 7 accepted
* **DFT (thermodynamic):** 5 accepted
```

and one route carries `ERROR_TIMEOUT_OR_CRASH: Job timed out or crashed during
DFT/NEB validation.`

**There is no DFT rung in the current pipeline.** `grep -rn "DFT\|NEB"` over
`src/` and `main.py` returns nothing; `main_validation.py` runs exactly two
steps (RDKit/stock, then rdchiral); `src/utils/report.py` computes only
`RDKit` and `RDChiral` counts; the current `json_to_md.py` template has no DFT
line, and the `ERROR_TIMEOUT_OR_CRASH` string does not exist anywhere in the
tree. Those aspirin artifacts are from an **older revision** that advertised a
physics rung.

This matters beyond housekeeping: **our physics capability
(`/mnt/data/resynthesis/admissibility/`: xTB, ORCA 6.1.1, NWChem, autodE, NEB,
AIMNet2) is real but is not wired to the planner.** It consumes hand-picked
reactions in a separate research line. The demo will make that seam visible,
which is exactly the kind of blind spot we are looking for. **Do not delete the
stale reports before the run** — they are evidence of how easy it is to read a
validation verdict that was never computed.

*(Related fragility, not currently firing: `validation_rdchiral.py` returns
`True` — accept — when rdchiral is missing, and returns `False` — reject — when
rdchiral throws. So an absent library silently passes everything and a crashing
one silently fails everything, and the report looks identical either way.
rdchiral **is** installed in `rfb`, so today it genuinely runs. Add an explicit
`UNAVAILABLE` state before anyone trusts this rung on stereo-heavy input.)*

---

## 2. Why these five molecules are the right input

Not because they are hard. Because they are a **designed contrast on the one
difficulty axis this tree has actually measured.**

Three independent lines here converge on stereochemistry: the `E4/E5/E6_stereo*`
probes, the oracle's 8.57 kcal/mol penalty for stereo-free input, and the 190-hard
`far` stratum being partly easier through carrying fewer stereocentres. The
measured dose–response (`admissibility/out/stereo.json`, PaRoutes single-step
recall@20, AZF and ReactionT5):

| assigned stereocentres | n | AZF | RT5 | both | either |
|---|---|---|---|---|---|
| 0 | 4102 | 81.8 | 82.0 | 71.4 | **92.4** |
| 1 | 1093 | 83.2 | 80.9 | 69.7 | 94.3 |
| 2 | 369 | 76.7 | 80.8 | 66.4 | 91.1 |
| 3 | 85 | 69.4 | 68.2 | 51.8 | **85.9** |
| 4+ | 108 | 75.9 | 71.3 | 62.0 | 85.2 |

And the burden is **assigned** stereochemistry (both-miss/both-hit ratio 2.291),
not merely *possible* stereochemistry (unassigned ratio 1.031, i.e. no effect).
Size-matched the effect shrinks but survives (1.230).

The Němec sample splits cleanly along that axis:

| target | assigned centres | unassigned | bin |
|---|---|---|---|
| pleuromutilin | **8** | 0 | past the end of the table |
| bilobalide | **4** | 2 | 4+ |
| bilobalide-analogue1 | **4** | 2 | 4+ |
| MU1700 | 0 | 0 | the 0 bin — control |
| MU1700-analogue1 | 0 | 0 | the 0 bin — control |

Three stereo-dense targets and **two achiral controls**, one of which
(MU1700) the chemist synthesised himself and calls "not too difficult". That is a
better-formed probe than anything we would have assembled ourselves, and the
controls are what make a negative on the natural products interpretable.

The second gift is `E5_stereo_intervention.py`: stripping stereochemistry from
both query and reference recovers only **+2.84 pp** (2 assigned) and **+2.11 pp**
(3+), 7 steps recovered and 0 lost. So the stereo deficit is **mostly a genuine
chemistry gap, not an exact-match descriptor artifact.** We should expect the
natural products to fail for real reasons, and we can say so with a number.

---

## 3. The stock question — and it is a blind-spot probe, not setup

The precedent is `/mnt/data/resynthesis/data/salbutamol/stock_k.txt`: **27,444
molecules**, a per-target slice, not the full catalogue. Source inventory is
eMolecules (`retro_fallback_iclr24/iclr24_experiments/eMolecules/`, 14.9 M
molecules, 6 price tiers) plus the benchmark stocks at
`data/1-benchmarks/stocks/` (`buyables-stock.txt`, `zinc_stock.hdf5`, n1/n5).

Run **three stocks per target**, because the disagreement between them is a
measurement:

- **S-cat — commercial.** eMolecules restricted to cheap tiers (0–2). What a
  medicinal chemist can order. This is the realistic setting for MU1700 and its
  analogue.
- **S-bulk — platform feedstock.** ~40 hand-listed commodities, the pattern
  already used in `Draslovka/experiments/scripts/draslovka_deep.py` (`FEEDSTOCK`:
  HCN, acetone, urea, benzil, glycine, ethylene…), extended for this sample with
  terpene/lactone-relevant bulk. Forces genuinely multi-step routes.
- **S-pool — chiral pool.** Cheap enantiopure building blocks (amino acids,
  terpenes, sugars, tartrate, lactate…). **This is the one that probes the blind
  spot.** eMolecules tiers are priced per catalogue entry with no notion of
  whether a *configured* centre is cheaply available. For an 8-stereocentre
  terpenoid the difference between "buyable" and "buyable in the right
  configuration" is the whole synthesis, and our stock representation cannot
  express it.

**Pre-registered:** S-cat will make the two MU1700 targets trivial and will leave
the natural products either unsolved or solved through absurd disconnections.
Draslovka already showed the shape — 6/6 solved but "multi-step routes are
chemically unsound (EDTA via acetate alkylation = wrong)", errors compounding
with depth. If that reproduces here it is the second headline, and it is
evidenced on the chemist's own molecules rather than on a benchmark.

Practical: build all three with a small script, canonicalise, and **always remove
the target itself from stock** (the Draslovka driver does this — `known.discard(smi)`
— and forgetting it is how you get a one-step "route").

---

## 4. The ladder, as it actually stands, and what each rung can be asked

| # | rung | asset | status | what it cannot do |
|---|---|---|---|---|
| 0 | stock membership | `stock_k.txt`, eMolecules | works | no notion of stereo availability, price, or scale |
| 1 | template / rule | AiZynthFinder policy, CLOVER `planning_aiZynthFinder.py` | works | template coverage is USPTO-shaped; NP chemistry is thin there |
| 2 | learned single-step | ReactionT5 (`rxnt5_venv`), Chemformer, LocalRetro, G2G, RetroXpert | works | recall drops with assigned stereocentres (§2) |
| 3a | structural validation | `validation_v.py` — RDKit sanitise + stock | works | pure syntax; accepts chemically absurd but valid SMILES |
| 3b | stereo validation | `validation_rdchiral.py` | works, but silent-fail modes (§1) | needs a reaction SMARTS; conflates crash with rejection |
| 4 | forward round-trip | ReactionT5, per `draslovka_feasibility.py` | works, **not in CLOVER** | artifact-prone: false-neg chlormequat, false-pos EDTA |
| 5 | mechanistic | FlowER (`/mnt/data/resynthesis/FlowER`, checkpoints present) | deployed, never wired | needs balanced, mapped reactions |
| 6 | physics barrier | admissibility: xTB, ORCA, NWChem, autodE, NEB, AIMNet2 | deployed, **not wired to planner** | ~22 min/reaction; refuses unbalanced input |

Rung 6 has a hard, measured gate: **2.4 % of USPTO records are atom-balanced
(6/250), and 10/11 real planner steps were unbalanced so xTB refused.** Any
per-step physics verdict in this demo therefore needs the completion/mapping
layer, which is **unowned**. Do not plan around getting barriers for every step —
plan to report honestly that we cannot, and to get barriers for the two or three
steps that survive.

Also apply the known fix if rung 6 runs at all: **relax both endpoints at the
NEB's own level before interpolating** (arm E of the 07-30 mechanism work).
Without it the 0/11 result reproduces and measures our converter, not chemistry.

---

## 5. Plan

**Phase A — provision and reproduce (½ day).**
Copy the 5 targets into `config/target_nemec_*.json`. Re-run CLOVER on **aspirin**
first as a positive control; confirm it reproduces the on-disk report *minus* the
phantom DFT line. Standing rule in this tree: a negative counts only if the
control passed in the same run.

**Phase B — stock construction (½ day).**
Build S-cat / S-bulk / S-pool per §3. Record, per target and per stock, whether
the target itself and its obvious precursors are in stock. For MU1700 ask Němec
for his actual starting materials — that turns S-cat from a guess into ground
truth for one target.

**Phase C — plan (1 day, RCI).**
5 targets × 3 stocks × {AZF template, ReactionT5} = 30 runs, 100 iterations,
depth 5, 3 seeds. Small enough to be cheap, structured enough to attribute a
failure to stock vs policy.

**Phase D — assess the surviving routes, rung by rung.**
Take the **top route per (target, stock)** — not all routes. For each step record:
in stock · RDKit valid · rdchiral verdict · round-trip score (rung 4, run
separately via `rxnt5_venv` as in `draslovka_feasibility.py`) · atom-balanced
(y/n) · FlowER verdict if balanced · barrier if it survives to rung 6.
**And, cross-cutting: a stereo audit** — for each step, does the product's
configuration follow from the reactants, is a centre set/carried/destroyed, and
did any centre get silently dropped? Our own S3 numbers say steps that *create* a
centre are the least-missed (4.6 % both-miss) and steps that *destroy* one the
most (9.6 %), so record which kind each step is.

**Phase E — the blind-spot map.**
A 5 × 7 grid, target × rung, each cell one of: **answered** / **refused**
(tool declined — unbalanced, no SMARTS, timeout) / **silent** (tool returned a
verdict it had no basis for). The **silent** cells are the deliverable.

---

## 6. Pre-registered predictions

Written before the run so the demo is a test rather than a narrative.

1. **MU1700 and its analogue solve under S-cat**, few steps, and the ladder
   returns green at every rung it reaches. Good — controls should be easy.
2. **The two MU1700 routes will be compared to each other.** Němec says
   "possibly also similar route". Score route overlap (Retro-BLEU is vendored).
   Divergence on a one-substituent change is a legible failure and costs nothing
   to explain.
3. **Pleuromutilin and both bilobalides do not produce a chemically sound route
   under any stock.** Either unsolved, or solved through the Draslovka failure
   mode — connectivity plausible, chemistry wrong, errors compounding with depth.
4. **The stereo rung will pass routes it should not.** rdchiral checks whether a
   given template reproduces a given product; it does not ask whether the
   *strategy* is stereochemically viable, and it cannot rule on the two
   unassigned centres in the bilobalides. Predicted signature: `RDChiral
   accepted == RDKit accepted` on stereo-dense targets, which is the same
   uninformative equality visible in the aspirin report on an achiral molecule.
5. **Rung 6 refuses on most steps** for atom balance, per the 6/250 and 10/11
   measurements. Expect barriers on 0–3 steps across all five targets.
6. **The route/step ranks that matter are low.** Our fitted marginal is
   p ≈ 0.533/r^2.152 (AZF) against Tripp's assumed 0.75/r^0.100 — by rank 10 the
   assumption is ~160–200× optimistic. If the NP routes are assembled from rank-5+
   proposals, that is the quantitative reason they will be wrong.

---

## 7. Deliverable

One `report_<target>.md` per molecule — the CLOVER format, extended with the
per-step ladder table from Phase D — plus a single `BLIND-SPOTS.md` holding the
Phase E grid and the ranked findings.

Then, and only then, the chemist conversation: hand Němec the routes with our own
verdicts attached and ask where **we** are wrong. That is worth more than asking
him to label steps cold, and it is the same instrument the error-structure paper
needs (`docs/sota/retrosynthesis-error-structure.md`: our marginal is a lower
bound and "the quantity that separates them is exactly what a synthetic chemist
can supply").

---

## 8. Two things to fix, and everything else to merely observe

Fix, because they corrupt the measurement itself:
- **The phantom DFT line** — either wire rung 6 or delete the claim. Right now the
  report format can assert a physics verdict with no physics behind it.
- **`UNAVAILABLE` as a distinct rdchiral state** — accept-on-missing and
  reject-on-crash currently look identical to accept and reject.

Observe and record, do not fix during the demo: unsound deep routes, stock
representation gaps, rung-6 refusals. Those *are* the blind-spot map. Fixing them
mid-run destroys the thing we are trying to measure.

**Open question for the owner:** `retro-fallback-harness` on RCI and the local
`retrosyntesis/` checkout have diverged (local submodules `RetroCrosstalk`,
`syntheseus`, `FlowER` are empty; the on-disk reports predate the current
reporter). Both owners are leaving. Worth deciding whether the demo runs against
RCI as-is — my recommendation, it is what works — or whether this is the moment to
consolidate.
