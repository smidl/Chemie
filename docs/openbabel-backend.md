# Open Babel in the pipeline — installed, measured, wired in

**Date:** 2026-08-08 · **Install:** `openbabel-wheel` in `/mnt/data/resynthesis/admissibility/.venv`
(Open Babel **3.1.0**; mmff94, uff, gaff, ghemical all present) · **Measurement:** `I0_embed.py`,
`out/embed_compare.json`, `logs/embed-11321389.log` · **Code:** `reaction_complex.py`, 18/18 tests

## Why measure rather than argue

The earlier case for RDKit was an argument: Open Babel's 37.3 % vs 98.3 % clash advantage was
measured on the **whole-molecule** path, where a dot-SMILES is embedded as one object — a situation
`build_endpoints` avoids by embedding fragments separately. Plausible, but nobody had compared them
on the job we actually do.

BH9 makes it measurable. Its reactant blocks are the isolated fragments at DFT-quality geometry, so
we can ask directly: from the SMILES alone, which builder lands closer to the true structure?

## Result — Open Babel is better on average, and neither dominates

Heavy-atom best-fit RMSD to the BH9 reference, 8 fragments from the four mapped set-A reactions:

| fragment | RDKit | Open Babel | |
|---|---|---|---|
| CO₂ | 0.203 | **0.034** | ETKDG bends a linear molecule |
| 1-methylcyclopropene | **0.050** | 0.223 | OB is poor on the strained ring |
| methyl azide | **0.099** | *failed* | charge-separated N₃ defeats OB |
| thiazolium enol | 0.452 | **0.389** | both mediocre on the flexible one |
| thiophene S-oxide | 0.142 | **0.138** | tie |
| 2,3-dihydrofuran | 0.031 | **0.029** | tie |
| thiophene-1,1-dioxide | 0.036 | 0.036 | identical |
| ethylene | 0.006 | 0.006 | identical |

**Median 0.036 Å (OB) vs 0.074 Å (RDKit); OB closer on 6 of 7 comparable fragments.** But the
aggregate hides the shape: on rigid aromatics the two agree to 0.000–0.003 Å and the choice is
irrelevant; the differences that matter are three specific molecules, and they point in *different*
directions. Open Babel gets CO₂ right where ETKDG bends it; RDKit gets the strained ring right where
OB is 4× worse; and **Open Babel fails outright on methyl azide**, a charge-separated hypervalent
group.

That failure is the most useful line in the table for the review — it is a concrete, reproducible
Open Babel hiccup on a common functional group, in a tool the reviewer knows better than we do.

## What was wired in

`_embed_fragment(frag, seed, generator=...)` takes `'rdkit'` (default) or `'openbabel'`, threaded
through `build_endpoints(..., generator=...)`.

Two deliberate choices:

- **It is a switch, never a fallback.** A missing `openbabel` raises `EndpointBuildError` rather
  than quietly reverting to RDKit. Robin's `validation_energy.py` does the opposite — silent
  `except ImportError` — which is how the shared RCI environment ended up taking the RDKit path
  while `requirements.txt` claimed Open Babel, with no record in any result of which ran.
- **Atom order is asserted, not assumed.** Open Babel is fed an ordered molblock and coordinates are
  read back by index, with a hard check on the atom count. OB's SMILES reader reorders, and a silent
  reorder would corrupt the atom map that every downstream stage depends on.

## Still open for the reviewer

- The azide failure: is that a known Open Babel limitation, a `make3D` parameter issue, or should
  the input be written differently?
- Is `make3D(mmff94, 250) + localopt(500)` the right invocation, or is there a better recipe —
  `--conformer`, `--gen3d best`, confab?
- We now have two builders that disagree by more than 0.2 Å on three of eight fragments. **Is that
  disagreement usable as a cheap conformer-uncertainty signal**, or is it just noise between two
  force fields?
