# What we want a numerical chemist to look at

**Date:** 2026-08-08 · **Companion to** `walkthrough-protocol.md`

The walkthrough's purpose is to get tools and procedures recommended that we are missing. So the
useful thing to expose is not the parts that work — it is the parts that are unclear, and
especially the parts that *look* like they work. Ranked by how much we think we are missing.

Fixing obvious bugs in set A — wrong parameters, wrong units, wrong API contract — is not "training
on the test set" and stays allowed. The items below are not that. They are places where we do not
know what the right procedure is.

---

## A. The two S1 failures — real, and confirmed not to be our bugs

**A1. Benzyne defeats the atom mapper (#95).** We suspected our own input: bond perception emitted
`c1ccccc#1`, an aromatic ring carrying a triple bond, which no mapper will have seen. So we fed
RXNMapper three representations — as-perceived, the Kekulé cyclohexyne form `C1#CC=CC=C1`, and
`C1=CC=CC#C1`. RDKit canonicalises all three to the same string, and all three return the **same
wrong map at the same confidence, 0.330**: the ring-fusion positions go to the aromatic CH carbons
instead of the strained alkyne carbons that actually form the bonds.

*Question:* is there a mapper that handles strained/unusual valence states, or is the right move to
map from geometry — we have reactant, TS and product coordinates — rather than from the graph?

**A2. Hydrogen mapping in a proton relay (#407).** RXNMapper maps heavy atoms by design. A
water-assisted tautomerisation moves only protons, so it returned water as an unchanged spectator
with confidence **0.968**, and our bond-change check reported 0 formed / 0 broken. Fifteen atoms,
and both the tool and the check are blind.

*Question:* what is standard practice for hydrogen-resolved mapping? Everything downstream —
endpoint construction, the NEB path — needs it, and this is the smallest possible instance.

---

## B. Two things that look like they work, and we think are larger gaps

We rate these **above** section A. They will not appear as failures anywhere in the walkthrough,
which is exactly why they need to be named.

**B1. We never verify that we found a transition state.** We take the highest image of a converged
NEB band and call the energy difference a barrier. We do not optimise it to a saddle point, we do
not compute frequencies to confirm exactly one imaginary mode, and we do not run an IRC to confirm
the saddle connects the endpoints we intended. By ordinary computational practice our "barrier" is
an upper estimate from a discretised band, not a verified barrier — and the discretisation is
coarse: 6–8 images.

*Question:* is CI-NEB → TS optimisation → frequency check → IRC the procedure we should adopt
wholesale, and what does it cost per reaction at our sizes? Is there a defensible cheaper
verification for a screening oracle that runs thousands of steps rather than six?

**B2. One conformer, one orientation, one seed.** `build_endpoints` places fragments at a single
2.5 Å contact geometry. Diels–Alder has endo and exo approaches with genuinely different barriers;
flexible reactants have conformer ensembles; our answer depends on which well the placement
happened to land in. We have no sampling at all, and we predict the complex-referenced barrier will
move by kcal/mol under reseeding — which is testable in the walkthrough and which we intend to
report.

*Question:* CREST, a systematic endo/exo enumeration, or multi-start with a Boltzmann average? What
is the cheapest thing that is not indefensible?

---

## C. Known and unowned, listed so they are not mistaken for oversights

- **Gas phase only.** Several of our real specialty steps carry `solvation_required: true`. BH9
  itself notes its charged reactions are strongly solvent-stabilised, some to negative barriers. We
  have no implicit solvation, which is why every charged reaction was excluded from the walkthrough
  set — and the charged ones are the classes closest to our actual chemistry.
- **ΔE, not ΔG.** No ZPE, thermal or entropic corrections. For a bimolecular step the association
  entropy is worth ~10–15 kcal/mol of ΔG‡ at 298 K / 1 M and is missing from every number we report.
- **Convergence is the exception.** Only 8/24 and 7/24 NEB runs met their force threshold within 50
  cycles on **7–9 atom** molecules. `OK_BUT_UNCONVERGED` exists as a status because it is the normal
  outcome, not a rare one.
- **Level mixing.** Endpoint geometry and band energy must come from the same surface: 12.5 %
  spurious rejections when mixed, 0 % when matched. Our cost ladder mixes levels by construction.

---

## The honest framing for the reviewer

We are not asking whether our numbers are right. At n = 6, and with the procedure developed on
these same six, they cannot be. We are asking **which of the four stages above has a standard
solution we have simply not adopted**, and which is genuinely open. Our own guess is that B1 has a
textbook answer we should just implement, B2 has a standard tool (CREST) whose cost at scale is the
real question, A2 is genuinely unsolved in the general case, and A1 is a niche failure that may not
be worth solving — but that ordering is exactly what we would like corrected.
