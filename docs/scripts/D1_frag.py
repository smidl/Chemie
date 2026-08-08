"""Can Transition1x test the thing that actually broke?

The July failure was multi-fragment endpoint construction. T1x scored 450/450. Before building a
walkthrough on T1x as the ground truth, check whether its reactant geometries are ever
multi-fragment at all -- if they are always one connected supersystem, then T1x is structurally
incapable of exercising the failure, and a clean T1x score says nothing about specialty chemistry.

Connectivity by covalent-radius overlap on the REACTANT frame, as a chemist would judge it.
"""
import h5py, numpy as np, json
from collections import Counter

RCOV = {1: 0.31, 6: 0.76, 7: 0.71, 8: 0.66}   # Angstrom, Cordero
TOL = 1.3

f = h5py.File('/mnt/data/resynthesis/data/data_student/Transition1x.h5', 'r')
g = f['data']


def n_fragments(z, xyz):
    n = len(z)
    adj = [[] for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = np.linalg.norm(xyz[i] - xyz[j])
            if d < TOL * (RCOV.get(int(z[i]), 0.7) + RCOV.get(int(z[j]), 0.7)):
                adj[i].append(j); adj[j].append(i)
    seen, comps = set(), 0
    for s in range(n):
        if s in seen:
            continue
        comps += 1
        stack = [s]
        while stack:
            v = stack.pop()
            if v in seen:
                continue
            seen.add(v)
            stack.extend(adj[v])
    return comps


counts, gaps = Counter(), []
checked = 0
for formula in g:
    for rxn in g[formula]:
        r = g[formula][rxn]
        try:
            z = np.array(r['atomic_numbers'])
            xyz = np.array(r['reactant']['positions']) if 'reactant' in r and 'positions' in r['reactant'] \
                else np.array(r['positions'])[0]
            if xyz.ndim == 3:
                xyz = xyz[0]
            nf = n_fragments(z, xyz)
            counts[nf] += 1
            checked += 1
        except Exception:
            continue
print(f"reactant frames checked: {checked}")
print("fragment count of the REACTANT geometry:")
for k in sorted(counts):
    print(f"  {k} fragment(s): {counts[k]:>6}  ({100.0*counts[k]/checked:5.1f} %)")
multi = sum(v for k, v in counts.items() if k > 1)
print(f"\nmulti-fragment: {multi}/{checked} = {100.0*multi/checked:.1f} %")
print("For comparison, real USPTO reactant sides are multi-fragment in 92.6 % of records.")
json.dump({str(k): v for k, v in counts.items()},
          open('/mnt/data/resynthesis/admissibility/out/t1x_fragments.json', 'w'), indent=2)
