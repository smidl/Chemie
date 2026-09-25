# `_radical_moves` decomposes only single-move steps — 52% of radical training data is silently dropped

## What happens

`decompose()` returns `None` for radical steps needing more than one move, because
`_radical_moves()` fails. With `train_filter: true` those steps are dropped from
training.

## Reproducer

```
[Cl:2][O:3].[O:1] >> [Cl:2].[O:1][O:3]
```

3 atoms. `in_sector(product)` is `True`, `_radical_moves(changes)` returns `None`.

A valid 2-move decomposition exists: `HOMOLYSIS(Cl:2, O:3)` then
`COLLIGATION(O:1, O:3)`.

## How much

`CollateAFM.trainable` over the corpus's own augmentation buckets:

| bucket | steps | dropped |
|---|---|---|
| RS (radical) | 3,223 | **41.2 %** |
| RC (radical) | 1,383 | **77.7 %** |
| PM (polar) | 12,322 | 0.06 % |
| PC (polar) | 14,746 | 0.01 % |

Every radical drop is `_radical_moves -> None` (1329/1329 RS, 1074/1074 RC).
None are `in_sector` or `_order`.

Of the kept RS steps, **1,892 of 1,894 have exactly one move** — the branch
handles m=1 and little else. The drop rate tracks the mean move count per bucket
(RS 1.57 moves → 41 %, RC 2.11 → 78 %).

## Effect on the model

Released `afm` nano checkpoint on the 5,088 held-out RS+RC steps, sampling with
frequency ranking:

| model | top-1 | top-10 |
|---|---|---|
| **afm** | **0.4914** | **0.4959** |
| flower_discrete | 0.8263 | 0.9440 |
| flower | 0.7492 | 0.8449 |

afm's top-10 minus top-1 is 0.005 here against 0.072 on polar: the ten samples
are near-identical. Validity and all three conservation checks stay 1.0000 — the
guarantee holds, the products are valid and wrong.

## Why

`_radical_moves` is a single special case, by its own docstring:

> "A step of odd parity is a bond breaking homolytically or two radicals
> combining -- **on this dataset every one of them is a metal-phosphorus bond
> doing exactly that** -- so it is one move."

True of the patent-derived steps. Not true of the RMechDB buckets, which are real
radical chemistry. The guard rejects everything else on its first line:

```python
if len(changes.bonds) != 1 or len(changes.lone) != 2:
    return None
```

The reproducer above has two bond changes (Cl-O breaks, O-O forms), so it exits
there.

## Suggested fix

`_pair_moves` handles the general even-parity case by delegating to
`chem.electron_arrows` and expanding bond-to-bond migrations into two moves.
`_radical_moves` has no equivalent -- it needs to become a search rather than a
pattern match.

The smallest version that would work: one slot per unit of bond-order change,
three candidate moves per slot (`LONE_TO_BOND` either direction or `COLLIGATION`
for +1; `BOND_TO_LONE` either direction or `HOMOLYSIS` for -1), keep the
assignments whose per-atom diagonal contributions match the required change
exactly, then hand the result to the existing `_order`. `_order` already copes
with multi-move steps, since `_pair_moves` emits two moves per migration, so the
change is contained in one function.

We have that search implemented and measured -- it is what produced the 99.29 %
above. Happy to send it as a PR if useful, but it is your design decision whether
the assignment should stay minimal (no move and its inverse on the same bond) or
search further, so it may be quicker for you to write.

## Ruled out

- **Not the validity table.** `local_table` admits every radical local state in
  RMechDB; zero atoms exceed it. `in_sector` passes on every dropped step.
- **Not the ordering.** `_order` is never reached.
- **The decompositions exist.** An independent implementation of the same
  alphabet finds valid, ordered decompositions for 99.29 % of these 4,606 steps.
