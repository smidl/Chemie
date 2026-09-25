Follow-up: split the held-out radical steps by whether `CollateAFM.trainable`
keeps them, and scored each half separately. Same nano checkpoints, sampling with
frequency ranking.

| model | kept (2,414) | dropped (2,674) |
|---|---|---|
| **afm** | **0.9925** | **0.0381** |
| flower_discrete | 0.9350 | 0.7319 |

top-10: afm 0.9946 / 0.0453, flower_discrete 0.9739 / 0.9144.

`flower_discrete` has no training filter, so it trained on both halves. It loses
20 points on the dropped half — those steps are genuinely harder. afm loses 95,
to near zero, and its top-10 there is 4.5 %, so it is not close on any of ten
samples.

The full-set number is just the average of the two halves:

```
0.9925 × 2414/5088  +  0.0381 × 2674/5088  =  0.4911      (measured: 0.4914)
```

So the read on the earlier table was wrong, and in your favour: **afm is the
strongest model in the comparison on the radical chemistry it is allowed to train
on — 0.9925 against flower_discrete's 0.9350.** The apparent collapse is entirely
the half that `_radical_moves` discards before training.

That makes the fix worth about +0.5 top-1 on radical steps rather than a marginal
cleanup, and 0.9925 on the kept half is the evidence for what the other half
could reach.
