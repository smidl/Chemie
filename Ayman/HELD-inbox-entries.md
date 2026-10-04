# Held — inbox entries for `retro-activelearning`, not yet sent

Outside the student's repository on purpose. Entries below are written and ready; each
carries the condition under which it gets pasted into
`retro-activelearning/coordination/inbox.md` and committed there.

**Why hold anything.** Phase 0 of the learning plan is that he reproduces the oracle ladder
himself. Handing him the answer first removes the exercise and teaches him to trust a table
instead of a measurement, which is the opposite of what this project needs.

---

## HELD-01 — the ladder's bottom rung

**Release when:** TASK 01 is delivered, i.e. the four deliverables of
`coordination/TASK-01-cyanohydrin.md` are in his repo and the control passed.
**Then:** paste the block below into his `coordination/inbox.md` as a dated entry and commit.

**Do not release early.** TASK 01 Part A item 5 asks him to work out what the missing error
column would take to measure. This entry is that column. Releasing it first turns the task
into reading comprehension.

> ### 2026-09-21 — the ladder's bottom rung, measured
>
> Run on the supervisor's side while you were working, so you have something to check your
> own Phase 0 against rather than a blank page. GFN2-xTB on all 449 BH9 systems at the
> reference geometries, separated-reactant referencing (job 11680758; script and raw output
> at `/mnt/data/resynthesis/admissibility/bh9_xtb/`).
>
> | rung | cost | forward barrier MAE |
> |---|---|---|
> | GFN2-xTB | seconds | **14.40** |
> | AIMNet2, general | ~43 s | 16.70 |
> | AIMNet2, domain-routed | ~43 s | 4.73 (in-sample) |
>
> **What it means for your project.** The two cheapest rungs are not distinguishable on
> barriers, so the ladder has a step that buys nothing. The gain comes from *routing* by
> domain rather than from paying for a more expensive method, which moves your question
> from "which rung do I buy" toward "which domain am I in, and is my model valid there".
> That is closer to reducible error, which is the thesis.
>
> Reaction energies rank the rungs differently (xTB 10.11 against 2.88 routed), so a policy
> has to be per-quantity. Multi-fragment reactants cost 53 % more error than single-fragment
> ones (16.88 against 11.04) — which you will have met directly in TASK 01.
>
> **Not to be taken on trust.** Single run, unreviewed, energies at reference geometries so
> geometry error is excluded by construction. Where your numbers disagree with these, say so.

---

## HELD-02 — introduction to the Zhong/retro-pfn work — RELEASED 2026-09-23

Pasted into `retro-activelearning/coordination/inbox.md` and committed there. Kept below for
provenance only.

**Release when:** the owner personally introduces Aymen to `retro-pfn`. Not gated on a task —
this is orientation, not an exercise. Hand him exactly this; do not point him at the repo itself
first, it will overwhelm him — `retro-pfn` is a large, multi-track leaf and almost none of it is
relevant to this entry point.

**Owner prerequisite, before release — not part of the message to him:** none outstanding —
confirmed 2026-09-23 that Aymen already has RCI `resynthesis` group access and a GitHub
collaborator grant on `aicenter/retro-pfn`.

**Then:** paste the block below wherever he'll actually read it (email/inbox), and separately
commit it as a dated entry in `retro-activelearning/coordination/inbox.md`.

> ### Starting point: Zhong 2025 and reaction-feasibility uncertainty
>
> The Zhong paper is a very good start. We've tested it ourselves inside `retro-pfn`, but only
> partially — there's a well-defined, unfinished piece of it that's a good fit for you.
>
> The test is taken from Zhong's own released code (`Chemlex-AI/bayesian-reactivity-prediction`):
> a reaction-feasibility classifier (does this reaction work — yes/no) trained on their Suzuki
> HTE data, and it measures how much better you can spend a fixed labelling budget by choosing
> *which* reactions to label next using the model's own uncertainty, instead of picking at
> random. Feasibility here is a proxy metric — it's the same quantity ("how likely is this
> reaction to work") that will later feed a planner's route search, but for now the required
> output is just the classifier-plus-acquisition comparison, nothing planner-shaped yet.
>
> We ran two of their five uncertainty methods: their `Ensemble`, and their `MCDropout`.
> MCDropout is a cheap, approximate way of getting a model's uncertainty (basically: leave a bit
> of randomness turned on at prediction time and see how much the answer wobbles). It's fast, but
> it's a rough stand-in for a real Bayesian posterior. Their actual best-performing model,
> `BNN-NUTS`, is a properly Bayesian neural network, and their strongest claims about uncertainty
> rest on *that* model — which nobody on our side has run yet. Our MCDropout run got a result
> that contradicts their headline claim; whether that's because MCDropout is too weak an
> estimator, or because the claim doesn't hold up, is exactly the open question.
>
> A very interesting experiment on your side: finish what we started — run their `BNN-NUTS`
> (and, if time allows, `BNN-SVI` and `DKL-GP`) through the same comparison — and then set that
> against a genuinely different way of handling uncertainty: retro-fallback's. Read **only** the
> part of the retro-fallback paper that defines its uncertainty model and its evaluation metric
> ("New evaluation metric: SSP") — stop there, before the section that turns it into a search
> algorithm; that part belongs to a different project. Retro-fallback doesn't try to get a good
> uncertainty estimate at all — it assumes you'll never fully trust one, and asks what to *do*
> given that. Comparing "get a better estimate" (Zhong's BNNs) against "plan around not trusting
> the estimate" (retro-fallback) is the comparison we want out of this.
>
> Three things to read, in this order, and nothing else yet:
> 1. Zhong et al. 2025 — you already have it.
> 2. Retro-fallback (Tripp et al. 2024) — the SSP section only, as above.
> 3. Two short internal notes so you're not rediscovering this from scratch: the entries dated
>    2026-06-17 and 2026-06-18 in `retro-pfn/coordination/outbox.md`, and
>    `retro-pfn/docs/mechanistic/tvoi_surrogate_results.md`. They show exactly what we ran, what
>    it found, and where it flipped.
>
> That's the reading list for now. Everything else about `retro-pfn` — the barrier/DFT side of
> the program — is a different track; ignore it until it's relevant.
>
> ### Compute: where the checkout is, and how to behave there
>
> All of this runs on RCI (the CTU cluster), not your laptop. Log in to `login3.rci.cvut.cz`
> (that's the login node our own setup was verified on — `login2` can have different module
> versions, don't mix them). Shared storage for this whole program is
> `/mnt/data/resynthesis/`, and the existing working checkout of `retro-pfn` there is
> `/mnt/data/resynthesis/retro-pfn` — **that one is mine, with work in progress on `main`, so
> don't touch it.** Make your own clone next to it, at `/mnt/data/resynthesis/retro-pfn-aymen/`,
> and immediately create and check out your own branch there (`aymen/bnn-comparison` or similar
> — your call on the exact name). Do all your work on that branch.
>
> **On the venv — reuse, don't rebuild, until you need to add something.** There's already a
> working `.venv` at `/mnt/data/resynthesis/retro-pfn/.venv/` with everything the MCDropout
> reproduction needed. For your first step — rerunning that reproduction yourself as a sanity
> check — just use it directly, `/mnt/data/resynthesis/retro-pfn/.venv/bin/python`, no setup at
> all. Do **not** `pip`/`uv install` anything into it, though — it's shared with my own active
> runs on `main` right now, and BNN-NUTS/BNN-SVI will need packages (likely a jax/numpyro stack)
> that MCDropout never needed, which risks a version clash with what's already pinned there for
> other work. The moment you need a new package: copy it instead of touching it —
> `uv venv --python "$(which python3)" .venv` (after `module load
> Python/3.11.5-GCCcore-13.2.0`) in your own checkout, then `uv pip install -r
> xif/requirements.txt` to match what's already proven to work — this reuses the same package
> cache on the same filesystem, so it costs seconds, not a real rebuild. Add whatever BNN-NUTS
> needs on top of *that* copy, freely.
>
> A few other things that will cost you a day each if you hit them cold:
> - `source /etc/profile` **before** any `module load` — skip it and the load silently no-ops,
>   then you get a confusing `libpython3.11.so.1.0: cannot open shared object file` later.
> - GPU nodes have **no `module` command at all**. Capture `LD_LIBRARY_PATH` on the login node
>   after loading modules there, then hardcode it in your GPU job script.
> - **Torch/JAX version must match the node's driver**, and Zhong's repo pins old versions —
>   this bit us running their MCDropout, expect it to bite again for BNN-NUTS/BNN-SVI. Check
>   `torch.version.cuda` (or the JAX equivalent) against the node before submitting, don't just
>   trust `pip install`.
> - Never run training on the login node — always `sbatch` (or `salloc` for a quick interactive
>   check). And before launching anything with many jobs at once, run `squeue -u <you>` and check
>   in — the per-user submit budget is shared across the whole program, and a big array from you
>   can silently block someone else's job with no error message pointing at why.
>
> Full reference for all of this (partitions, GPU inventory, job-script templates): ask for
> `~/agents/compute/rci.md` — it's the machine-wide reference, not retro-pfn-specific.
>
> **Committing your results:** yes, to `retro-pfn` — that's where the harness and the existing
> Zhong-repro results already live, and where this comparison belongs. Keep it all on your
> branch, never `main`. Follow the existing convention in `xif/results/`: small result summaries
> (JSON tables, plots) get committed; raw model checkpoints and full logs stay on RCI's
> `/mnt/data/resynthesis/` and are not pushed. Put your results under a clearly-named new folder
> (e.g. `xif/results/aymen_bnn/`) rather than inside the existing `zhong_repro/` one, so nothing
> you write collides with or overwrites what's already there. When you think it's ready, flag it
> — I'll review before anything of yours touches `main`.

---

## Provenance

Full numbers and caveats: `WORKING-reducible-noise.md` §3 in this folder. Raw output and the
script stay on the cluster at `/mnt/data/resynthesis/admissibility/bh9_xtb/`; nothing about
this measurement lives in the student's repository until release.

---

## HELD-03 — review of the MCDropout baseline; margin before NUTS — RELEASED 2026-10-04

Pasted into `retro-activelearning/coordination/inbox.md` and committed there, in full (both
judgment calls kept: the closing direction paragraph and the correction about the bad
directions). Kept below for provenance only.

**Also needs doing separately (not part of this message):** `retro-pfn`'s own
`docs/mechanistic/tvoi_surrogate_results.md` still reports the 06-18 REVERSAL without the
undertraining caveat and still names "run their BNN" as the definitive test. Both are now
superseded.

> ### 2026-10-04 — review: the budget control lands, and it changes what to run next
>
> This is good work, and the part that makes it good is not the headline. It is that you logged
> per-round diagnostics *before* you needed them, so when epistemic behaved oddly you could
> diagnose it instead of speculating; that you killed the competing explanation (the 3-decimal
> rounding) by measuring ties at the k-th score rather than arguing about it; and that seed 7
> collapsing at 30 epochs and being your *best* seed at 100 is a within-seed demonstration, which
> is worth more than any between-condition mean. Committing the baseline for review before
> spending NUTS time was also the right call.
>
> I re-derived your collapse number independently: a constant all-positive predictor at this
> split's 0.655 positive rate scores F1-macro 0.39577, against the 0.39573 you observe. That
> diagnosis is confirmed, not merely plausible.
>
> **Your decision request: yes, run at the 100-epoch-equivalent setting, not the released 30.**
> Your own evidence makes 30 epochs indefensible as a comparison point. But do not run BNN-NUTS
> next — see below.
>
> #### Run a margin baseline first, and mind one detail that decides whether it is worth running
>
> Your result is that with a trained model the *irreducible* component carries the whole benefit
> (aleatoric +0.029) while the *reducible* one is worth nothing (epistemic −0.001). That is
> backwards from theory, which says a label only buys you something where uncertainty is
> reducible. There are two explanations and they are not yet separated:
>
> 1. **MCDropout's epistemic estimator is degenerate.** Your own diagnostics support this: at 100
>    epochs its `score_zero_frac` averages 0.110 and peaks at 0.443, against 0.001 for aleatoric.
>    It assigns literally zero to a large and swinging share of the pool, so it cannot rank there.
> 2. **The decomposition is decorative on a binary task.** High aleatoric entropy on a binary
>    problem just means proximity to p = 0.5 — the decision boundary. If so, "aleatoric wins" is
>    really "margin sampling wins" and the reducible/irreducible labels explain nothing.
>
> Explanation 2 threatens the whole question and costs almost nothing to test, whereas NUTS is
> expensive and *presupposes* the decomposition is meaningful. So: add a margin policy to your
> existing loop, same seeds and budget.
>
> **The detail that matters:** for binary classification, predictive entropy H(p̄) is a strictly
> monotone function of |p̄ − 0.5|. So margin computed on your MC-averaged prediction is the
> *identical ranking* to predictive-entropy acquisition and would test nothing. The baseline has
> to be a **single deterministic forward pass with dropout off**. That version isolates the real
> question: does averaging 100 stochastic passes and decomposing them buy anything over a plain
> softmax?
>
> If deterministic margin lands near +0.031, the honest conclusion is that none of the Bayesian
> machinery earns its cost *for acquisition* on this task. That is a stronger result than
> "epistemic fails," because it goes at the paper's headline rather than one of its arms. It
> would not say anything about their other uses of uncertainty (OOD detection, robustness
> scoring) — keep that scope limit explicit when you write it up.
>
> Worth knowing: **Zhong has no such baseline.** Their AL experiment is four arms — random,
> predictive, epistemic, aleatoric — and random is the only non-uncertainty comparator. Also note
> their reported ordering is *inverted* relative to yours: the paper says predictive and
> epistemic "significantly outperform the method based on aleatoric uncertainty," where you
> measure predictive ≈ aleatoric ≫ epistemic ≈ random. Their figure is on their wetlab stratified
> splits and yours is Suzuki `k_fold_0`, so this is not yet a contradiction — but it is the
> sharpest open discrepancy you have, and worth stating plainly in the README.
>
> #### Two corrections to what I sent you on 09-23 — my error, not yours
>
> 1. **The 06-18 loop does exist on RCI**, at `/mnt/data/resynthesis/zhong-reactivity/` —
>    `zhong_al.py`, `run_al.sbatch`, `run_al_aleatoric.sbatch`, its own `.venv`, and four curves
>    in `results/al_{random,predictive,aleatoric,epistemic}.json` from 06-18. My note sent you to
>    `retro-pfn/.venv` and never mentioned it, which is why you reconstructed from prose. Your
>    reconstruction landing within 0.02 on three of four policies is arguably *better* evidence
>    than a re-run would have been, so this costs you nothing scientifically — but please
>    cross-check your curves against those four JSONs now that you know they are there.
> 2. **The venv and requirements I pointed you at were the wrong ones**, and my claim that
>    BNN-NUTS "will need packages MCDropout never needed" was wrong: `numpyro 0.11.0` and
>    `pyro_ppl 1.8.4` are already pinned in `zhong-reactivity/requirements.txt`.
>
> #### Environment — read before the NUTS run
>
> You ran Python 3.12 / torch 2.7.1 / pyro-ppl 1.9.1 / drfp 0.3.7. The original pins are torch
> 1.13.1+cu117, pyro_ppl 1.8.4, **jax 0.4.8, jaxlib 0.4.7+cuda11.cudnn82, numpyro 0.11.0**, drfp
> 0.3.2, numpy 1.23.4, sklearn 1.1.3.
>
> - For torch-only MCDropout the drift is probably tolerable, but it belongs in your write-up as
>   a caveat on the comparison rather than going unmentioned.
> - **One candidate for your residual deltas:** you regenerated the DRFP features with drfp 0.3.7
>   and the original used 0.3.2. Different fingerprints would shift every arm slightly, which is
>   the right shape for the −0.007 / −0.019 / −0.014 you see. Cheap to check by regenerating under
>   the pinned version.
> - For the jax/numpyro path, do not fight the version gap — jax 0.4.8 is old enough that the API
>   has moved substantially. Use the pinned environment in `zhong-reactivity/` rather than
>   porting their sampler forward.
>
> #### Two places the write-up outruns the data
>
> 1. Your bold headline says the acquisition advantage "shrinks as the baseline is trained
>    properly." I ran it: +0.043 against +0.031 is a difference of 0.012 with SE 0.0087, t = 1.37
>    at n = 5–6. Not established. Your *Open* section states this correctly, so the two sections
>    disagree with each other — demote the headline or add seeds, but do not leave both standing.
> 2. "Random is still improving at 200 epochs" rests on n = 2 of a single policy, and it carries
>    real weight in your argument. Flag it as provisional or fill the cell.
>
> Neither is a criticism of the finding. The epistemic result is solid and I would defend it; it
> is the *second* claim, the one about the advantage shrinking, that is currently the fragile one
> — and it happens to be the more consequential of the two for this programme, which is exactly
> why it needs the seeds.
>
> #### Process
>
> Your decision request was in the branch README. Status sweeps grep `coordination/outbox.md` for
> `DECISION NEEDED:` on its own line, so as written it was invisible to the mechanism — I found it
> by reading your branch. Put future ones in the outbox; the README is the right place for the
> science, the outbox is the channel for anything you need an answer on.
>
> #### One thing to be aware of, not to act on yet
>
> Your finding has a structural consequence worth naming: this dataset has no *reduction* axis at
> all — no ladder, no escalation, nothing that makes error go away by paying more. The epistemic
> term is the only reducible quantity in play and it measures zero. That is informative rather
> than disappointing, but it bears on where the thesis goes after this baseline closes. Let us
> talk it through rather than settle it over the inbox.
