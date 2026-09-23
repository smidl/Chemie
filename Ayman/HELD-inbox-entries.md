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
