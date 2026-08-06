"""Does Open Babel's make3D avoid the clash that ETKDG causes -- and is the 10 A shift usable?

validation_energy.py has a SECOND SMILES->3D path, independent of the one the 07-31 handover fixed:

  StructureBuilder.convert_smiles_to_xyz    -> pybel.make3D(mmff94, 100 steps), RDKit ETKDG fallback
  StructureBuilder.convert_multiple_smiles_to_single_xyz -> per-fragment build, then a fixed +10 A
                                                            translation along x per component

Three questions, no quantum chemistry:

  Q1  On a dot-containing single SMILES -- which is what a reaction record actually stores --
      len(smiles_list)==1, so the multi-fragment branch is BYPASSED and the whole thing goes through
      the whole-molecule builder. Does OB clash there the way ETKDG does?
  Q2  When the multi-fragment branch IS taken, the +10 A x-shift guarantees no overlap. But a NEB
      endpoint needs the fragments in CONTACT (~2.5 A between the reacting atoms). How far apart
      does the shift actually leave the closest atoms?
  Q3  Does OB vs RDKit even give the same geometry? The import is wrapped in try/except with a
      silent fallback, so which generator ran is not recorded in any result.
"""
import json, random
from collections import Counter
import numpy as np
from rdkit import Chem, RDLogger
from rdkit.Chem import AllChem

RDLogger.DisableLog("rdApp.*")
USPTO = "/mnt/data/resynthesis/data/data_student/uspto.csv"
CLASH = 0.8
CONTACT_TARGET = 2.5
N = 300

try:
    from openbabel import pybel
    HAVE_OB = True
except ImportError:
    pybel = None
    HAVE_OB = False
print(f"openbabel importable: {HAVE_OB}", flush=True)


def mindist(coords):
    if len(coords) < 2:
        return None
    d = np.linalg.norm(coords[:, None, :] - coords[None, :, :], axis=-1)
    np.fill_diagonal(d, np.inf)
    return float(d.min())


def ob_build(smi):
    """Exactly convert_smiles_to_xyz's OB branch."""
    m = pybel.readstring("smi", smi)
    m.make3D(forcefield="mmff94", steps=100)
    c = np.array([a.coords for a in m.atoms])
    return c


def rdkit_build(smi):
    """Exactly the RDKit fallback branch: AddHs, ETKDGv3, seed 42, useRandomCoords retry."""
    mol = Chem.MolFromSmiles(smi)
    if mol is None:
        return None
    mol = Chem.AddHs(mol)
    p = AllChem.ETKDGv3(); p.randomSeed = 42
    if AllChem.EmbedMolecule(mol, p) == -1:
        p.useRandomCoords = True
        if AllChem.EmbedMolecule(mol, p) == -1:
            return None
    return np.array(mol.GetConformer().GetPositions())


# ---- sample multi-fragment reactant sides, as before
random.seed(20260806)
rows = []
with open(USPTO) as fh:
    fh.readline()
    for i, line in enumerate(fh):
        r = line.split(",")[0]
        if "." in r:
            rows.append(r)
        if len(rows) > 200000:
            break
cand = [r for r in rows if 8 <= Chem.MolFromSmiles(r).GetNumAtoms() <= 40] if False else rows
sample = []
for r in random.sample(cand, min(4000, len(cand))):
    m = Chem.MolFromSmiles(r)
    if m is None:
        continue
    if len(Chem.GetMolFrags(m)) < 2:
        continue
    if not (6 <= m.GetNumAtoms() <= 40):
        continue
    sample.append(r)
    if len(sample) >= N:
        break
print(f"sampled {len(sample)} multi-fragment reactant sides\n", flush=True)

res = {"ob": Counter(), "rd": Counter()}
ob_d, rd_d, agree = [], [], []
for smi in sample:
    rc = rdkit_build(smi)
    if rc is None:
        res["rd"]["failed"] += 1
    else:
        d = mindist(rc); rd_d.append(d)
        res["rd"]["clash" if d < CLASH else "ok"] += 1
    if HAVE_OB:
        try:
            oc = ob_build(smi)
            d2 = mindist(oc); ob_d.append(d2)
            res["ob"]["clash" if d2 < CLASH else "ok"] += 1
            if rc is not None and len(oc) == len(rc):
                agree.append(abs(mindist(oc) - mindist(rc)))
        except Exception:
            res["ob"]["failed"] += 1

print("=" * 72)
print("Q1  dot-SMILES through the WHOLE-MOLECULE builder (the branch actually taken)")
print("=" * 72)
for k, label in (("rd", "RDKit ETKDGv3 (the fallback)"), ("ob", "OpenBabel make3D mmff94")):
    c = res[k]
    tot = sum(c.values())
    if tot == 0:
        print(f"  {label:<32} not run")
        continue
    print(f"  {label:<32} clash {c['clash']:>4}/{tot}  = {100.0*c['clash']/tot:5.1f}%   "
          f"failed {c['failed']}")
if rd_d:
    print(f"\n  RDKit  min-interatomic-distance: median {np.median(rd_d):.3f} A, "
          f"p05 {np.percentile(rd_d,5):.3f}, min {min(rd_d):.3f}")
if ob_d:
    print(f"  OB     min-interatomic-distance: median {np.median(ob_d):.3f} A, "
          f"p05 {np.percentile(ob_d,5):.3f}, min {min(ob_d):.3f}")

print()
print("=" * 72)
print("Q2  the +10 A x-shift, when the multi-fragment branch IS taken")
print("=" * 72)
gaps = []
for smi in sample[:120]:
    frs = smi.split(".")
    built = []
    ok = True
    for f in frs:
        c = rdkit_build(f)
        if c is None:
            ok = False; break
        built.append(c)
    if not ok or len(built) < 2:
        continue
    shifted, shift = [], 0.0
    for c in built:
        s = c.copy(); s[:, 0] += shift; shifted.append(s); shift += 10.0
    best = np.inf
    for i in range(len(shifted)):
        for j in range(i + 1, len(shifted)):
            d = np.linalg.norm(shifted[i][:, None, :] - shifted[j][None, :, :], axis=-1)
            best = min(best, float(d.min()))
    gaps.append(best)
if gaps:
    g = np.array(gaps)
    print(f"  n={len(g)} multi-fragment records")
    print(f"  closest approach between fragments after the shift: median {np.median(g):.2f} A, "
          f"p05 {np.percentile(g,5):.2f}, max {g.max():.2f}")
    print(f"  never overlapping (>{CLASH} A): {100.0*(g>CLASH).mean():.1f}%   <- the shift does work as an anti-clash device")
    print(f"  in reactive contact (<={CONTACT_TARGET} A): {100.0*(g<=CONTACT_TARGET).mean():.1f}%   <- but this is what a NEB endpoint needs")
    print(f"  further than 4 A apart: {100.0*(g>4.0).mean():.1f}%")

json.dump({"rdkit": dict(res["rd"]), "ob": dict(res["ob"]), "have_ob": HAVE_OB,
           "gaps": gaps, "rd_mindist": rd_d, "ob_mindist": ob_d},
          open("/mnt/data/resynthesis/admissibility/out/babel_probe.json", "w"), indent=2)
print("\nwrote out/babel_probe.json")
