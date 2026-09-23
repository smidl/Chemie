# Your two compounds — what our software found (blind)

V. Šmídl, 2026-09-15. Methods and results below; full route trees on request.

---

## Setup

We ran both compounds through our full retrosynthesis toolchain, using a blind protocol.

- **Compound 1**: `CCN1CCC2(N=C(C3=CC(OC)=CC=C3)CC(C4=C(O)C(OCC)=CC=C4)N2)CC1`
- **Compound 2**: `CC(C)N(C1=CC=C(NC(CSC2=NN=C(C3=CC=C(C)C=C3)N2N)=O)C=C1)C4=CC=CC=C4`

## Methods

**Search tools.** Eight independent search methods per compound, all against
the same 313,458-compound purchasable-stock database — a snapshot of
[eMolecules' building-block catalog](https://www.emolecules.com/products/building-blocks)
(aggregated supplier stock, with real per-supplier pricing):

| method | basis | compound 1 routes | compound 2 routes |
|---|---|---:|---:|
| AiZynthFinder MCTS, USPTO templates | Genheden et al. 2020 | 10 | 1,258 |
| AiZynthFinder MCTS, USPTO + RingBreaker | Genheden et al. 2020 | 11 | 1,240 |
| — same, + neural filter policy | Genheden et al. 2020 | 8 | 1,334 |
| Retro\* (A\*-style guided search) | Chen et al., ICML 2020 | 7 | 1,309 |
| Proof-number search | Franz et al., IJCAI 2022 | 25 | 4 |
| Cost-objective search (real supplier prices) | Badowski, Molga & Grzybowski, *Chem. Sci.* 2019 | 25 | 821 |
| SeeA\*, value net A (learned heuristic) | AI Center, in-house | 0 — did not solve | 1 |
| SeeA\*, value net B (independently trained) | AI Center, in-house | 0 — did not solve | 1 |
| ReactionT5 (transformer, retro-star decoding) | Sagawa & Kojima, *J. Cheminform.* 2025 | 0 — did not solve | 0 — did not solve |
| ReactionT5 (transformer, breadth-first decoding) | Sagawa & Kojima, *J. Cheminform.* 2025 | 0 — did not solve | 0 — did not solve |

**Analysis.** Routes from all methods were pooled and de-duplicated on
molecular structure (not on the text of the reaction template, which would
wrongly merge two routes that use the same reaction type on different
substrates), keeping a record of which method(s) independently found each
route. Every route was checked end-to-end: does every starting material
actually sit in that purchasable-compound database, or does the route
dead-end on something nobody sells? Only a route that fully resolves is a
real answer. Complete routes were then priced with real supplier quotes
(USD/mmol, eMolecules) and ranked jointly on step count and price.

Separately, to tell genuinely different chemistry apart from routes that
only swap a leaving group, each step was labelled by **which bond it
forms** — fragmenting the product on that bond and checking the pieces
match the reactants, rather than comparing the reaction-template text (which
calls the same reaction type on two different substrates identical, and
would hide the distinction we needed here). Routes were then clustered by
the set of bonds they form, so "how many really different strategies are in
this pool" could be answered directly instead of guessed from inspection.

## Results

This is the number that actually separates the two compounds:

| | compound 1 | compound 2 |
|---|---:|---:|
| distinct routes pooled from all 8 methods | 75 | 4,770 |
| of those, **fully resolved to purchasable starting materials** | **0** | **2,343** |

**Compound 2: not just solved, over-solved.** Half the pooled routes are
complete, real answers. The best of them:

> **CC(C)Nc1ccccc1** + Nc1ccc(Br)cc1 → CC(C)N(c1ccccc1)c1ccc(N)cc1
> **CCOC(=O)CCl** + [above] → CC(C)N(c1ccccc1)c1ccc(NC(=O)CCl)cc1
> **Cc1ccc(-c2nnc(S)n2N)cc1** + [above] → **compound 2**

3 steps, **\$62/mmol** in real starting-material cost, 100% purchasable, and
independently rediscovered by 3 of the 8 methods (Retro\*, and AiZynthFinder
MCTS with and without RingBreaker).

The bond-level clustering of all 2,343 complete routes turns up exactly
**two** genuinely different strategies, not many — they differ in **which
bond is formed last**, the amide or the thioether, and every other
"different" route we found is a leaving-group or halide variant of one of
these two:

> **Strategy A** (above): build the chloroacetamide first, close with a
> thioether-forming **S-alkylation last**. 1,426 of the 2,343 complete
> routes; cheapest member \$62/mmol, found independently by 3 of 8 methods.

> **Strategy B**: build the thioether first, close with an **amide coupling
> last** — same four building blocks, different order. 917 of the 2,343
> complete routes; cheapest member \$76/mmol (rank 862, methyl instead of
> ethyl ester, otherwise identical reagents), found by 1 of 8 methods.

Both are real, complete, fully-priced options; we are not aware of a chemical
reason to prefer one over the other, which is exactly the kind of question
your judgement would settle and ours can't. A separate route (4 steps,
building the aniline by nitro reduction rather than buying it pre-formed) is
the single most corroborated route in the whole exercise — found
independently by 5 of the 8 methods — but is a variant of Strategy A, not a
third strategy.

**Compound 1: not one of the 75 routes actually closes.** Every single one
dead-ends on at least one intermediate that isn't in the purchasable-compound
database. This is the real reason it "doesn't converge" — it isn't that our
methods disagree with each other, it's that none of them can finish the job.
The closest attempt (8 steps, 86% of it purchasable, independently found by
3 of the 8 methods) is blocked by exactly one leftover piece:

> `CCOc1cccc(C2CC(c3cccc(OC)c3)=NC(CCCl)(COS(C)(=O)=O)N2)c1OCc1ccccc1`

— an advanced intermediate that already carries most of the target
scaffold. It is not that our tools converge on one specific missing building
block: across all 75 routes we counted **42 different** non-purchasable
intermediates blocking closure, none of them recurring in more than 8 of the
75 attempts. The same bond-level clustering that found only 2 real
strategies for compound 2 finds **58 distinct strategies among these 75
routes** — almost no repetition at all. So this isn't "the tools agree on an
approach that happens to fail" — they're scattered across dozens of
different, unrelated approaches, and none of them reaches the stock.
(Consistent with this: our two independently-trained learned search models,
which solve compound 2 in 3 search steps each, cannot find any route to
compound 1 at all after 500 search steps.)

### We tried to fix it, and failed — here is exactly why

Before concluding anything, we ran down every lever we have. In order:

1. **More search depth.** The closest attempt above stops at exactly our
   8-step search limit, one step short of taking what our own model rates as
   by far its best next move. We reran all 8 methods with the limit raised
   to 12 steps. Result: **still zero complete routes.** The search does use
   the extra room — its best attempt improves from 86% to 91% purchasable —
   but it simply runs into a *new* blocked intermediate one or two steps
   further in, every time. Depth was a real constraint, but not the
   bottleneck.
2. **Whether a good disconnection was being out-voted by a worse one.**
   Queried our model directly for every way it knows to take the blocking
   intermediate apart, with no search involved. Its favourite move (91%
   confidence) is exactly the one that shrinks the molecule — it isn't
   being buried under competing options. So the search is doing the right
   thing with what it knows; it just doesn't know a way to take apart the
   ring system itself.
3. **A second, independent source of reaction knowledge.** Repeated the same
   query against a completely different template library (ASKCOS,
   32,622 USPTO-mined reaction templates, built and trained independently
   of the first). If our first model was simply missing a template the
   second one had, this would find it. It didn't: on the bare ring system
   with no other substituents, its top-scoring "match" turns out, on
   inspection, not to be a real disconnection at all (same ring count,
   same atom count — a tautomer flip, not a bond cut). On your actual
   molecule, the only genuine disconnection it proposes removes an
   N-ethyl group elsewhere in the molecule and doesn't touch this ring
   either.
4. **Two neural models that don't use templates at all** — Graph2Edits and
   MEGAN, which predict reactions as direct edits to the molecular graph
   rather than matching known reaction patterns, so in principle they can
   propose things no template library has ever seen. Graph2Edits landed on
   the same non-answer as ASKCOS (another same-ring tautomer, not a real
   cut) and otherwise **independently reconfirmed the exact same peripheral
   step** the first two methods found — three unrelated methods now agree
   on that one move, for what it's worth. **MEGAN did something different
   and genuinely useful:** with very high confidence (>99%, on both the
   bare ring and your full molecule) it proposed hydrolysing the ring open
   — splitting the amidine back into a linear 1,3-diamine and an aryl
   ketone. That's real, chemically sound retrosynthetic logic for this ring
   class, and the first time any of the four methods touched the ring
   itself rather than working around it. But asked to take that idea one
   step further, its confidence collapsed — it doesn't actually know how to
   finish the disconnection into two purchasable pieces either.

**Four architecturally unrelated methods — two template libraries and two
neural models that don't use templates — agree that none of them has ever
seen how this ring is really made.** That's a much stronger statement than
"our software failed." One of them (MEGAN) at least points at a plausible
*shape* for the answer — a 1,3-diamine condensing with an aryl ketone or
aldehyde, the standard way this bicyclic amidine class is built — without
being able to complete it. We don't think more compute or different
settings will change this — the next useful step is chemistry knowledge,
not another automated run.
