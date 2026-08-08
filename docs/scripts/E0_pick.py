"""Pick the walkthrough set from BH9.

Constraints, in priority order:
  1. MULTI-FRAGMENT reactant side. This is the failure mode our pipeline actually has, and the
     reason Transition1x (99.9 % single-fragment) could not test it.
  2. Types VIII (nucleophilic substitution) and IX (nucleophilic addition) -- the two classes the
     specialty_11 set is made of. spec01_cyanohydrin is a type IX.
  3. NEUTRAL. The pipeline is gas-phase; BH9 itself warns that its charged species are strongly
     solvent-stabilised, some barriers even negative. Charged cases would confound the audit.
  4. Tractable: a NEB with 8 images at wB97X/6-31G(d) on N atoms costs roughly N^3 per image per
     cycle, and July's 13-atom case took ~6 h at 50 cycles. Cap around 20 atoms.
  5. Span the barrier range, so the walkthrough exercises easy and hard.

Reads the .db files directly rather than the paper's tables: the db has the geometries AND the
reference, so charge/multiplicity/fragment-count come from the same place as the number.
"""
import glob, os, re, json
from collections import Counter, defaultdict

SI = "/mnt/data/resynthesis/admissibility/data/BH9_SI"


def parse_db(path):
    """-> dict(ref, blocks=[(coef, charge, mult, [(sym,x,y,z)...])])"""
    ref, blocks, cur = None, [], None
    for line in open(path):
        s = line.split()
        if not s:
            continue
        if s[0] == "ref":
            ref = float(s[1])
        elif s[0] == "molc":
            cur = dict(coef=float(s[1]), charge=float(s[2]), mult=int(s[3]), atoms=[])
        elif s[0] == "end":
            blocks.append(cur); cur = None
        elif cur is not None and len(s) == 4:
            cur["atoms"].append((s[0], float(s[1]), float(s[2]), float(s[3])))
    return dict(ref=ref, blocks=blocks)


# reaction id -> (type, subtype) from the reference table
meta = {}
for line in open(f"{SI}/Reference.org"):
    p = [c.strip() for c in line.strip().strip("|").split("|")]
    if len(p) >= 7 and p[0].isdigit():
        meta[p[3]] = dict(id=int(p[0]), type=p[1], subtype=p[2],
                          fwd=float(p[4]), rev=float(p[5]), re=float(p[6]))

rows = []
for path in sorted(glob.glob(f"{SI}/DB_files/BH/*_forward.db")):
    n = os.path.basename(path).replace("BH9-BH_", "").replace("_forward.db", "")
    d = parse_db(path)
    ts = [b for b in d["blocks"] if b["coef"] > 0]
    rx = [b for b in d["blocks"] if b["coef"] < 0]
    if not ts or not rx:
        continue
    natoms = sum(len(b["atoms"]) for b in ts)
    charge = sum(b["charge"] for b in rx)
    mult = max(b["mult"] for b in d["blocks"])
    rows.append(dict(num=n, ref=d["ref"], n_frag=len(rx), n_atoms=natoms,
                     charge=charge, mult=mult, path=path))

print(f"forward barrier records parsed: {len(rows)}")
print("fragment count of the reactant side:", dict(Counter(r["n_frag"] for r in rows)))
multi = [r for r in rows if r["n_frag"] >= 2]
print(f"multi-fragment: {len(multi)}/{len(rows)} = {100.0*len(multi)/len(rows):.1f} %"
      "   <- vs 0.1 % in Transition1x")

# attach type via the id ordering in Reference.org (db numbering follows the table id)
by_id = {m["id"]: (k, m) for k, m in meta.items()}
for r in rows:
    try:
        k, m = by_id[int(r["num"])]
        r["system"], r["type"], r["subtype"] = k, m["type"], m["subtype"]
    except (KeyError, ValueError):
        r["system"] = r["type"] = r["subtype"] = "?"

print("\nmulti-fragment records by reaction type:")
for t, c in sorted(Counter(r["type"] for r in multi).items()):
    print(f"  type {t:<5} {c:>4}")

cand = [r for r in multi
        if r["type"] in ("VIII", "IX") and abs(r["charge"]) < 0.5 and r["mult"] == 1
        and 8 <= r["n_atoms"] <= 22]
cand.sort(key=lambda r: r["ref"])
print(f"\n=== NEUTRAL, MULTI-FRAGMENT, types VIII/IX, 8-22 atoms: {len(cand)} candidates ===")
for r in cand:
    print(f"  #{r['num']:<4} {r['system']:<8} {r['type']:<4} {r['subtype'][:30]:<30} "
          f"frags {r['n_frag']}  atoms {r['n_atoms']:>2}  ref {r['ref']:>7.2f} kcal/mol")

# widen if thin
if len(cand) < 6:
    print("\n(too few -- widening to all neutral closed-shell multi-fragment, any type, 8-22 atoms)")
    wide = [r for r in multi if abs(r["charge"]) < 0.5 and r["mult"] == 1 and 8 <= r["n_atoms"] <= 22]
    wide.sort(key=lambda r: r["ref"])
    print(f"  {len(wide)} candidates; type mix {dict(Counter(r['type'] for r in wide))}")
    for r in wide[::max(1, len(wide)//12)]:
        print(f"  #{r['num']:<4} {r['system']:<8} {r['type']:<4} {r['subtype'][:30]:<30} "
              f"frags {r['n_frag']}  atoms {r['n_atoms']:>2}  ref {r['ref']:>7.2f}")

json.dump(rows, open("/mnt/data/resynthesis/admissibility/out/bh9_index.json", "w"), indent=1)
print("\nwrote out/bh9_index.json")
