# Appendix B — our top-ranked routes

Selected from the 63 distinct routes. `arms` = how many independent
planner configurations found this route; `minScore` = our own model's
weakest-step score (we do not trust it, see main report §5).

## Route 3 — 5 steps, 3 arms

| n_reactions | n_precursors | frac_in_stock | state_score | route_cost | minScore |
|---|---|---|---|---|---|
| 5.0 | 5.0 | 1.000 | 0.975 | 18.7 | 0.009 |

Starting materials: `Brc1cnc2ccoc2c1`, `CC(C)OB(OC(C)C)OC(C)C`, `CC1(C)OB(c2ccnc3ccccc23)OC1(C)C`, `CCOC(=O)N1CCN(c2ccc(Br)cc2)CC1`, `O=C1CCC(=O)N1Br`

```text
→ c1ccc2c(-c3coc4cc(-c5ccc(N6CCNCC6)cc5)cnc34)ccnc2c1
  [Rxn] score=0.165 src=Generative Model
    → CC1(C)OB(c2ccnc3ccccc23)OC1(C)C (stock)
    → Brc1coc2cc(-c3ccc(N4CCNCC4)cc3)cnc12
      [Rxn] score=0.165 src=Generative Model
        → CCOC(=O)N1CCN(c2ccc(-c3cnc4c(Br)coc4c3)cc2)CC1
          [Rxn] score=0.165 src=Generative Model
            → Brc1cnc2c(Br)coc2c1
              [Rxn] score=0.009 src=Generative Model Fallback
                → O=C1CCC(=O)N1Br (stock)
                → Brc1cnc2ccoc2c1 (stock)
            → CCOC(=O)N1CCN(c2ccc(B(O)O)cc2)CC1
              [Rxn] score=0.212 src=Generative Model
                → CC(C)OB(OC(C)C)OC(C)C (stock)
                → CCOC(=O)N1CCN(c2ccc(Br)cc2)CC1 (stock)
```

## Route 4 — 5 steps, 3 arms

| n_reactions | n_precursors | frac_in_stock | state_score | route_cost | minScore |
|---|---|---|---|---|---|
| 5.0 | 5.0 | 1.000 | 0.975 | 18.7 | 0.009 |

Starting materials: `Brc1coc2cccnc12`, `CC(C)OB(OC(C)C)OC(C)C`, `CC1(C)OB(c2ccnc3ccccc23)OC1(C)C`, `CCOC(=O)N1CCN(c2ccc(Br)cc2)CC1`, `O=C1CCC(=O)N1Br`

```text
→ c1ccc2c(-c3coc4cc(-c5ccc(N6CCNCC6)cc5)cnc34)ccnc2c1
  [Rxn] score=0.165 src=Generative Model
    → CC1(C)OB(c2ccnc3ccccc23)OC1(C)C (stock)
    → Brc1coc2cc(-c3ccc(N4CCNCC4)cc3)cnc12
      [Rxn] score=0.165 src=Generative Model
        → CCOC(=O)N1CCN(c2ccc(-c3cnc4c(Br)coc4c3)cc2)CC1
          [Rxn] score=0.165 src=Generative Model
            → Brc1cnc2c(Br)coc2c1
              [Rxn] score=0.009 src=Generative Model Fallback
                → O=C1CCC(=O)N1Br (stock)
                → Brc1coc2cccnc12 (stock)
            → CCOC(=O)N1CCN(c2ccc(B(O)O)cc2)CC1
              [Rxn] score=0.212 src=Generative Model
                → CC(C)OB(OC(C)C)OC(C)C (stock)
                → CCOC(=O)N1CCN(c2ccc(Br)cc2)CC1 (stock)
```

## Route 1 — 5 steps, 3 arms

| n_reactions | n_precursors | frac_in_stock | state_score | route_cost | minScore |
|---|---|---|---|---|---|
| 5.0 | 5.0 | 1.000 | 0.963 | 20.0 | 0.003 |

Starting materials: `Brc1coc2cccnc12`, `ClCCNCCCl`, `O=C1CCC(=O)N1Br`, `O=[N+]([O-])c1ccc(B(O)O)cc1`, `OB(O)c1ccnc2ccccc12`

```text
→ c1ccc2c(-c3coc4cc(-c5ccc(N6CCNCC6)cc5)cnc34)ccnc2c1
  [Rxn] score=0.1 src=AiZynthFinder Neural Network
    → ClCCNCCCl (stock)
    → Nc1ccc(-c2cnc3c(-c4ccnc5ccccc45)coc3c2)cc1
      [Rxn] score=0.158 src=Generative Model
        → O=[N+]([O-])c1ccc(-c2cnc3c(-c4ccnc5ccccc45)coc3c2)cc1
          [Rxn] score=0.017 src=Generative Model
            → OB(O)c1ccnc2ccccc12 (stock)
            → O=[N+]([O-])c1ccc(-c2cnc3c(Br)coc3c2)cc1
              [Rxn] score=0.09 src=Generative Model
                → O=[N+]([O-])c1ccc(B(O)O)cc1 (stock)
                → Brc1cnc2c(Br)coc2c1
                  [Rxn] score=0.003 src=Generative Model Fallback
                    → O=C1CCC(=O)N1Br (stock)
                    → Brc1coc2cccnc12 (stock)
```

## Route 2 — 5 steps, 3 arms

| n_reactions | n_precursors | frac_in_stock | state_score | route_cost | minScore |
|---|---|---|---|---|---|
| 5.0 | 5.0 | 1.000 | 0.963 | 20.0 | 0.003 |

Starting materials: `Brc1cnc2ccoc2c1`, `ClCCNCCCl`, `O=C1CCC(=O)N1Br`, `O=[N+]([O-])c1ccc(B(O)O)cc1`, `OB(O)c1ccnc2ccccc12`

```text
→ c1ccc2c(-c3coc4cc(-c5ccc(N6CCNCC6)cc5)cnc34)ccnc2c1
  [Rxn] score=0.1 src=AiZynthFinder Neural Network
    → ClCCNCCCl (stock)
    → Nc1ccc(-c2cnc3c(-c4ccnc5ccccc45)coc3c2)cc1
      [Rxn] score=0.158 src=Generative Model
        → O=[N+]([O-])c1ccc(-c2cnc3c(-c4ccnc5ccccc45)coc3c2)cc1
          [Rxn] score=0.017 src=Generative Model
            → OB(O)c1ccnc2ccccc12 (stock)
            → O=[N+]([O-])c1ccc(-c2cnc3c(Br)coc3c2)cc1
              [Rxn] score=0.09 src=Generative Model
                → O=[N+]([O-])c1ccc(B(O)O)cc1 (stock)
                → Brc1cnc2c(Br)coc2c1
                  [Rxn] score=0.003 src=Generative Model Fallback
                    → O=C1CCC(=O)N1Br (stock)
                    → Brc1cnc2ccoc2c1 (stock)
```

## Route 5 — 6 steps, 3 arms

| n_reactions | n_precursors | frac_in_stock | state_score | route_cost | minScore |
|---|---|---|---|---|---|
| 6.0 | 6.0 | 1.000 | 0.963 | 25.7 | 0.003 |

Starting materials: `Brc1ccnc2ccccc12`, `Brc1coc2cccnc12`, `CC(C)OB(OC(C)C)OC(C)C`, `CC1(C)OB(B2OC(C)(C)C(C)(C)O2)OC1(C)C`, `CCOC(=O)N1CCN(c2ccc(Br)cc2)CC1`, `O=C1CCC(=O)N1Br`

```text
→ c1ccc2c(-c3coc4cc(-c5ccc(N6CCNCC6)cc5)cnc34)ccnc2c1
  [Rxn] score=0.165 src=Generative Model
    → Brc1ccnc2ccccc12 (stock)
    → CC1(C)OB(c2coc3cc(-c4ccc(N5CCNCC5)cc4)cnc23)OC1(C)C
      [Rxn] score=0.245 src=Generative Model
        → CC1(C)OB(B2OC(C)(C)C(C)(C)O2)OC1(C)C (stock)
        → Brc1coc2cc(-c3ccc(N4CCNCC4)cc3)cnc12
          [Rxn] score=0.165 src=Generative Model
            → CCOC(=O)N1CCN(c2ccc(-c3cnc4c(Br)coc4c3)cc2)CC1
              [Rxn] score=0.165 src=Generative Model
                → Brc1cnc2c(Br)coc2c1
                  [Rxn] score=0.003 src=Generative Model Fallback
                    → O=C1CCC(=O)N1Br (stock)
                    → Brc1coc2cccnc12 (stock)
                → CCOC(=O)N1CCN(c2ccc(B(O)O)cc2)CC1
                  [Rxn] score=0.212 src=Generative Model
                    → CC(C)OB(OC(C)C)OC(C)C (stock)
                    → CCOC(=O)N1CCN(c2ccc(Br)cc2)CC1 (stock)
```

## Route 6 — 6 steps, 3 arms

| n_reactions | n_precursors | frac_in_stock | state_score | route_cost | minScore |
|---|---|---|---|---|---|
| 6.0 | 6.0 | 1.000 | 0.963 | 25.7 | 0.003 |

Starting materials: `Brc1ccnc2ccccc12`, `Brc1cnc2ccoc2c1`, `CC(C)OB(OC(C)C)OC(C)C`, `CC1(C)OB(B2OC(C)(C)C(C)(C)O2)OC1(C)C`, `CCOC(=O)N1CCN(c2ccc(Br)cc2)CC1`, `O=C1CCC(=O)N1Br`

```text
→ c1ccc2c(-c3coc4cc(-c5ccc(N6CCNCC6)cc5)cnc34)ccnc2c1
  [Rxn] score=0.165 src=Generative Model
    → Brc1ccnc2ccccc12 (stock)
    → CC1(C)OB(c2coc3cc(-c4ccc(N5CCNCC5)cc4)cnc23)OC1(C)C
      [Rxn] score=0.245 src=Generative Model
        → CC1(C)OB(B2OC(C)(C)C(C)(C)O2)OC1(C)C (stock)
        → Brc1coc2cc(-c3ccc(N4CCNCC4)cc3)cnc12
          [Rxn] score=0.165 src=Generative Model
            → CCOC(=O)N1CCN(c2ccc(-c3cnc4c(Br)coc4c3)cc2)CC1
              [Rxn] score=0.165 src=Generative Model
                → Brc1cnc2c(Br)coc2c1
                  [Rxn] score=0.003 src=Generative Model Fallback
                    → O=C1CCC(=O)N1Br (stock)
                    → Brc1cnc2ccoc2c1 (stock)
                → CCOC(=O)N1CCN(c2ccc(B(O)O)cc2)CC1
                  [Rxn] score=0.212 src=Generative Model
                    → CC(C)OB(OC(C)C)OC(C)C (stock)
                    → CCOC(=O)N1CCN(c2ccc(Br)cc2)CC1 (stock)
```

## Route 50 — the only route that BUILDS the bicycle

Discussed in main report §4. Constructs the furo[3,2-b]pyridine ring by
intramolecular acylation of a pyridinyl ether — the same strategic move
as Němec's Sonogashira/cyclisation, by different chemistry. 8 steps,
found by 1 configuration, and it also builds the piperazine.

| n_reactions | frac_in_stock | state_score | route_cost |
|---|---|---|---|
| 8.0 | 0.800 | 0.761 | 90.7 |

```text
→ c1ccc2c(-c3coc4cc(-c5ccc(N6CCNCC6)cc5)cnc34)ccnc2c1
  [Rxn] score=0.165 src=Generative Model
    → OB(O)c1ccnc2ccccc12 (stock)
    → Clc1coc2cc(-c3ccc(N4CCNCC4)cc3)cnc12
      [Rxn] score=0.1 src=AiZynthFinder Neural Network
        → ClCCNCCCl (stock)
        → Nc1ccc(-c2cnc3c(Cl)coc3c2)cc1
          [Rxn] score=0.158 src=Generative Model
            → O=[N+]([O-])c1ccc(-c2cnc3c(Cl)coc3c2)cc1
              [Rxn] score=0.09 src=Generative Model
                → O=[N+]([O-])c1ccc(B(O)O)cc1 (stock)
                → Clc1coc2cc(Br)cnc12
                  [Rxn] score=0.028 src=Generative Model
                    → O=C(O)c1oc2cc(Br)cnc2c1Cl
                      [Rxn] score=0.008 src=Generative Model Fallback
                        → CCOC(=O)c1oc2cc(Br)cnc2c1Cl
                          [Rxn] score=0.1 src=AiZynthFinder Neural Network
                            → CCOC(=O)C(Oc1cncc(Br)c1)C(=O)Cl
                              [Rxn] score=0.235 src=Generative Model
                                → O=S(Cl)Cl (stock)
                                → CCOC(=O)C(Oc1cncc(Br)c1)C(=O)O
```