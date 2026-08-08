"""Name the candidates. Derive SMILES from the BH9 geometries so a chemist reads structures.

Also: how badly do the VIII/IX (our specialty classes) fail the neutral/small filter, and what does
relaxing the size cap buy?
"""
import json, sys
from collections import Counter
from rdkit import Chem, RDLogger
from rdkit.Chem import rdDetermineBonds
RDLogger.DisableLog("rdApp.*")

sys.path.insert(0, "/mnt/data/resynthesis/admissibility/scripts")
from E0_pick import parse_db  # noqa

rows = json.load(open("/mnt/data/resynthesis/admissibility/out/bh9_index.json"))


def smiles_of(block):
    xyz = f"{len(block['atoms'])}\n\n" + "\n".join(
        f"{a[0]} {a[1]:.6f} {a[2]:.6f} {a[3]:.6f}" for a in block["atoms"])
    m = Chem.MolFromXYZBlock(xyz)
    if m is None:
        return None
    try:
        rdDetermineBonds.DetermineBonds(m, charge=int(block["charge"]))
    except Exception:
        return None
    try:
        return Chem.MolToSmiles(Chem.RemoveHs(m))
    except Exception:
        return None


print("=== types VIII / IX: why they were all filtered out ===")
vx = [r for r in rows if r["type"] in ("VIII", "IX")]
print(f"  {len(vx)} reactions;  charged: {sum(1 for r in vx if abs(r['charge'])>0.5)};  "
      f"multi-fragment: {sum(1 for r in vx if r['n_frag']>=2)}")
sz = sorted(r["n_atoms"] for r in vx)
print(f"  atom counts: min {sz[0]}  median {sz[len(sz)//2]}  max {sz[-1]}")
neutral_multi = [r for r in vx if abs(r["charge"]) < 0.5 and r["n_frag"] >= 2 and r["mult"] == 1]
print(f"  neutral + multi-fragment + closed-shell: {len(neutral_multi)}")
for r in sorted(neutral_multi, key=lambda r: r["n_atoms"])[:8]:
    print(f"    #{r['num']:<4} {r['subtype'][:34]:<34} atoms {r['n_atoms']:>3}  ref {r['ref']:>7.2f}")

print("\n=== the neutral closed-shell multi-fragment pool, up to 30 atoms ===")
pool = [r for r in rows if abs(r["charge"]) < 0.5 and r["n_frag"] >= 2 and r["mult"] == 1
        and 8 <= r["n_atoms"] <= 30]
pool.sort(key=lambda r: (r["type"], r["ref"]))
print(f"  {len(pool)} reactions; types {dict(Counter(r['type'] for r in pool))}\n")
for r in pool:
    d = parse_db(r["path"])
    rx = [b for b in d["blocks"] if b["coef"] < 0]
    sm = [smiles_of(b) for b in rx]
    ok = all(s for s in sm)
    print(f"  #{r['num']:<4} {r['type']:<4} {r['subtype'][:26]:<26} atoms {r['n_atoms']:>2} "
          f"ref {r['ref']:>6.2f}  {' + '.join(s or '??' for s in sm) if ok else 'SMILES FAILED'}")
