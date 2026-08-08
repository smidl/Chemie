# Adopting an established protocol instead of inventing one

**Date:** 2026-08-08 · **Installed on RCI:** `autode` 1.4.5 (from source; not on PyPI),
xtb at `/mnt/data/resynthesis/xtb_dl/xtb-dist/bin/xtb`, both live in the admissibility venv

## Two published protocols, for two different jobs

**BH9's curation protocol** — read out of its computational-details SI while checking the reference
geometries. Preliminary TS by optimisation + frequency → check for a *single* imaginary frequency
and **visually inspect the eigenvector along the reaction coordinate** → constrained conformer
search (MacroModel) with forming/breaking bonds fixed → 100-step Monte-Carlo multiple-minimum search
(FullMonte) → PM6-DH2 screen → ten lowest reoptimised → final optimisation and frequency at
CAM-B3LYP-D3(BJ)/6-311++G\*\* → reactants and products built **from the optimised TS** and given the
same treatment → DLPNO-CCSD(T) single points.

Note the direction: **TS first, endpoints derived from it.** That is the right way round when you
have the reaction and want the best possible number, cost no object, with a human in the loop. It is
not available to us — finding the TS is the entire problem — and it does not scale to a planner
oracle. It is a *curation* protocol.

**autodE** — Young, Silcock, Sterling & Duarte, *Angew. Chem. Int. Ed.* **60**(8), 4266–4274 (2021),
DOI `10.1002/anie.202011941` (Crossref-verified). SMILES in, reaction profile out, automated:
conformational sampling of **both minima and the TS**, a double-ended TS search (NEB / CI-NEB /
adaptive), and frequency verification of the saddle. Applicable to addition, substitution,
elimination, migratory insertion, oxidative addition, reductive elimination — organic and
organometallic.

That is a *screening* protocol, and it is our regime.

## What this means for what we have been building

autodE already solves, in published and used form, the two gaps we ranked highest in
`open-questions-for-review.md`:

- **B1, TS verification** — it optimises to a saddle and checks the imaginary mode. We take the
  highest image of a 6–8 point band and call it a barrier.
- **B2, conformational sampling** — it samples conformers of reactants, products *and* the TS. We
  generate one geometry from one seed.

So the honest position is that we should not be inventing these. The remaining questions are what
autodE costs at planner scale, where it fails on our reactions, and what it does not cover.

**What it does not cover, and stays ours:**

- **Atom mapping.** autodE takes a reaction SMILES; it does not solve the mapping problem that
  broke 2 of our 6.
- **The refusal vocabulary.** Our `classify_neb_result` statuses exist because a screening oracle
  must distinguish *tool failure* from *chemistry* at scale without a human. autodE is built to be
  supervised.
- **The cost regime.** autodE is designed for tens of reactions at DFT, not for the thousands of
  edges a planner evaluates.

## A constraint found on installing it

autodE drives ORCA, Gaussian, NWChem, QChem, MOPAC and xtb. **It cannot drive PySCF**, which is the
only DFT engine we have. On RCI today it therefore runs **xtb-only**, so any barrier it produces is
a GFN2-xTB number, not a DFT one.

**It is a blocker, and the requirement is structural.** I tried to work around it by promoting xtb
to the high-level tier, on the reasoning that it would separate "we lack a DFT backend" (an install
problem) from "the protocol fails on our chemistry" (a science problem). Three attempts, three
different enforcement points:

1. `Config.hcode = "xtb"` → `MethodUnavailable`; xtb is registered only in
   `low_level_method_names`.
2. appending xtb to `autode.methods.h_methods` → no effect; `h_methods` is a **local list built
   inside `get_hmethod()`**, not a module attribute.
3. replacing `autode.methods.get_hmethod` itself → passes the decorator gate, then fails again in
   `reactions/reaction.py`, which imported `get_hmethod` by name at module load.

Three independent guards is not an oversight. autodE's authors deliberately refuse to emit a
reaction profile without a high-level method, and that is a defensible position — a semi-empirical
"reaction profile" is not something they want their tool to endorse. Continuing to patch around it
would produce numbers the protocol's own designers consider inadmissible, which defeats the entire
point of adopting an established protocol.

**So the ask is concrete: ORCA on RCI.** It is free for academic use, it is autodE's best-supported
backend, and it would additionally give the cost ladder a second DFT engine independent of PySCF —
every DFT number in this tree currently comes from one code. Until then autodE is installed and
importable but cannot run a profile.

## The proposal, which also improves the walkthrough

Rather than asking the reviewer to audit a bespoke pipeline, **run both on the same six reactions
and show them side by side.** The chemist then reads a familiar tool next to ours, and every
divergence is a specific question rather than a general invitation to comment.

Concretely, each walkthrough page gains a column: autodE's barrier, its TS imaginary frequency, its
conformer counts, and its wallclock — against ours at the same level of theory. Where we agree, the
bespoke path is validated. Where we differ, the difference is the finding.

This costs one extra run per reaction and makes the artifact considerably stronger than it was.
