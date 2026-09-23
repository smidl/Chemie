# Appendix D — route diversity: method and results

Two metrics; see main report §2.

**TED** — tree edit distance between route trees (Genheden, Engkvist & Bjerrum,
*Clustering of synthetic routes using tree edit distance*, J. Cheminform. 2021;
package `route_distances`, also used internally by AiZynthFinder).

**Intermediate-Tanimoto** — proposed by V. Němec: represent each route by Morgan
fingerprints of its *intermediates*, compare two routes by the symmetric mean of
best-match Tanimoto. Note this ignores purchased starting materials by
construction, which is why regio-twin routes score exactly 0.000.

Agreement between the two over all 1,953 pairs: **Spearman ρ = 0.820**,
Pearson r = 0.804.

## Threshold profiles

| TED threshold | distinct groups | regio-twin pairs merged (of 16) |
|---|---|---|
| 1 | 58 | 0 |
| 2 | 31 | 14 |
| 3 | 26 | 16 |
| 5 | 21 | 16 |
| 8 | 13 | 16 |
| 12 | 9 | 16 |
| 20 | 3 | 16 |

| Tanimoto threshold | distinct groups | regio-twin pairs merged |
|---|---|---|
| 0.05 | 27 | 16 |
| 0.10 | 19 | 16 |
| 0.15 | 16 | 16 |
| 0.30 | 10 | 16 |
| 0.50 | 3 | 16 |

## Separation of trivial variants

| metric | regio-twin pairs (median) | all pairs (median) |
|---|---|---|
| TED | 1.37 | 15.65 |
| intermediate-Tanimoto | 0.000 | 0.472 |

## Distance from Němec's published route to ours

| metric | nearest of our 63 | median to ours | median *among* our own |
|---|---|---|---|
| TED | 13.57 | 16.81 | 15.68 |
| intermediate-Tanimoto | 0.504 | 0.659 | 0.472 |

Under his own metric his route is further from any of ours than a typical pair
of our routes are from each other: we did not find anything close to it.

## Silhouette-optimal clustering

k = 2 clusters (silhouette 0.514): sizes [52, 11].
This is too coarse to be useful and is reported only for completeness; the
threshold profile above is the usable form.