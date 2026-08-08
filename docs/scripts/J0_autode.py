"""Run an ESTABLISHED protocol on one of our walkthrough reactions, end to end.

autodE (Young, Silcock, Sterling & Duarte, Angew. Chem. Int. Ed. 60, 4266-4274, 2021;
DOI 10.1002/anie.202011941) does exactly what we have been assembling by hand: SMILES in, reaction
profile out, with conformational sampling of BOTH minima and the TS, a double-ended TS search
(NEB / CI-NEB / adaptive), and frequency verification of the saddle.

That is our gap B1 (we never verify a TS) and gap B2 (we sample nothing) already solved, published,
and used by the field. The question is not whether to adopt it -- it is what it costs, where it
fails on our reactions, and what it cannot do that we need.

Test case #93: thiophene-1,1-dioxide + ethylene, Diels-Alder, 17 atoms.
BH9 reference forward barrier: 16.98 kcal/mol (DLPNO-CCSD(T)/CBS at CAM-B3LYP-D3(BJ)/6-311++G**).
We run entirely at GFN2-xTB, so a large error is EXPECTED -- the point is whether the protocol
completes and what it reports, not accuracy.
"""
import os, time, traceback
import autode as ade

ade.Config.n_cores = int(os.environ.get("SLURM_CPUS_PER_TASK", 8))
ade.Config.max_core = 4000
# we have no DFT code autodE can drive (no ORCA/Gaussian/NWChem/QChem), so xtb does both tiers
ade.Config.lcode = "xtb"
ade.Config.hcode = "xtb"

print(f"autodE {ade.__version__}  cores {ade.Config.n_cores}")
print(f"lcode {ade.Config.lcode}  hcode {ade.Config.hcode}", flush=True)

RXN = "C=C.O=S1(=O)C=CC=C1>>O=S1(=O)C2C=CC1CC2"
REF = 16.98

os.makedirs("/mnt/data/resynthesis/admissibility/work_autode", exist_ok=True)
os.chdir("/mnt/data/resynthesis/admissibility/work_autode")

t0 = time.time()
try:
    rxn = ade.Reaction(RXN, name="bh9_93_da", solvent_name=None)
    rxn.calculate_reaction_profile(free_energy=False, enthalpy=False)
    dt = time.time() - t0
    print(f"\ncompleted in {dt/60:.1f} min", flush=True)
    try:
        dE_ddagger = rxn.delta("E‡").to("kcal mol-1")
        dE = rxn.delta("E").to("kcal mol-1")
        print(f"  barrier   {float(dE_ddagger):8.2f} kcal/mol   (BH9 reference {REF})")
        print(f"  reaction  {float(dE):8.2f} kcal/mol")
    except Exception as e:
        print("  could not read deltas:", e)
    ts = rxn.ts
    if ts is not None:
        print(f"  TS found: {ts.name}")
        try:
            print(f"  imaginary frequencies: {[float(f) for f in ts.imaginary_frequencies]}")
            print("  -> a single imaginary mode is what verifies this is a saddle, "
                  "which our own pipeline never checks")
        except Exception as e:
            print("  frequency read failed:", e)
    else:
        print("  NO TS FOUND")
    print(f"\n  conformers -- reactants: "
          f"{[len(m.conformers or []) for m in rxn.reacs]}  products: "
          f"{[len(m.conformers or []) for m in rxn.prods]}")
except Exception:
    print(f"\nFAILED after {(time.time()-t0)/60:.1f} min")
    traceback.print_exc()
