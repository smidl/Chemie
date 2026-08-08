"""Pick the walkthrough set. Data-driven, not by taste.

Transition1x is the only set here with a TRUE reference barrier: it ships the wB97X/6-31G(d)
reaction path, so max(E) - E_reactant is a reference number, not an estimate. We need a handful
spanning the axes that actually broke things in July -- fragment count, size, and barrier height --
so the walkthrough exercises the failure modes rather than the easy middle.
"""
import h5py, numpy as np, json
from collections import Counter

EV2KCAL = 23.060548  # Transition1x energies are in eV, not Hartree
f = h5py.File('/mnt/data/resynthesis/data/data_student/Transition1x.h5', 'r')
g = f['data']

rows = []
for formula in g:
    for rxn in g[formula]:
        r = g[formula][rxn]
        try:
            e = np.array(r['wB97x_6-31G(d)']['energy']) if 'wB97x_6-31G(d)' in r else None
            if e is None:
                # energies may sit directly under the rxn group
                for k in r:
                    if 'energ' in k.lower():
                        e = np.array(r[k]); break
            if e is None or len(e) < 3:
                continue
            z = np.array(r['atomic_numbers'])
            er = float(np.array(r['reactant']['wB97x_6-31G(d)']['energy'])) if 'reactant' in r and 'wB97x_6-31G(d)' in r['reactant'] else float(e[0])
            ep = float(np.array(r['product']['wB97x_6-31G(d)']['energy'])) if 'product' in r and 'wB97x_6-31G(d)' in r['product'] else float(e[-1])
            barrier = (float(e.max()) - max(er, ep)) * EV2KCAL
            rows.append(dict(formula=formula, rxn=rxn, n_atoms=int(len(z)),
                             n_heavy=int((z > 1).sum()), barrier_kcal=barrier,
                             dE_kcal=(ep - er) * EV2KCAL, n_frames=int(len(e))))
        except Exception:
            continue

print(f"reactions with a usable reference barrier: {len(rows)}")
b = np.array([r['barrier_kcal'] for r in rows])
a = np.array([r['n_atoms'] for r in rows])
print(f"atoms:   min {a.min()}  median {np.median(a):.0f}  max {a.max()}")
print(f"barrier: p05 {np.percentile(b,5):.1f}  median {np.median(b):.1f}  p95 {np.percentile(b,95):.1f}  max {b.max():.1f} kcal/mol")
print(f"formulae: {len(set(r['formula'] for r in rows))}")
print("\nelement coverage:", Counter(''.join(c for c in fo if c.isalpha()) for fo in set(r['formula'] for r in rows)).most_common(6))

json.dump(rows, open('/mnt/data/resynthesis/admissibility/out/t1x_index.json', 'w'))
print("\nwrote out/t1x_index.json")

# candidates: span the barrier range at the LARGEST sizes available, since size is our weak axis
print("\n=== candidates: largest molecules, spanning low/mid/high barrier ===")
big = [r for r in rows if r['n_atoms'] >= a.max() - 1]
big.sort(key=lambda r: r['barrier_kcal'])
for label, r in (("LOW ", big[len(big)//10]), ("MID ", big[len(big)//2]), ("HIGH", big[-len(big)//10])):
    print(f"  {label} {r['formula']:<10} {r['rxn']:<9} atoms {r['n_atoms']:>2}  "
          f"barrier {r['barrier_kcal']:>7.2f}  dE {r['dE_kcal']:>8.2f}  frames {r['n_frames']}")
