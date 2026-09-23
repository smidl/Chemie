# Němec sample — 5 targets (extracted 2026-09-01)

Source: `Retrosyntéza - vzorek 1.9..xlsx` (single sheet, columns `SMILES` /
`Name` / `Comment`). Extracted verbatim; the `canonical` column is RDKit
`MolToSmiles` output for our own use — **the input SMILES is authoritative**.

All five parse under RDKit. Formulae and masses match the literature values for
the two named natural products, so the connectivity is sound.

## Targets

| # | Name | Comment (verbatim) | Formula | MW | heavy | rings (arom) | stereocentres | SA |
|---|---|---|---|---|---|---|---|---|
| 1 | pleuromutilin | Complex natural product | C22H34O5 | 378.5 | 27 | 3 (0) | 8 (0 unassigned) | 5.47 |
| 2 | MU1700 | Chemical probe that I developed during my PhD so I know the chemistry, synthesis not too difficult | C26H22N4O | 406.5 | 31 | 6 (5) | 0 | 2.57 |
| 3 | bilobalide | Complex natural product | C15H18O8 | 326.3 | 23 | 4 (0) | 6 (**2 unassigned**) | 5.74 |
| 4 | bilobalide-analogue1 | Close analogue of bilobalide - cyclopropyl group | C15H16O8 | 324.3 | 23 | 5 (0) | 6 (**2 unassigned**) | 5.88 |
| 5 | MU1700-analogue1 | Unpublished analogue with very similar structure and possibly also similar route | C28H27N5O | 449.6 | 34 | 6 (5) | 0 | 2.71 |

SA = RDKit `sascorer` synthetic-accessibility score (1 easy → 10 hard). It is the
same hand-crafted heuristic that retro-fallback uses as its cost-to-go `h`, so
it is listed as *what the current planner will believe*, not as ground truth.

## SMILES, as given

```
pleuromutilin
C[C@@H]1CC[C@@]23CCC(=O)[C@H]2[C@@]1([C@@H](C[C@@]([C@H]([C@@H]3C)O)(C)C=C)OC(=O)CO)C

MU1700
N1(C2=CC=C(C3=CC(OC=C4C5=C(C=CC=C6)C6=NC=C5)=C4N=C3)C=C2)CCNCC1

bilobalide
CC(C)(C)[C@]1(O)CC2OC(=O)C[C@@]23C(=O)OC4OC(=O)[C@H](O)[C@]134

bilobalide-analogue1
CC1([C@@]2(CC3OC(C[C@@]34C(OC5OC([C@@H]([C@]245)O)=O)=O)=O)O)CC1

MU1700-analogue1
CC(C)N(CC1)CCN1C2=CC=C(C=C2)C3=CC4=C(N=C3)C(C5=C6C=CC=CC6=NN=C5)=CO4
```

RDKit-canonical forms (for joining against run outputs):

```
pleuromutilin          C=C[C@]1(C)C[C@@H](OC(=O)CO)[C@]2(C)[C@H](C)CC[C@]3(CCC(=O)[C@H]32)[C@@H](C)[C@@H]1O
MU1700                 c1ccc2c(-c3coc4cc(-c5ccc(N6CCNCC6)cc5)cnc34)ccnc2c1
bilobalide             CC(C)(C)[C@]1(O)CC2OC(=O)C[C@@]23C(=O)OC2OC(=O)[C@H](O)[C@]213
bilobalide-analogue1   CC1([C@]2(O)CC3OC(=O)C[C@@]34C(=O)OC3OC(=O)[C@H](O)[C@]324)CC1
MU1700-analogue1       CC(C)N1CCN(c2ccc(-c3cnc4c(-c5cnnc6ccccc56)coc4c3)cc2)CC1
```

Demo plan that consumes this file: [DEMO-PLAN.md](DEMO-PLAN.md).

## The sample's structure — it is not five independent molecules

It is **two matched pairs and one singleton**, and the design is the point:

- **(3, 4) bilobalide → cyclopropyl analogue** — close analogue, chemist expects
  related chemistry.
- **(2, 5) MU1700 → unpublished analogue** — chemist states explicitly
  "possibly also similar route".
- **(1) pleuromutilin** — unpaired hard natural product.

Two properties make this worth more than its n:

0. **It is a contrast on assigned stereocentres — the one difficulty axis this
   tree has measured.** Three stereo-dense targets (8 / 4 / 4 assigned centres)
   against two achiral controls. Our measured single-step recall@20 falls from
   92.4 % (0 centres, n=4102) to 85.2 % (4+, n=108) on "either model", and from
   71.4 % to 62.0 % on "both" (`admissibility/out/stereo.json`). See DEMO-PLAN §2.
1. **MU1700 carries a chemist-held ground-truth route.** "I developed it during
   my PhD so I know the chemistry" is the label we do not otherwise have
   anywhere in this tree (`coordination/synthesis.md`, oracle inventory:
   *chemist labels — none*).
2. **MU1700-analogue1 is unpublished**, therefore genuinely absent from USPTO /
   ORD / any training corpus. That is a real held-out target, unlike the
   190-hard "far" stratum, where 28/28 supposedly deep-OOD targets turned out to
   be verbatim USPTO products (`docs/ood-strata-invalid.md`).

## Data-quality items to send back

- **bilobalide and bilobalide-analogue1 each carry 2 unassigned stereocentres**
  in the SMILES as given (the C2/C4 acetal-lactone ring positions). Bilobalide's
  absolute configuration is known; the analogue's intended configuration is not
  recoverable from the string. Stereo-underspecified targets change what a
  planner is being asked to make. Worth one email before any run.
- No conditions, scale, or "must avoid" constraints supplied. If Němec has a
  preferred starting-material set (in-house shelf vs commercial catalogue), that
  changes the inventory and therefore every solve/no-solve result.
