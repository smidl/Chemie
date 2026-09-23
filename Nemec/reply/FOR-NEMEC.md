# MU1700 retrosynthesis — what we have, and what we do not

Prepared 2026-09-03 for Václav Němec. Answers the four points in your email.

---

## 0. First, a correction: we did **not** read your paper

You wrote that Claude is probably reading your procedures from the publication.
It is not, and we checked rather than assumed.

Our knowledge layer queries an index of **1,048,347 reaction products** built
from the Open Reaction Database and patent extraction. For MU1700 it returned
**0 hits** — every single disconnection in every route came from a model trained
on **USPTO patent reactions**, which does not contain *J. Med. Chem.* 2024,
67, 12632–12659.

So the routes below were produced without any access to your published route.
That makes the comparison worth doing rather than circular — and it is why we
would very much like to see your scheme (thank you for the figure link; it sits
behind the ACS paywall for us, so if you can send the SI scheme or a PDF we will
compare properly).

---

## 1. "Every minimal change should not count as a new route" — this is solved

This was the sharpest thing in your email, and you identified exactly the failure
we had measured on our side the week before: our planner returned **63 distinct
routes** for MU1700, and many were trivial variants of each other.

### What the field does

The established answer is **tree edit distance (TED)** between route trees:

> Genheden, Engkvist & Bjerrum, *Clustering of synthetic routes using tree edit
> distance*, J. Cheminform. 2021.

It ships as the open-source `route_distances` package and is what **AiZynthFinder
itself** uses to cluster its output. So the tooling you were asking about exists
and we already had it installed.

### Your Tanimoto idea also works — and the two agree

We implemented your proposal as well: represent each route by the Morgan
fingerprints of its **intermediates**, and compare two routes by the symmetric
mean of best-match Tanimoto. Over all 1,953 route pairs:

| | |
|---|---|
| Spearman ρ (your metric vs TED) | **0.820** |
| Pearson r | 0.804 |

Your intuition reproduces the published metric closely. We are not saying this to
be polite — we ran it because if the two had *disagreed* that would have been the
more interesting result.

### Both of them do what you actually asked for

We had an independent ground truth to test against. Among the 63 routes there are
**16 pairs that differ only in which bromo-furopyridine you start from** — the
rest of the route is identical. A useful metric must merge those.

| | twin pairs | all pairs |
|---|---|---|
| TED, median distance | **1.37** | 15.65 |
| your Tanimoto, median | **0.000** | 0.472 |

Both separate cleanly. Under your metric the twins are *exactly* identical,
because they converge on the same first intermediate — the two monobromides give
the same dibromide after bromination.

**One design choice you should know about:** our implementation of your metric
compares intermediates only, ignoring purchased starting materials. That is why
the twins score 0.000. It is the behaviour you asked for here, but it means the
metric is blind to a change of starting material that does not change any
intermediate. Worth deciding deliberately rather than inheriting from us.

### The knob you wanted

Rather than a fixed number of clusters, here is the filter as a slider — pick a
distance and see how many genuinely distinct routes remain:

| TED threshold | distinct groups | twin pairs merged |
|---|---|---|
| 1 | 58 | 0/16 |
| 2 | 31 | 14/16 |
| **3** | **26** | **16/16** |
| 5 | 21 | 16/16 |
| 8 | 13 | 16/16 |
| 12 | 9 | 16/16 |
| 20 | 3 | 16/16 |

| your Tanimoto threshold | distinct groups | twin pairs merged |
|---|---|---|
| 0.05 | 27 | 16/16 |
| 0.10 | 19 | 16/16 |
| **0.15** | **16** | **16/16** |
| 0.30 | 10 | 16/16 |
| 0.50 | 3 | 16/16 |

So: **63 raw routes → about 13–26 real alternatives**, depending on how coarse
you want to be. Our suggestion is to give you the slider rather than pick for you.

---

## 2. "Do you have a ranking system?" — yes, seven of them, and they disagree

Our first answer to you was going to be "no". That was wrong, and checking it
properly changed the answer.

**AiZynthFinder ships an open-source scoring framework** — about 20 route
scorers — and we already had it installed and were not using it. Seven run on
your routes out of the box:

| scorer | what it measures | range over the 63 routes |
|---|---|---|
| `n_reactions` | route length | 4 – 13 |
| `max_transform` | longest linear sequence | 4 – 8 |
| `n_precursors` | how many starting materials | 5 – 9 |
| `n_precursors_stock` | how many are purchasable | 4 – 8 |
| `frac_in_stock` | fraction of the tree that is purchasable | 0.80 – 1.00 |
| `state_score` | AiZynthFinder's own composite | 0.761 – 0.975 |
| `route_cost` | Badowski-style cost (materials + reactions, yield-weighted) | 18.7 – 121.7 |

### The useful part is where they disagree

They are not one opinion. Pairwise Spearman ρ splits them into two families that
are almost independent of each other:

- **length/cost**: `n_reactions`, `max_transform`, `n_precursors`, `route_cost`
  (ρ = 0.68 – 0.92 among themselves)
- **availability**: `frac_in_stock`, `state_score` (ρ = 0.88 with each other)

and *between* the families ρ is only **−0.27** (`frac_in_stock` vs
`n_reactions`). In plain terms: **the shortest routes are not the ones built from
the most readily purchasable material**, and no single number reconciles that —
it is a genuine trade-off you would make differently depending on whether you are
optimising time or cost.

This is why we would give you the columns rather than one ranking.

### Where they agree, and it is worth noting

The cheapest routes by `route_cost` (18.7, five steps) are also among the ones
found independently by the most planner configurations. Our two best-supported
routes are top of that list.

### Two honest caveats

- **These are heuristics, not chemistry.** None has been validated against
  chemist judgement — on your molecule or any other. They count steps and check a
  catalogue; none of them knows that a Suzuki on a dibromide needs the
  selectivity to work out.
- **The one scorer that measures literature precedent is dead in our pipeline.**
  `avg_template_occurrence` — how often each template appears in the reaction
  corpus — returns 0.000 for every route, because our code discards the template
  occurrence metadata before the route is stored. That is a bug on our side, not
  a limit of the method, and precedent is probably the single thing you would
  weight most heavily. We are fixing it.

Our own model's per-step score, by contrast, correlates only weakly and mostly
*negatively* with all seven (ρ = −0.12 to −0.64), which is one more reason we do
not put weight on it.

## 3. "The same analysis from 2–3 other packages"

Honest status, rather than a promise:

| software | status |
|---|---|
| **AiZynthFinder** (template policy, USPTO) | **done** — the 63 routes above; two template policies (standard + ringbreaker) |
| **ReactionT5** (transformer, unrelated architecture) | **running now** — validated, solved MU1700 in a small pilot; a full run is queued on our cluster |
| **ASKCOS** | **not installed.** It needs its own model stack; we will not claim a result we have not run |
| LocalRetro, Chemformer, MEGAN, GLN | wrappers available, model weights not deployed |

ReactionT5 matters most because it is architecturally unrelated to a template
policy — where it and AiZynthFinder *agree*, that is real evidence rather than
one template library seen twice.

One early signal from it already: asked directly for MU1700's precursors,
ReactionT5 proposed a **Boc**-protected piperazine, whereas the template model
chose an **ethyl** carbamate. We had flagged the ethyl carbamate as odd by
inspection; a second, independent model appears to agree with the chemist's
instinct rather than ours.

---

## 4. Two questions where five minutes of your time removes most of the noise

**(a) Which bromo-furopyridine do you actually start from?** Our routes split 22
vs 20 between the two, and the choice fixes the whole sequence: the isomer
brominated on the **pyridine** ring couples the phenylpiperazine first and then
needs a regioselective NBS bromination of the furan for the quinoline; the isomer
brominated on the **furan** ring does the quinoline first. Structures attached
(`nemec_q_structures.png`). This single answer collapses 16 pairs.

**(b) Would you ever build the piperazine on the molecule?** **36 of 63 routes**
construct the piperazine ring from bis(2-chloroethyl)amine plus an aniline —
often via 4-nitrophenylboronic acid and a nitro reduction — rather than buying a
preformed 4-bromophenylpiperazine. We suspect you would reject that on sight for
a medicinal-chemistry target, but we would rather ask than assume. If you rule it
out, more than half the route set disappears.

---

## 5. What the routes agree on, chemically

Across all runs the consensus is stable, and it is not unreasonable: build the
two biaryl bonds by **Suzuki coupling**, install the second halide with **NBS**
(present in 46 of 63 routes), and carry the piperazine on a para-substituted
phenyl. The disagreements are the three above: which monobromide to start from,
whether to buy or build the piperazine, and which protecting group.

We are not claiming these routes are good. We are claiming they are a
well-characterised starting point, that we can now tell you which of them are
genuinely different, and that we know precisely which parts we cannot yet judge.
