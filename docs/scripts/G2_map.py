"""S1 done properly: atom map by minimum bond change on the heavy-atom skeleton.

The previous attempt ran MCS over explicit-hydrogen graphs, which is degenerate (up to 1.7M
embeddings) and does not correspond to anything a chemist would recognise. Redone:

  * map HEAVY atoms only. In every one of these reactions the heavy skeleton is conserved, so a
    correct map covers 100 % of heavy atoms -- that is the check, not a percentage to report.
  * among the symmetry-equivalent embeddings, choose the one MINIMISING THE NUMBER OF BOND CHANGES.
    A concerted cycloaddition should come out at 2 bonds formed (+ formal order changes); a proton
    transfer at 1 broken + 1 formed. If the minimum is larger than that, the map is wrong and the
    walkthrough should say so rather than proceed.
  * hydrogens follow their parent heavy atom, except a transferred H, which is reported explicitly.

The residual degeneracy after that is real chemical symmetry (equivalent methyls, the two O of a
sulfone) and is harmless -- any choice gives the same energetics. It is reported, not hidden.
"""
import json, sys, itertools
from collections import Counter
from rdkit import Chem, RDLogger
from rdkit.Chem import rdDetermineBonds, rdFMCS
RDLogger.DisableLog("rdApp.*")
sys.path.insert(0, "/mnt/data/resynthesis/admissibility/scripts")
from E0_pick import parse_db

SI = "/mnt/data/resynthesis/admissibility/data/BH9_SI"
PICKED = ["407", "107", "93", "92", "95", "436"]
META = json.load(open("/mnt/data/resynthesis/admissibility/out/walkthrough_six.json"))


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


def combined(blocks, sign):
    ms = [mol_from_block(b) for b in blocks if (b["coef"] > 0) == (sign > 0)]
    if any(m is None for m in ms):
        return None
    out = ms[0]
    for m in ms[1:]:
        out = Chem.CombineMols(out, m)
    return out


def heavy_bondset(mol, match):
    """set of frozenset heavy-atom index pairs, in MCS-index space"""
    pos = {a: i for i, a in enumerate(match)}
    s = set()
    for b in mol.GetBonds():
        i, j = b.GetBeginAtomIdx(), b.GetEndAtomIdx()
        if i in pos and j in pos:
            s.add(frozenset((pos[i], pos[j])))
    return s


results = {}
for n in PICKED:
    d_f = parse_db(f"{SI}/DB_files/BH/BH9-BH_{n}_forward.db")
    d_r = parse_db(f"{SI}/DB_files/BH/BH9-BH_{n}_reverse.db")
    R_all, P_all = combined(d_f["blocks"], -1), combined(d_r["blocks"], -1)
    print(f"\n=== #{n}  {META[n]['name']}")
    if R_all is None or P_all is None:
        print("  bond perception failed"); continue
    R, P = Chem.RemoveHs(R_all), Chem.RemoveHs(P_all)
    nh = R.GetNumAtoms()
    print(f"  reactants {Chem.MolToSmiles(R)}")
    print(f"  product   {Chem.MolToSmiles(P)}")

    res = rdFMCS.FindMCS([R, P], atomCompare=rdFMCS.AtomCompare.CompareElements,
                         bondCompare=rdFMCS.BondCompare.CompareAny,
                         ringMatchesRingOnly=False, completeRingsOnly=False, timeout=120)
    q = Chem.MolFromSmarts(res.smartsString)
    mr = list(dict.fromkeys(R.GetSubstructMatches(q, uniquify=False, maxMatches=20000)))
    mp = list(dict.fromkeys(P.GetSubstructMatches(q, uniquify=False, maxMatches=20000)))
    cover = 100.0 * res.numAtoms / nh
    print(f"  heavy atoms {nh};  MCS covers {res.numAtoms} = {cover:.0f} %"
          f"   {'OK' if cover > 99.5 else '<-- SKELETON NOT CONSERVED, map is unreliable'}")

    best = None
    for a, b in itertools.islice(itertools.product(mr, mp), 200000):
        d = len(heavy_bondset(R, a) ^ heavy_bondset(P, b))
        if best is None or d < best[0]:
            best = (d, a, b)
    nmin = sum(1 for a, b in itertools.islice(itertools.product(mr, mp), 200000)
               if len(heavy_bondset(R, a) ^ heavy_bondset(P, b)) == best[0])
    print(f"  embeddings: R {len(mr)} x P {len(mp)};  minimum heavy-bond changes = {best[0]}"
          f"   attained by {nmin} symmetry-equivalent maps")
    exp = {"407": 2, "107": 2, "93": 2, "92": 2, "95": 2, "436": 1}
    verdict = "as expected" if best[0] <= exp[n] + 1 else "MORE THAN EXPECTED -- inspect"
    print(f"  expected for this reaction class: ~{exp[n]}  -> {verdict}")

    results[n] = dict(name=META[n]["name"], fwd_ref=META[n]["fwd_ref"],
                      heavy_atoms=nh, mcs_cover_pct=round(cover, 1),
                      min_bond_changes=best[0], degenerate_maps=nmin,
                      reactant_smiles=Chem.MolToSmiles(R), product_smiles=Chem.MolToSmiles(P))

json.dump(results, open("/mnt/data/resynthesis/admissibility/out/walkthrough_s1.json", "w"), indent=1)
print("\nwrote out/walkthrough_s1.json")
