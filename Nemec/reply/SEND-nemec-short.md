# MU1700 — what our software found

V. Šmídl, 2026-09-18. Full route trees and appendices on request.

---

## Part 1 — Blind (no knowledge of your route)

Knowledge base returned 0 hits for this molecule; every result below comes
from a USPTO-trained model with no access to your route or its origin.

**Methods**

| tool | basis | output |
|---|---|---|
| AiZynthFinder MCTS, USPTO ± RingBreaker, default priors, 1000 iterations | Genheden et al. 2020 | 867 distinct routes |
| ReactionT5 (transformer, no templates) | Sagawa & Kojima, *J. Cheminform.* 2025 | solves MU1700, 26 routes |
| ASKCOS `uspto_higher_level` (independent 32,622-template corpus) | — | top disconnections, with literature-precedent counts |
| Route scoring: 7 measures + real supplier pricing (63-route scored subset) | Badowski, Molga & Grzybowski, *Chem. Sci.* 2019 | see below |

Stock: 313,458 compounds, [eMolecules' building-block catalog](https://www.emolecules.com/products/building-blocks).

**Best route found** (cheapest complete route, real pricing, found
independently by 5 of the scored arms):

> `O=C1CCC(=O)N1Br` + `Brc1coc2cccnc12` → `Brc1cnc2c(Br)coc2c1`
> `CC(C)OB(OC(C)C)OC(C)C` + `CCOC(=O)N1CCN(c2ccc(Br)cc2)CC1` → boronic ester
> `Brc1cnc2c(Br)coc2c1` + boronic ester → mono-coupled intermediate
> deprotect piperazine
> `Brc1ccnc2ccccc12` + intermediate → **MU1700**

5 steps, **$412.65/mmol**. Buys the bromofuropyridine core rather than
building it — the consensus strategy across the blind search.

**How your route compares** (your route was not used to guide the search or
scoring above; this is a post-hoc comparison against it):

| | value |
|---|---|
| your 6 steps reproduced exactly | 2 of 6 |
| your 10 molecules reached | 7 of 10 |
| your route's rank on real-priced cost, among 64 | **#1** ($222.75/mmol) |
| your route's rank on `n_precursors`, `n_precursors_stock`, `frac_in_stock` | **#1, #1, #1** |
| routes that **construct** the bicycle (your strategy, not the consensus) | 33 of 867 (3.8%) |
| TED to nearest of our routes | 8.89 |

**Diversity metric** (also blind — compares our own route pairs to each
other, not to your route): tree-edit distance (Genheden 2021) and your
intermediate-Tanimoto proposal agree at Spearman ρ = 0.82 over 1,953 route
pairs; both collapse the 16 pairs differing only in starting
bromofuropyridine. Our own bond-level disconnection label is the only one of
the three that isolates the single route (of 867) matching your
intermediates once your route *is* used for comparison; tree-edit distance
and Badowski's rule both miss it or tie it with unrelated routes.

## Part 2 — Route-informed (uses your known intermediate)

Everything below used your exact route as an input, to test the tools'
limits rather than to search blind. Not a fair test of what the software
would hand a chemist with an unknown target — a diagnostic of what it's
capable of when told what to look for.

**Is the ring-forming disconnection even in the template library?** Queried
directly: yes — the exact move you used (TMS-alkyne on the chloropyridinol)
is proposed at prior 0.045, rank 3 of 50, under RingBreaker alone. Combined
with USPTO's larger policy it drops to prior 0.0027, rank 25 — AiZynthFinder
concatenates the two policies' raw priors without renormalising them onto a
common scale, and that's what buries it.

**Reweighting RingBreaker's priors ×20**, at the same 1000-iteration budget
used in Part 1:

| | Part 1 (default priors) | reweighted ×20 |
|---|---:|---:|
| routes | 867 | 550 |
| routes that **construct** the bicycle | 33 (3.8%) | **505 (92%)** |
| your key intermediate (`Clc1cnc2c(Br)coc2c1`) reached | no | **yes** |
| TMS-acetylene reached | no | **yes** |

The ×20 weight was chosen specifically to make your known answer reappear —
a demonstrated lever, not a calibrated general setting. It shouldn't be read
as "the software finds your route 92% of the time"; it's "the capability is
there once told where to look."
