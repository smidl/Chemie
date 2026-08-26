# Our angle — measuring the gap that Toniato named

Core: [[sota/smiles-to-barrier-automation]] · local, 2026-08-26

## Verdict first: the framing survives, but only as a MEASUREMENT paper, and it must be rescoped

The proposed thesis was "SMILES→barrier at planner scale is a pipeline of silent failure modes."
The SOTA says: **the failure modes are known and named; none of them is measured.** So we cannot
claim discovery of the gap. We can claim the numbers, and we are the only ones positioned to.

Three findings from the survey, in descending order of consequence for us.

**1. `toniato2023_qc-fillin-retrosynthesis` already occupies our framing — qualitatively, at n = 2.**
IBM RXN + Reiher's SCINE group, Digital Discovery 2023, *the venue we were aiming at*. It runs
retrosynthesis → Chemoton/GFN2-xTB → TURBOMOLE and then lists our gaps as limitations: no tool exists
to estimate precursor stoichiometry; the planner may omit stereochemistry; elementary-step
identification "will have to be developed". **But its scope is two hand-curated reactions with manual
atom mapping, and it reports no rate for anything.** That is the opening: they identified the gap and
listed it as future work; we have measured it on real planner output. A paper that quantifies what a
prior paper named as an open problem is a clean contribution — provided we cite them as the origin of
the framing and do not present it as ours.

**2. Two of our six "failure modes" are established practice we violated, not findings.**
- **NEB endpoint pre-optimisation** is documented tool guidance — ORCA's own manual (we run ORCA
  6.1.1), plus ASH and AMS, which exposes an `OptimizeEnds` switch. Our 2026-07-30 "MECHANISM FOUND"
  result is therefore a *bug report on our own pipeline*, not a discovery. It stays in the record as
  the diagnosis it was; it cannot go in a paper as a finding. Same for the 107 kcal/mol magnitude —
  the number is ours, the mechanism is textbook.
- **Multi-fragment placement** is known ("notoriously sensitive to the initial spatial arrangement")
  and *solved* by reactant/product alignment in YARP and Chemoton; `stuyver2024_ts-tools` uses
  autodE's randomize-and-relax and re-runs it until stereochemistry matches. So `reaction_complex.py`
  reinvented an existing component. Our **98.4 % clash rate on 800 real USPTO reactant sides vs 0 %
  single-fragment** is still ours and still unpublished — but it is a measurement of a known
  phenomenon on planner-relevant data, not a new phenomenon.

**3. The evaluation-critique literature cannot scoop us, because it never enters the physics arm.**
`maziarz2024_syntheseus` owns retrosynthesis-evaluation critique and owns it thoroughly — S1
recall-without-precision anticipates our 18.5 pp exact-match-vs-likelihood result *as an argument*,
and its round-trip critique anticipates our Draslovka artifact case. **But it contains one occurrence
of "barrier" (idiomatic) and zero of DFT / transition state / activation energy.** Its scope is
single-step metrics and search. Our metric findings are quantifications of their arguments — weak
alone, and they should be cited, not re-claimed. The physics arm is genuinely unoccupied.

## What is left that is ours

The contribution is the **input-distribution measurement between the two literatures**:
automated-TS tools report 95–97 % success on curated elementary reactions
(`stuyver2024_ts-tools`, ARC); planners do not emit those; nobody has measured the difference.

| our number | status against the SOTA |
|---|---|
| 2.4 % of real USPTO records atom-balanced (6/250) | unpublished; `phan2024_synrbl` motivates rebalancing but does not report this rate |
| 10/11 planner steps unbalanced → xTB refused | unpublished |
| 92.6 % of real reactant sides multi-fragment; **98.4 %** naive-embedding clash vs **0 %** single-fragment (n=800) | unpublished measurement of a known phenomenon |
| stereochemistry-free input costs **8.57 kcal/mol** | unpublished; Toniato names the gap, never prices it |
| mapper fails at **both** confidence tails (0.330 and 0.968) | ring/azide failures are in `schwaller2021_rxnmapper`; the *confidence-is-not-a-filter* framing needs checking against their SI |
| 81 min of DFT to learn the inputs were ill-posed; 45–90 min/reaction | cost framing partly published (100–1000× slowdown reported); our per-reaction accounting is ours |

**The honest paper is narrower than proposed and still worth writing:** *what a retrosynthesis
planner actually emits, measured against what automated transition-state tools require* — with
Toniato as the framing citation, Stuyver/autodE/ARC as the success-rate baseline the input
distribution breaks, and Maziarz as the precedent for this kind of audit on the ML side.

## What this kills

- **The "inadmissibility" thesis.** Already dead from the 07-30 retraction of the 0/11 result; the
  SOTA independently removes the framing's novelty. Do not revive it.
- **The endpoint-relaxation and multi-fragment "findings"** as headline contributions. Demoted to
  measurements and to a methods appendix.
- **A standalone benchmark-integrity paper.** Maziarz owns it; our 190-target leakage claim was
  retracted on 2026-08-26 by job `11418664` anyway.

## Consequences for the tree

1. **DSVR's value goes up slightly, for a specific reason.** `stuyver2024_ts-tools` re-runs conformer
   generation until stereochemistry matches the *input* SMILES — which presumes the input specifies
   it. Planners do not, and that is exactly the 8.57 kcal/mol hole. Enumerating and ranking
   endpoint microstates is the missing component, and DSVR is a candidate. Still not worth a stream;
   worth the day, as a by-product of the paper.
2. **The authority question is now sharper, not softer.** With the thesis reduced to measurement, a
   chemist referee will ask whether our *measurement protocol* is right — the balance criterion, what
   counts as multi-fragment, whether the clash threshold is defensible. `briefing/asks/barrier-computation.md`
   still has no reply. Chase it.
3. **Prerequisite before drafting:** the three queued PDFs (`toniato2023`, `stuyver2024`,
   `young2021`) are all bot-blocked and must be downloaded by hand. **We cannot write against
   Toniato from a web summary** — their exact scope and claims decide our positioning, and our own
   citation rules forbid it. This is the blocking item.
