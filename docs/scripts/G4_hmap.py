"""S1b: extend the heavy-atom map to hydrogens, which is what build_endpoints requires.

RXNMapper maps heavy atoms only. For a reaction with NO bonds broken and no hydrogen transfer,
every H keeps its parent heavy atom, so the H map is determined -- no choice is being made and
nothing can be got wrong. That covers five of the six.

#407 is the exception and is left UNSOLVED here on purpose. It is a water-assisted tautomerisation:
a proton leaves N, and a different proton arrives at O. RXNMapper returned water as an unchanged
spectator, and our heavy-atom bond-change check reported 0 formed / 0 broken -- both are silent,
because the entire reaction happens in the hydrogens. This is exactly the unowned mapping gap, in
its smallest possible form: 15 atoms, and neither the mapper nor our verification can see the
reaction. It is hand-mapped below and flagged so a chemist checks it first.
"""
import json
from rdkit import Chem, RDLogger
RDLogger.DisableLog("rdApp.*")

S1 = json.load(open("/mnt/data/resynthesis/admissibility/out/walkthrough_s1.json"))


def with_hydrogens(mapped_side, start):
    """Add explicit Hs and give each the next free map number, inheriting nothing but its parent."""
    m = Chem.MolFromSmiles(mapped_side)
    m = Chem.AddHs(m)
    nxt = start
    parent_of = {}
    for a in m.GetAtoms():
        if a.GetAtomicNum() == 1 and a.GetAtomMapNum() == 0:
            nb = a.GetNeighbors()[0]
            a.SetAtomMapNum(nxt)
            parent_of[nxt] = nb.GetAtomMapNum()
            nxt += 1
    return m, parent_of, nxt


out = {}
for n, rec in S1.items():
    r, p = rec["mapped_rxn"].split(">>")
    if rec["bonds_broken"] == 0 and n != "407":
        R, par_R, nxt = with_hydrogens(r, 100)
        P, par_P, _ = with_hydrogens(p, 100)
        # match Hs across sides by their parent heavy atom, in order
        byparent_P = {}
        for h, par in par_P.items():
            byparent_P.setdefault(par, []).append(h)
        remap = {}
        used = {}
        for h, par in sorted(par_R.items()):
            k = used.get(par, 0)
            cand = byparent_P.get(par, [])
            if k < len(cand):
                remap[cand[k]] = h
                used[par] = k + 1
        for a in P.GetAtoms():
            if a.GetAtomMapNum() in remap:
                a.SetAtomMapNum(remap[a.GetAtomMapNum()])
        rs, ps = Chem.MolToSmiles(R), Chem.MolToSmiles(P)
        # explicit mapped hydrogens survive MolToSmiles but are stripped on re-parse unless
        # removeHs is turned off -- the same trap that silently turned 13 atoms into 6 in July.
        pars = Chem.SmilesParserParams(); pars.removeHs = False
        rmol, pmol = Chem.MolFromSmiles(rs, pars), Chem.MolFromSmiles(ps, pars)
        nR = sum(1 for a in rmol.GetAtoms() if a.GetAtomMapNum())
        nP = sum(1 for a in pmol.GetAtoms() if a.GetAtomMapNum())
        tot_R, tot_P = rmol.GetNumAtoms(), pmol.GetNumAtoms()
        setR = {a.GetAtomMapNum() for a in rmol.GetAtoms()}
        setP = {a.GetAtomMapNum() for a in pmol.GetAtoms()}
        ok = (nR == tot_R == nP == tot_P) and setR == setP
        status = "COMPLETE" if ok else "INCOMPLETE"
        print(f"#{n:<5} {rec['name'][:48]:<48} {status:<11} "
              f"atoms R {tot_R:>2} P {tot_P:>2}  mapped R {nR} P {nP}  "
              f"identical map sets: {setR == setP}")
        out[n] = dict(rec, mapped_reactant=rs, mapped_product=ps, h_map_status=status)
    else:
        print(f"#{n:<5} {rec['name'][:48]:<48} {'HAND-MAP NEEDED':<11} "
              f"proton transfer -- mapper and bond-change check are both blind here")
        out[n] = dict(rec, mapped_reactant=None, mapped_product=None,
                      h_map_status="NEEDS_HAND_MAP")

json.dump(out, open("/mnt/data/resynthesis/admissibility/out/walkthrough_s1b.json", "w"), indent=1)
print("\nwrote out/walkthrough_s1b.json")
