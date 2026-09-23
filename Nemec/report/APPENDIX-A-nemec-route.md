# Appendix A — Němec's published route

Source: Němec, Remeš, Beňovský, Böck, Šranková, Wong, Cros, Williams, Tse, Smil,
Ensan, Isaac, Al-Awar, Gomolková *et al.*, "Discovery of Two Highly Selective
Structurally Orthogonal Chemical Probes for Activin Receptor-like Kinases 1 and
2", *J. Med. Chem.* **2024**, 67 (15), 12632–12659,
doi:[10.1021/acs.jmedchem.4c00629](https://doi.org/10.1021/acs.jmedchem.4c00629).
Figure 1, panel A. Metadata verified against Crossref. The article is paywalled
for us; queued in `~/agents/library/paywalled.md`.

MU1700 arose by **scaffold hopping from LDN-193189** (panel B): the
pyrazolo[1,5-a]pyrimidine is replaced by furo[3,2-b]pyridine.

| # | compound | SMILES | formula | in our stock? |
|---|---|---|---|---|
| 1 | 5-chloropyridin-3-ol | `Oc1cncc(Cl)c1` | C5H4ClNO | **yes** |
| 2 | 5-chloro-2-iodopyridin-3-ol | `Oc1cc(Cl)cnc1I` | C5H3ClINO | yes |
| 3 | 6-chloro-2-TMS-furo[3,2-b]pyridine | `C[Si](C)(C)c1cc2ncc(Cl)cc2o1` | C10H12ClNOSi | yes |
| 4 | 6-chlorofuro[3,2-b]pyridine | `Clc1cnc2ccoc2c1` | C7H4ClNO | no (made) |
| 5 | **3-bromo-6-chlorofuro[3,2-b]pyridine** | `Clc1cnc2c(Br)coc2c1` | C7H3BrClNO | no (made) |
| — | quinolin-4-ylboronic acid (R³) | `OB(O)c1ccnc2ccccc12` | — | **yes** |
| — | 4-(piperazin-1-yl)phenylboronic acid (R⁶) | `OB(O)c1ccc(N2CCNCC2)cc1` | — | **yes** |
| — | TMS-acetylene | `C#C[Si](C)(C)C` | — | **yes** |

## Steps and conditions, as published

1. **1 → 2** — NaHCO₃, I₂, H₂O. Iodination *ortho* to the phenol / adjacent to N.
2. **2 → 3** — TMS-acetylene, PdCl₂(PPh₃)₂, CuI, Et₃N, dioxane. Sonogashira
   coupling followed by cyclisation of the phenol onto the alkyne: this is the
   step that **creates the furo[3,2-b]pyridine ring system**.
3. **3 → 4** — KF, MeOH. TMS removal.
4. **4 → 5** — 1. Br₂, CCl₄; 2. DBU, toluene. Bromination at C-3 (furan ring)
   with rearomatisation.
5. **5 → 6** — R³B(OR)₂, Pd cat., base. Suzuki at the **C–Br** (more reactive),
   installing quinolin-4-yl at C-3.
6. **6 → MU1700** — R⁶B(OR)₂, Pd cat., base. Suzuki at the **C–Cl**, installing
   4-(piperazin-1-yl)phenyl at C-6.

## The design feature our tools have no representation for

Intermediate **5** carries **two different halogens**. Steps 5 and 6 are
sequential and chemoselective *by construction* — the C–Br oxidative-adds under
milder conditions than the C–Cl, so the two aryl groups can be installed in a
defined order with ordinary Pd catalysis.

Our consensus route reaches the same disconnection topology through
`Brc1cnc2c(Br)coc2c1` — **Br/Br**, differing from compound 5 by one atom, and
requiring a selectivity between two chemically near-identical C–Br bonds that
nothing in our pipeline checks.

Retro tree as scored (machine-readable copy:
`outputs/mu1700/nemec_published_route.json`):

```text
→ MU1700
  [Suzuki at C-Cl: 4-(piperazin-1-yl)phenyl]
    → OB(O)c1ccc(N2CCNCC2)cc1                        (stock)
    → Clc1cnc2c(-c3ccnc4ccccc34)coc2c1
      [Suzuki at C-Br: quinolin-4-yl]
        → OB(O)c1ccnc2ccccc12                        (stock)
        → Clc1cnc2c(Br)coc2c1                        [5]
          [1. Br2/CCl4  2. DBU/toluene]
            → Clc1cnc2ccoc2c1                        [4]
              [KF, MeOH]
                → C[Si](C)(C)c1cc2ncc(Cl)cc2o1       [3]
                  [TMS-acetylene, PdCl2(PPh3)2, CuI, Et3N]
                    → C#C[Si](C)(C)C                 (stock)
                    → Oc1cc(Cl)cnc1I                 [2]
                      [I2, NaHCO3, H2O]
                        → Oc1cncc(Cl)c1              (stock)  [1]
```
