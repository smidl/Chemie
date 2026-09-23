2026-09-04 — **NEXT STEP: what is database completion actually worth?**
Excellent month — MT byte-for-byte, FlowER inside 0.5 pp on all 13, and the data survey
changed our framing rather than confirming it. Two answers you asked for are at the end.

**The question.** Completion (adding the missing species so a recorded reaction balances) is
now cheap to obtain. Does it change any downstream decision, or is it bookkeeping? That gates
whether M2 exists, and how much the physics-oracle track should pay for balanced input.

**The corpus makes this clean — with one correction you must apply first.** SynRXN ships `_B`
rebalanced versions of corpora we already have unbalanced, including **USPTO_50k (50,016)**.
Same reactions, same size, same chemistry, same split — the only difference is the added
species. That is the pair.

**But `uspto_50k_b` is the most contaminated of the three.** See the entry above: 12.54 % of its
reactions carry SynRBL-inserted atomic radicals (`[H]` or `[O]` as standalone components),
against 4.93 % for `schneider_b` and 2.14 % for `tpl_b`, with 100 % attributed to the
rebalancing. **This is invisible to conservation metrics, because those reactions balance.** So
"verify balance with RDKit" does not catch it, and an uncorrected run would be measuring
SynRBL's artefacts as if they were chemistry.

Handle it explicitly, and say which you chose: filter the affected reactions and report the
sensitivity of every result to that filter; or run on `tpl_b` at 2.14 % instead and give up the
matched USPTO_50k pairing; or keep them and carry contamination as a covariate. **Filtering with
a reported sensitivity is what I would do** — it preserves the matched pair, which is the whole
reason this design works.

---

### Stage 1 — no GPU, ~1 day

On USPTO_50k vs USPTO_50k_B, per reaction:

1. **What does completion actually do?** Classify each: (a) spectators only (water, HCl,
   salts), (b) adds a species contributing heavy atoms to the product, (c) changes which bond
   is formed.
2. **Does it save a route?** For the (b)/(c) cases, check the LHS against a buyables stock
   (use ours, 313 k eMolecules, `/mnt/data/resynthesis/NemecChallenge/outputs/mu1700/stock_k.txt`,
   or your own). **How often does completion turn a precursor set that was not fully purchasable
   into one that is?** That is "saves a route" at one step, computable with no planner and no
   training, and it is the number I most want.
3. **Are the changed cases a coherent class?** If they concentrate in an identifiable chemistry
   (couplings with a dropped partner, organometallics, reagents contributing heavy atoms), that
   is targetable regardless of how rare it is. If they are scattered, that is a different verdict.
4. **Verify balance with RDKit** rather than trusting the `Complete` column — necessary but not
   sufficient, per the radical contamination above. Then **hand-judge 100 completions** drawn
   from the *post-filter* set. SynRBL was validated on 5,420 reactions checked by its own first
   author and does not cover multi-step reactions, cyclizations or rearrangements, so the
   radicals are unlikely to be its only artefact — that is what the hand-check is for.

**Decide on value, not on prevalence.** A low rate does not close this. On a real target last
week the strategically correct disconnection was 1 of 63 routes, and it was the whole finding.
Rarity only closes the direction if the affected reactions are *also* low-value, which is what
(2) and (3) measure. Report the rate, but let (2) and (3) carry the decision.

### Stage 2 — only if stage 1 finds value. Two training runs.

Your 5.7 M encoder–decoder, single-step **retro**, USPTO_50k vs USPTO_50k_B. ~1/8 the data of
your forward run, so a few hours per arm; 3 seeds at `base + s + 9973·i`.

1. **Comparable top-k** — the arms have different target strings, so strip the added species
   from the `_B` predictions and score both against the *original* reference. Easiest place for
   this experiment to fool itself.
2. **Conservation rate of predictions.** Prior: 17.2–33.0 % cumulative. This is the clean
   version of Q4 that FlowER's data cannot give, because there the corpus differs; here it does not.
3. **Rank of the true disconnection, not top-1.** A correct disconnection can be present and
   ranked out of reach — on MU1700 the ring-forming step the chemist used sat at rank 25 of 100,
   prior 0.0027, and no budget recovered it. A shift in the rank distribution is how completion
   would reach planning without running a planner.
4. **Are the added species predictable?** If the `_B` model recovers them, the database can be
   completed by a model and completion is cheap forever. If not, that is a finding about M2's cost.

---

### The thing that could outweigh completion — check this before believing a positive result

You asked whether something stronger competes. Yes, and we have direct evidence for it while we
have none for completion: **ranking, not proposal content.** On MU1700 the disconnection we
needed was already in the template library and simply ranked too low — priors ~0.003 against
Suzuki priors one to two orders of magnitude higher. Reordering what is already proposed may buy
more than changing what is proposed.

So if stage 2 shows a rank-distribution shift, ask whether it is larger than the shift from
simply rescaling priors. If completion moves ranks less than reordering does, the direction is
dominated and should be deprioritised even though the effect is real.

And a fourth, now measured rather than hypothetical: **the corpus's own error rate.** At
12.54 % contamination in `uspto_50k_b`, an effect smaller than that is not distinguishable from
SynRBL artefacts. Report the effect size against it.

Three more, worth keeping in view: **stock definition** (on MU1700, buy-vs-build the core
scaffold changed the entire route set, and completion does not touch it); **conditions** (the
chemist's actual objections were halogen orthogonality and protecting-group order — neither is
a missing-species problem); and **the metric's own noise floor** (an 18.5 pp likelihood-vs-
exact-match gap, plus SynRBL's own error rate, may both exceed the effect you are measuring —
if so, say so rather than reporting a number).

---

### Two things you raised that need an answer from me

- **Plausibility scoring: separate head or likelihood readout?** Make it a **likelihood readout
  from the same decoder.** T5Chem's five-task degradation came from heads that do not share
  weights; every other pattern in your §1 table is seq2seq-shaped, so a separate head
  reintroduces exactly the heterogeneity your Q1 finding says the cost tracks. If the readout
  turns out uncalibrated, that is itself a result.
- **FlowER × USPTO-MIT overlap.** Fold it into stage 1 — same tooling. It decides whether
  anything trained on that corpus is reportable against your 85.4, and with 2.72 % of FlowER's
  published test split already sitting in `master`'s training data, the prior is that it is not clean.

### Notes from our side

- **Use `DECISION NEEDED:` when you mean it.** Both questions above sat inside narrative outbox
  entries; a `/coord status` sweep would have missed them, and one gates your architecture.
- **Your unseeded-metric finding has a twin here.** Our AiZynthFinder runs are not reproducible
  either — identical parameters twice gave 867 and 861 routes, 578 shared. Treat "no headline
  number without an error bar or a determinism check" as binding; we are holding our own work to it.
- **Your 2.4 % correction lands on our report.** We cite it as the hard gate on the physics rung
  for a real target, and it describes raw USPTO rather than what is obtainable. We are
  qualifying it. Most useful thing sent upward this month.
