> **Superseded 2026-08-18.** The maintained version is published in the knowledge base at
> `briefing/asks/barrier-computation.md`, which carries the n=3 rescore. This copy is kept only as
> the drafting record.

# Are we driving this correctly?

We compute reaction barriers from SMILES, automatically, at planner scale — thousands of candidate
steps, no human in the loop. We are using **autodE 1.4.5** with **ORCA 6.1.1** and **xtb**. Three
things stopped us. We would value ten minutes of your opinion on whether we are calling the tools
the right way.

## Exactly what we run

```python
ade.Config.lcode = "xtb"          # conformers, initial paths
ade.Config.hcode = "orca"
ade.Config.n_cores = 8
rxn = ade.Reaction("C=C.O=S1(=O)C=CC=C1>>O=S1(=O)C2C=CC1CC2", solvent_name=None)
rxn.calculate_reaction_profile()
```

autodE's default ORCA keywords, unmodified:

```
optimisation : ! LooseOpt PBE0 RIJCOSX D3BJ def2-SVP  def2/J
frequency    : ! Freq     PBE0 RIJCOSX D3BJ def2-SVP  def2/J
single point : ! SP       PBE0 RIJCOSX D3BJ def2-TZVP def2/J
```

Every transition state is confirmed by one imaginary mode. Cost is 45–90 min per reaction on 8 cores
at 17–21 atoms.

## What we get

Against BH9 (Prasad et al., *JCTC* 2022), whose references are DLPNO-CCSD(T)/CBS:

| reaction | ours | reference | error |
|---|---|---|---|
| thiophene-1,1-dioxide + ethylene | 11.03 | 16.98 | −5.95 |
| thiophene S-oxide + 2,3-dihydrofuran | 13.66 | 16.64 | −2.98 |
| 1-methylcyclopropene + methyl azide | 12.83 | 15.30 | −2.47 |

Re-scoring the **first** one at DLPNO-CCSD(T)/def2-TZVP, single points on the same geometry, gives
**16.25 — error −0.73**. So the geometry is essentially right and the error is the functional.
17 min for three single points.

**Question 1.** Should we simply always rescore at DLPNO-CCSD(T) rather than trust the PBE0 number —
or is def2-SVP too small for the *geometry*, and we are being lucky?

## Three things that stopped us

**Stereochemistry costs more than the functional.** Running the second reaction with the product
stereochemistry stripped from the SMILES — which is what our planner emits — gives **5.09 instead of
13.66**, an error of −11.55 rather than −2.98. For a Diels–Alder the product stereochemistry *is* the
endo/exo distinction, so the search converges on a different diastereomer.

**Question 2.** When stereochemistry is unspecified, is there a defensible way to score the reaction —
enumerate diastereomers, take the lowest, something else?

**A zwitterion will not stay together in the gas phase.** CO₂ + a thiazolium enol → carboxylate
adduct. On optimisation the product expels CO₂: C–O 1.158–1.162 Å (free CO₂, not carboxylate at
~1.25 Å), nearest C–C 3.02–3.40 Å. autodE discards every conformer and stops. We run without
solvation.

**Question 3.** Is implicit solvation (CPCM/SMD) the right fix here, and does it hold shallow-well
zwitterions reliably enough for automated use?

**Atom mapping fails on two of six reactions.** RXNMapper puts the ring-fusion carbons on the wrong
atoms of benzyne (confidence 0.330; three input representations, same wrong map). And on a
water-assisted tautomerisation it returns water as an unchanged spectator at confidence 0.968 —
the whole reaction is in the hydrogens, which it does not map.

**Question 4.** Is there a mapper that handles strained valence, and what is standard practice for
hydrogen-resolved mapping?

## The one question, if you only answer one

**Given that we must do this automatically and at scale, is autodE with these settings the right
tool — and if not, what would you use instead?**
