"""How much does the missing association entropy actually matter here?

The omitted term is ~10-15 kcal/mol of dG_dagger for a BIMOLECULAR step and ~0 for a unimolecular
one. So it is a near-constant offset IF the steps we score are almost all of one molecularity, and
a rank-inverting bias if they are mixed. Barriers are used here for RANKING (mechanism kernel,
rho 0.585), so a constant offset is harmless and a class-dependent one is not.

Counts molecularity of the FORWARD reaction, i.e. fragments on the reactant side of a retro step.
"""
import json
from collections import Counter
from rdkit import Chem, RDLogger
RDLogger.DisableLog("rdApp.*")

USPTO = "/mnt/data/resynthesis/data/data_student/uspto.csv"

c = Counter()
n = 0
with open(USPTO) as fh:
    fh.readline()
    for line in fh:
        r = line.split(",")[0]
        if not r:
            continue
        n += 1
        c[min(r.count(".") + 1, 4)] += 1
print(f"USPTO reactant sides: {n:,}")
print("forward molecularity (4 = 4 or more):")
for k in sorted(c):
    print(f"  {k}: {c[k]:>9,}  {100.0*c[k]/n:5.1f} %")
uni = c[1]
print(f"\nunimolecular: {100.0*uni/n:.1f} %   bimolecular+: {100.0*(n-uni)/n:.1f} %")

# the sets barriers are actually scored on
try:
    d = json.load(open("/mnt/data/resynthesis/draslovka/data/specialty_barriers_v1.json"))
    cc = Counter(len(r["reactants"]) for r in d["reactions"])
    print(f"\nspecialty_11 molecularity: {dict(cc)}")
except Exception as e:
    print("specialty_11:", e)

# zhong reactivity set, if it is what the mechanism-kernel ranking was measured on
import glob
for p in glob.glob("/mnt/data/resynthesis/zhong-reactivity/**/*.json", recursive=True)[:3]:
    print(" zhong file:", p)
