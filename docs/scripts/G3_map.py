"""S1, third attempt: RXNMapper for the map, an independent chemical criterion for the check.

Why not MCS: FindMCS returns a CONNECTED common substructure, which cannot express two molecules
fusing into one ring system. It covered 50-88 % of the heavy skeleton and reported "0 bond changes",
which is the tell -- a reaction with no bond changes is not a reaction.

So: RXNMapper produces the map, and it is then checked against something it did not optimise --
the number of heavy-atom bond changes the map implies. For these classes the answer is known a
priori:
    concerted [4+2] / [3+2] cycloaddition : 2 sigma bonds FORMED, 0 broken
    nucleophilic addition                 : 1 formed, 0 broken
    water-assisted tautomerisation        : 1 broken + 1 formed (a proton relay is 2 + 2)
If the map implies more than that, it is wrong and the walkthrough must say so rather than proceed.
"""
import json, sys
from rdkit import Chem, RDLogger
from rxnmapper import RXNMapper
RDLogger.DisableLog("rdApp.*")

S1 = json.load(open("/mnt/data/resynthesis/admissibility/out/walkthrough_s1.json"))
EXPECT = {"407": "1 broken + 1 formed (relay: up to 2+2)",
          "107": "2 formed", "93": "2 formed", "92": "2 formed",
          "95": "2 formed", "436": "1 formed"}

rxn_mapper = RXNMapper()
out = {}
for n, rec in S1.items():
    rsmi = f"{rec['reactant_smiles']}>>{rec['product_smiles']}"
    res = rxn_mapper.get_attention_guided_atom_maps([rsmi])[0]
    mapped = res["mapped_rxn"]
    conf = res.get("confidence")
    r, p = mapped.split(">>")
    R, P = Chem.MolFromSmiles(r), Chem.MolFromSmiles(p)

    def bonds(m):
        s = set()
        for b in m.GetBonds():
            i = b.GetBeginAtom().GetAtomMapNum()
            j = b.GetEndAtom().GetAtomMapNum()
            if i and j:
                s.add(frozenset((i, j)))
        return s

    br, bp = bonds(R), bonds(P)
    formed, broken = bp - br, br - bp
    nmap_r = sum(1 for a in R.GetAtoms() if a.GetAtomMapNum())
    nmap_p = sum(1 for a in P.GetAtoms() if a.GetAtomMapNum())
    print(f"\n=== #{n}  {rec['name']}")
    print(f"  {rsmi}")
    print(f"  confidence {conf:.3f}" if conf is not None else "  confidence n/a")
    print(f"  heavy atoms mapped: R {nmap_r}/{R.GetNumAtoms()}  P {nmap_p}/{P.GetNumAtoms()}"
          f"   {'OK' if nmap_r == R.GetNumAtoms() == nmap_p else '<-- INCOMPLETE'}")
    print(f"  bonds formed {len(formed)}  broken {len(broken)}   expected: {EXPECT[n]}")
    print(f"  mapped: {mapped}")
    out[n] = dict(rec, mapped_rxn=mapped, confidence=conf,
                  bonds_formed=len(formed), bonds_broken=len(broken),
                  fully_mapped=bool(nmap_r == R.GetNumAtoms() == nmap_p))

json.dump(out, open("/mnt/data/resynthesis/admissibility/out/walkthrough_s1.json", "w"), indent=1)
print("\nwrote out/walkthrough_s1.json")
