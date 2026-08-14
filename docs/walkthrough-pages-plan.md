# What goes on each walkthrough page

**Date:** 2026-08-14 · Supersedes the three-pair structure in `walkthrough-delivery.md`, which was
designed before we knew which reactions would run.

Four pages, not three pairs. The pairing idea survives inside pages 2 and 3; the change is that
#436 now fails too, at a different stage from #95 and #407, which is more informative than the
success/failure contrast originally planned.

---

## Page 1 — One reaction, end to end (#93)

The reference page: what the procedure does, shown once completely, on the cheapest case.
Thiophene-1,1-dioxide + ethylene, 17 atoms, BH9 reference 16.98 kcal/mol.

| stage | what is shown |
|---|---|
| S0 | the reaction drawn; both reactants and the product as structures, with the BH9 id and reference |
| S1 | the atom map drawn *on* the structures; RXNMapper confidence 0.496; the check that passed it — 2 bonds formed, 0 broken, hydrogen map sets identical |
| S2 | each fragment embedded separately; min interatomic distance and heavy-atom RMSD to BH9's own geometry, for **both** RDKit and Open Babel (here: 0.036/0.036 Å and 0.006/0.006 Å — a tie, stated as such) |
| S3 | the pre-reaction complex, with contact distances |
| S4 | endpoint optimisation — level, convergence, energies |
| S4b | separated-fragment reference energy, and the resulting complexation energy |
| S5–S6 | the TS search and the band, as an energy profile |
| S7 | the guard's verdict, and **the frequency check: one imaginary mode at −363.9 cm⁻¹** |
| S8 | barrier 11.03 vs 16.98, error −5.95, wallclock 88 min |
| **closing** | the DLPNO-CCSD(T) rescore: **16.25, error −0.73** — 87 % of the gap is the functional, so the geometry is right |

The closing block is the point of the page. It says the procedure finds essentially the correct
transition state, and that the visible error is a level-of-theory choice.

## Page 2 — The same reaction twice (#93 and #92)

Two Diels–Alders on thiophene-oxide dienes whose references differ by **0.34 kcal/mol**, at 17 and
21 atoms with 2 and 4 stereocentres. Shows consistency and cost scaling with nothing failing.

Headline: **dropping stereochemistry from the input SMILES cost 8.57 kcal/mol.**

| product SMILES supplied | barrier | error | conformers |
|---|---|---|---|
| stereochemistry stripped | 5.09 | −11.55 | 5 |
| BH9's stereochemistry | 13.66 | −2.98 | 2 |

With the reasoning laid out: for a Diels–Alder the product stereochemistry *is* the endo/exo
distinction, so removing it lets the search converge on a different diastereomeric TS. And the
consequence for us: a planner emits stereochemistry-free SMILES, so this error is available to any
barrier oracle downstream of one, silently.

Question for the reviewer: *is there a defensible way to score a reaction whose stereochemistry is
not specified, or must the mapper supply it?*

## Page 3 — Where it stops, and whether it should

Three refusals, at three different stages. This is the page that asks for tools we do not have.

| # | stage | what happened |
|---|---|---|
| 95 | S1 | RXNMapper puts the ring-fusion carbons on the wrong atoms of benzyne; confidence 0.330, the lowest of the six; three different input representations give the same wrong map |
| 407 | S1 | water-assisted tautomerisation — the reaction is entirely in the hydrogens, so the mapper returns water as a spectator at confidence 0.968 and our bond-change check reports 0 formed / 0 broken. **Both are blind** |
| 436 | S4 | the zwitterionic product expels CO₂ on optimisation — C–O 1.158–1.162 Å (free CO₂), nearest C–C 3.02–3.40 Å. Every conformer's connectivity changes, all are pruned, autodE stops |

The three questions: is there a mapper that handles strained valence; what is standard practice for
hydrogen-resolved mapping; and is implicit solvation the right answer for shallow-well zwitterions
or is there a better construction.

And one observation worth putting to a chemist: **#436's refusal is the behaviour we want.** It
declined to report a barrier for a product that does not exist at that level of theory. Our own
pipeline, in July, returned a confident 434 kcal/mol in an analogous situation.

## Page 4 — What we could not test

The honest-limits page, and the one most likely to earn useful recommendations.

- **Conformational sampling is untested.** 93, 92 and 107 found 1, 2 and 1 conformers — they are
  rigid. 436 was the only flexible case and it cannot run gas-phase. So the question of whether one
  orientation is enough remains open, and answering it needs solvation or a different reaction set.
- **Gas phase only**, which is why every charged BH9 reaction was excluded — and those are the
  classes closest to real specialty chemistry.
- **ΔE, not ΔG.** No thermal or entropic corrections; for a bimolecular step the association entropy
  is worth roughly 10–15 kcal/mol of ΔG‡ and is absent from every number here.
- **Five environment traps**, none of them chemistry, each of which cost a job or a wrong number:
  shared working directory (1.45 kcal/mol), TS template cache inside `site-packages`, `n_cores`
  silently 1, ORCA refusing parallel runs invoked via `PATH`, and `module` undefined in a batch shell.

---

## One thing to resolve before writing

**The runs above are autodE's pipeline, not ours.** `build_endpoints` and `classify_neb_result` —
the fragment placement and refusal vocabulary written in July — were never run on set A, because
autodE constructs its own endpoints. Our own tooling therefore appears only at S1 (the atom map) and
S2 (the embedding comparison).

The original plan was to run both side by side so each divergence became a specific question. As it
stands the pages document the established tool, with our contribution being the mapping layer, the
findings and the traps. That is still a worthwhile artifact, but it is not the comparison that was
promised.

Two options: run our pipeline on the same three reactions and add a column, which is affordable now
that the numbers to compare against exist; or state plainly that the walkthrough documents autodE
and that our own path is superseded for this purpose. **The second may be the honest answer** — if
the established tool does the job, the interesting question is no longer how ours compares.
