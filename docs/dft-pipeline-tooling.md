# The DFT/NEB pipeline — what it is built from, and what is still broken

**Date:** 2026-08-06 · **Probe:** `/mnt/data/resynthesis/admissibility/scripts/C0_babel.py`,
`logs/babel-11315578.log`, `out/babel_probe.json` · **Follows:**
`retrosyntesis/coordination/handover/README.md` (2026-07-31)

## The stack

| stage | tool |
|---|---|
| SMILES → 3D | **RDKit** ETKDGv3 + MMFF94 — and, in one module, **Open Babel** `make3D` (see below) |
| fragment placement | our own numpy rigid-body code (`reaction_complex.py`); Robin's own `+10 Å` x-shift in the other module |
| endpoint relaxation | pysisyphus `RFOptimizer` |
| interpolation | pysisyphus IDPP |
| band | pysisyphus `NEB` + `LBFGS` |
| energies | **PySCF** via `pysisyphus.calculators.PySCF` (wB97X/6-31G(d) production; PBE/3-21g for the validated contract); GFN2-xTB on lower rungs |
| reference set | Transition1x (ships wB97X geometries, atom-mapped — energies in **eV**) |

No MLIP, no ASE. `reaction_complex.py` itself imports only `numpy` and `rdkit` — deliberately, so
the guard runs in microseconds without a quantum-chemistry stack.

## Yes, Open Babel is in there — and it matters more than expected

`src/validation/validation_energy.py:44-49` imports `from openbabel import pybel` inside a
`try/except ImportError` with a **silent fallback to RDKit**. `requirements.txt:358` pins
`openbabel-wheel>=3.1.1`. `StructureBuilder.convert_smiles_to_xyz` uses
`pybel.make3D(forcefield='mmff94', steps=100)` as the **primary** path.

This is a **second SMILES→3D path**, parallel to the one the 07-31 handover fixed, and it was never
measured. Measured now, on 300 real multi-fragment USPTO reactant sides:

| generator | clashes (< 0.8 Å) | median min-interatomic distance |
|---|---|---|
| RDKit ETKDGv3 — *the fallback* | **98.3 %** (295/300) | 0.249 Å |
| Open Babel `make3D` — *the primary* | **37.3 %** (112/300) | 0.968 Å |

Two things follow.

**Open Babel is genuinely better here.** `OBBuilder` separates disconnected fragments; ETKDG has no
intermolecular term at all. 98.3 % reproduces the 98.4 % measured in July, so the harness is sound.

**But 37.3 % is still a broken oracle**, and worse, *which generator runs is environment-dependent
and unrecorded*. In the shared RCI environment `openbabel` is **not importable**, so the code takes
the silent fallback — the 98.3 % path — while `requirements.txt` says otherwise. Robin's own venv
presumably has it (his home is mode 700, so this is not checkable). Two geometry generators
differing 2.6× in clash rate, chosen by an `ImportError`, with nothing in any result recording which
one produced the number. That is a reproducibility hole independent of the chemistry.

## The `+10 Å` shift is not a pre-reaction complex

`convert_multiple_smiles_to_single_xyz` builds each fragment separately and translates each
successive one `+10 Å` along x. Measured on 120 multi-fragment records:

- closest approach after the shift: median **2.99 Å**, max 6.24 Å
- still overlapping (< 0.8 Å): **9.2 %** — the shift is a *fixed* offset, so extended molecules
  still collide
- in reactive contact (≤ 2.5 Å): **40.8 %**
- more than 4 Å apart: **26.7 %**

So it is neither a reliable anti-clash device nor a reaction complex. It is an arbitrary axis with
no relation to which atoms react — the band then has to close a multi-Ångström gap, which is the
regime that produced 146 / 434 / 142.7 kcal/mol in July.

Also note `convert_smiles_to_xyz` dispatches on `len(smiles_list) > 1`, so a **dot-containing single
SMILES** — which is how a reaction record actually stores a reactant side — never reaches the
multi-fragment branch at all. No caller splits on `.` first (checked; `:531` passes `[smiles]`
directly). The placement code that exists is bypassed by the input format it was written for.

## So: is it perfect? No. Four things are open.

1. **The fix is not integrated.** `src/validation/validation_dft_neb.py` on `main` has no reference
   to `reaction_complex`, `build_endpoints` or `classify_neb_result`. It exists only on the
   `18-handover` branch, which is ours. Robin's `17-validation_filter` predates the handover.
2. **Atom mapping is still unowned.** `build_endpoints` requires a map number on every atom and
   refuses to guess; planner output is unmapped. The existing `react_geom.atoms != prod_geom.atoms`
   check compares element *sequences*, so a wrong-but-element-consistent mapping passes silently.
   Three consumers need this and none owns it.
3. **The validated numbers are PBE/3-21g, 30 cycles, unconverged** — 27.57 and 111.03 kcal/mol are
   the reproduction contract, not chemistry.
4. **The second path in `validation_energy.py`** — everything above. The handover fixed one entry
   point; this one is untouched, has its own placement logic, and swaps geometry generator on an
   `ImportError`.

## What would close it

Cheapest first: **pin the generator and fail loudly.** Turn the silent `except ImportError` into a
hard error, or record the generator in the result — the current design cannot tell you which
geometry produced a published barrier.

Then **collapse the two paths.** `build_endpoints` already does fragment-wise embedding, contact
placement at 2.5 Å, and a guard; `validation_energy.py` should call it rather than keep a parallel
implementation. Open Babel is still worth keeping as the *per-fragment* builder — it beats ETKDG on
its own terms — but fragment placement must be the reaction-aware code, not a fixed axis shift.
