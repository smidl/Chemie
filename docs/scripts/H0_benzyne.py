"""Is #95's bad map RXNMapper's limitation, or our malformed input?

Bond perception on the benzyne geometry emitted `c1ccccc#1` -- an aromatic ring carrying a triple
bond, which is not a representation any mapper will have seen in training. Before calling this a
hard problem, try the standard Kekule forms.
"""
from rdkit import Chem, RDLogger
from rxnmapper import RXNMapper
RDLogger.DisableLog("rdApp.*")

PROD = "C[C@]12N=N[C@](C)(N=N1)c1ccccc12"
TETRA = "Cc1nnc(C)nn1"
BENZYNE = {
    "as perceived (aromatic + triple)": "c1ccccc#1",
    "Kekule cyclohexyne form":          "C1#CC=CC=C1",
    "cumulene/strained-alkyne form":    "C1=CC=CC#C1",
}

rm = RXNMapper()
for label, bz in BENZYNE.items():
    m = Chem.MolFromSmiles(bz)
    if m is None:
        print(f"\n{label:<34} -> UNPARSEABLE"); continue
    rsmi = f"{TETRA}.{Chem.MolToSmiles(m)}>>{PROD}"
    try:
        res = rm.get_attention_guided_atom_maps([rsmi])[0]
    except Exception as e:
        print(f"\n{label:<34} -> mapper failed: {e}"); continue
    mapped = res["mapped_rxn"]
    R, P = [Chem.MolFromSmiles(x) for x in mapped.split(">>")]

    def bonds(mm):
        return {frozenset((b.GetBeginAtom().GetAtomMapNum(), b.GetEndAtom().GetAtomMapNum()))
                for b in mm.GetBonds()
                if b.GetBeginAtom().GetAtomMapNum() and b.GetEndAtom().GetAtomMapNum()}

    formed = bonds(P) - bonds(R)
    # the chemical test: the two carbons that form the new bonds must be the ones that carried
    # the strained triple bond, i.e. must have NO hydrogen in the reactant
    newC = set()
    for fb in formed:
        newC |= set(fb)
    rmap = {a.GetAtomMapNum(): a for a in R.GetAtoms()}
    hs = {n: rmap[n].GetTotalNumHs() for n in sorted(newC) if n in rmap}
    print(f"\n{label:<34} confidence {res['confidence']:.3f}")
    print(f"  formed {len(formed)}  broken {len(bonds(R)-bonds(P))}")
    print(f"  H count on the atoms that form new bonds: {hs}")
    print(f"  -> {'CORRECT: bond-forming carbons are the H-free alkyne carbons' if all(v==0 for v in hs.values()) else 'WRONG: a bond-forming carbon still carries H'}")
    print(f"  {mapped}")
