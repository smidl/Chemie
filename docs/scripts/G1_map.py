"""S0 + S1 of the walkthrough: structures, and an atom map that can be checked.

Atom mapping is the unowned gap in this pipeline, so the walkthrough must not paper over it. BH9
gives geometries for reactant, TS and product but with INCONSISTENT atom ordering (verified: all six
differ on the reactant side), so the map has to be constructed.

Method, chosen to be auditable rather than clever:
  * perceive bonds on each BH9 geometry (RDKit DetermineBonds) -> reactant fragments and product
  * maximum common substructure between combined reactants and product, element- and ring-aware
  * extend to hydrogens through the heavy atom each is bonded to
  * report, per reaction: how many atoms mapped, which did not, and whether the map is unique or
    only unique up to a SYMMETRY that genuinely does not matter (equivalent methyls, the two O of
    a sulfone). A symmetry-degenerate map is correct chemistry, not a defect -- but it must be said.
"""
import json, sys
from collections import Counter
from rdkit import Chem, RDLogger
from rdkit.Chem import rdDetermineBonds, rdFMCS
RDLogger.DisableLog("rdApp.*")
sys.path.insert(0, "/mnt/data/resynthesis/admissibility/scripts")
from E0_pick import parse_db

SI = "/mnt/data/resynthesis/admissibility/data/BH9_SI"
PICKED = ["407", "107", "93", "92", "95", "436"]
NAMES = json.load(open("/mnt/data/resynthesis/admissibility/out/walkthrough_six.json"))


def mol_from_block(b):
    xyz = f"{len(b['atoms'])}\n\n" + "\n".join(
        f"{a[0]} {a[1]:.6f} {a[2]:.6f} {a[3]:.6f}" for a in b["atoms"])
    m = Chem.MolFromXYZBlock(xyz)
    if m is None:
        return None
    try:
        rdDetermineBonds.DetermineBonds(m, charge=int(b["charge"]))
    except Exception:
        return None
    return m


def side(dbl, sign):
    return [b for b in dbl if (b["coef"] > 0) == (sign > 0)]


out = {}
for n in PICKED:
    d_f = parse_db(f"{SI}/DB_files/BH/BH9-BH_{n}_forward.db")
    d_r = parse_db(f"{SI}/DB_files/BH/BH9-BH_{n}_reverse.db")
    rmols = [mol_from_block(b) for b in side(d_f["blocks"], -1)]
    pmols = [mol_from_block(b) for b in side(d_r["blocks"], -1)]
    print(f"\n=== #{n}  {NAMES[n]['name']}")
    if any(m is None for m in rmols + pmols):
        print("  bond perception FAILED on one side -- cannot map"); continue

    R = rmols[0]
    for m in rmols[1:]:
        R = Chem.CombineMols(R, m)
    P = pmols[0]
    for m in pmols[1:]:
        P = Chem.CombineMols(P, m)
    print(f"  reactants {Chem.MolToSmiles(Chem.RemoveHs(R))}")
    print(f"  product   {Chem.MolToSmiles(Chem.RemoveHs(P))}")
    print(f"  atoms R {R.GetNumAtoms()}  P {P.GetNumAtoms()}   "
          f"formula match: {Counter(a.GetSymbol() for a in R.GetAtoms()) == Counter(a.GetSymbol() for a in P.GetAtoms())}")

    res = rdFMCS.FindMCS([R, P], atomCompare=rdFMCS.AtomCompare.CompareElements,
                         bondCompare=rdFMCS.BondCompare.CompareAny,
                         ringMatchesRingOnly=False, completeRingsOnly=False,
                         matchValences=False, timeout=60)
    q = Chem.MolFromSmarts(res.smartsString)
    mr = R.GetSubstructMatches(q, uniquify=False, maxMatches=5000)
    mp = P.GetSubstructMatches(q, uniquify=False, maxMatches=5000)
    heavy_R = sum(1 for a in R.GetAtoms() if a.GetAtomicNum() > 1)
    print(f"  MCS: {res.numAtoms} atoms, {res.numBonds} bonds   "
          f"covers {100.0*res.numAtoms/R.GetNumAtoms():.0f} % of all atoms "
          f"({100.0*res.numAtoms/max(heavy_R,1):.0f} % of heavy)")
    print(f"  distinct MCS embeddings: reactants {len(set(mr))}  product {len(set(mp))}"
          f"   -> map unique up to {len(set(mr))*len(set(mp))} symmetry-equivalent choices")
    unmapped_R = R.GetNumAtoms() - res.numAtoms
    if unmapped_R:
        idx = set(range(R.GetNumAtoms())) - set(mr[0]) if mr else set()
        syms = Counter(R.GetAtomWithIdx(i).GetSymbol() for i in idx)
        print(f"  UNMAPPED on the reactant side: {unmapped_R}  {dict(syms)}"
              f"   <- these are the atoms whose identity the map cannot fix")
    out[n] = dict(name=NAMES[n]["name"], mcs_atoms=res.numAtoms, total_atoms=R.GetNumAtoms(),
                  embeddings_R=len(set(mr)), embeddings_P=len(set(mp)),
                  reactant_smiles=Chem.MolToSmiles(Chem.RemoveHs(R)),
                  product_smiles=Chem.MolToSmiles(Chem.RemoveHs(P)),
                  fwd_ref=NAMES[n]["fwd_ref"])

json.dump(out, open("/mnt/data/resynthesis/admissibility/out/walkthrough_s1.json", "w"), indent=1)
print("\nwrote out/walkthrough_s1.json")
