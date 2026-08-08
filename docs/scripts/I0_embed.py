"""Which SMILES->3D generator should the pipeline use, measured rather than argued.

Until now the choice was justified by an argument: Open Babel beat RDKit 37.3 % vs 98.3 % on clash
rate, but only on the WHOLE-MOLECULE path where a dot-SMILES is embedded as one object -- a
situation build_endpoints avoids by embedding each fragment separately. Nobody measured them on the
job we actually do, which is single-fragment embedding.

BH9 makes that partly measurable. Its reactant blocks are isolated fragments optimised at
CAM-B3LYP-D3(BJ)/6-311++G** -- a good DFT reference, NOT a coupled-cluster one: DLPNO-CCSD(T) is a
single point at those geometries. And each is the LOWEST-ENERGY CONFORMER from an extensive search
(MacroModel constrained search, 100-step MCMM, PM6-DH2 screen, top-10 reoptimised). A single ETKDG
or make3D shot does no search at all, so for a flexible fragment this metric scores conformer luck,
not geometry quality. It is a clean bond-length/angle test only for rigid fragments.

Per fragment, three numbers:
  * heavy-atom best-fit RMSD to the BH9 reference geometry (symmetry-aware)  <- the real metric
  * MMFF94 single-point energy of the produced geometry, scored by RDKit for both so the comparison
    is on one force field rather than each tool's own
  * wallclock
"""
import json, sys, time
import numpy as np
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem, rdDetermineBonds, rdMolAlign
from openbabel import pybel
RDLogger.DisableLog("rdApp.*")
sys.path.insert(0, "/mnt/data/resynthesis/admissibility/scripts")
from E0_pick import parse_db

SI = "/mnt/data/resynthesis/admissibility/data/BH9_SI"
S1 = json.load(open("/mnt/data/resynthesis/admissibility/out/walkthrough_s1b.json"))
MAPPED = [n for n, r in S1.items() if r.get("h_map_status") == "COMPLETE"]


def ref_mol(block):
    xyz = f"{len(block['atoms'])}\n\n" + "\n".join(
        f"{a[0]} {a[1]:.6f} {a[2]:.6f} {a[3]:.6f}" for a in block["atoms"])
    m = Chem.MolFromXYZBlock(xyz)
    if m is None:
        return None
    try:
        rdDetermineBonds.DetermineBonds(m, charge=int(block["charge"]))
    except Exception:
        return None
    return m


def rdkit_embed(smi):
    t = time.time()
    m = Chem.AddHs(Chem.MolFromSmiles(smi))
    p = AllChem.ETKDGv3(); p.randomSeed = 42
    if AllChem.EmbedMolecule(m, p) == -1:
        p.useRandomCoords = True
        if AllChem.EmbedMolecule(m, p) == -1:
            return None, None
    AllChem.MMFFOptimizeMolecule(m, maxIters=500)
    return m, time.time() - t


def ob_embed(smi):
    t = time.time()
    om = pybel.readstring("smi", smi)
    om.make3D(forcefield="mmff94", steps=250)
    om.localopt(forcefield="mmff94", steps=500)
    xyz = om.write("xyz")
    m = Chem.MolFromXYZBlock(xyz)
    if m is None:
        return None, None
    try:
        rdDetermineBonds.DetermineBonds(m, charge=om.charge)
    except Exception:
        return None, None
    return m, time.time() - t


def mmff_energy(m):
    try:
        mp = AllChem.MMFFGetMoleculeProperties(m)
        ff = AllChem.MMFFGetMoleculeForceField(m, mp)
        return ff.CalcEnergy()
    except Exception:
        return None


print(f"{'rxn':<6}{'fragment':<34}{'RDKit RMSD':>11}{'OB RMSD':>10}"
      f"{'RDKit E':>11}{'OB E':>11}{'RDKit s':>9}{'OB s':>8}   winner")
print("-" * 118)
rows = []
for n in sorted(MAPPED):
    d = parse_db(f"{SI}/DB_files/BH/BH9-BH_{n}_forward.db")
    for blk in [b for b in d["blocks"] if b["coef"] < 0]:
        ref = ref_mol(blk)
        if ref is None:
            continue
        smi = Chem.MolToSmiles(Chem.RemoveHs(ref))
        a, ta = rdkit_embed(smi)
        b, tb = ob_embed(smi)
        out = {"rxn": n, "smiles": smi}
        for tag, m, t in (("rdkit", a, ta), ("ob", b, tb)):
            if m is None:
                out[tag] = None; continue
            try:
                rms = rdMolAlign.GetBestRMS(Chem.RemoveHs(m), Chem.RemoveHs(ref))
            except Exception:
                rms = None
            out[tag] = dict(rmsd=rms, energy=mmff_energy(m), seconds=t)
        ra = out.get("rdkit") or {}
        rb = out.get("ob") or {}
        win = "-"
        if ra.get("rmsd") is not None and rb.get("rmsd") is not None:
            win = "RDKit" if ra["rmsd"] < rb["rmsd"] else "OpenBabel"
        f = lambda v, w, p: (f"{v:>{w}.{p}f}" if isinstance(v, (int, float)) else f"{'--':>{w}}")
        print(f"{n:<6}{smi[:33]:<34}{f(ra.get('rmsd'),11,3)}{f(rb.get('rmsd'),10,3)}"
              f"{f(ra.get('energy'),11,2)}{f(rb.get('energy'),11,2)}"
              f"{f(ra.get('seconds'),9,2)}{f(rb.get('seconds'),8,2)}   {win}")
        rows.append(out)

va = [r["rdkit"]["rmsd"] for r in rows if r.get("rdkit") and r["rdkit"].get("rmsd") is not None]
vb = [r["ob"]["rmsd"] for r in rows if r.get("ob") and r["ob"].get("rmsd") is not None]
print("-" * 118)
print(f"fragments compared: {len(rows)}")
if va and vb:
    print(f"median heavy-atom RMSD to the DFT reference:  RDKit {np.median(va):.3f} A   "
          f"OpenBabel {np.median(vb):.3f} A")
    both = [(r["rdkit"]["rmsd"], r["ob"]["rmsd"]) for r in rows
            if r.get("rdkit") and r.get("ob") and r["rdkit"].get("rmsd") is not None
            and r["ob"].get("rmsd") is not None]
    w = sum(1 for x, y in both if x < y)
    print(f"RDKit closer on {w}/{len(both)} fragments")
json.dump(rows, open("/mnt/data/resynthesis/admissibility/out/embed_compare.json", "w"), indent=1)
print("wrote out/embed_compare.json")
