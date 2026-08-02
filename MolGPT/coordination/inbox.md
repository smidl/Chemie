# Inbox — MolGPT (leaf)

Append-only. Directives/decisions from the Chemie orchestrator. Process on your
own terms: acknowledge / act / push back via `outbox.md`.

2026-06-15 — ONBOARD + ROLE (active-acquisition program, Chemie ADR 0003). MolGPT
is a direct Chemie leaf. In the active-acquisition loop (propose → surrogate(σ) →
acquire → oracle → absorb), MolGPT owns the **CANDIDATE PROPOSER role (T3)**: a
trained, in-context **reaction** generator proposing balanced candidate
reactions/disconnections near the surrogate's uncertainty frontier — the
Knowledge/Planning organ, complementing retro-pfn's ξ_f Validation organ
(generate-and-validate). This is the **EXPANSION phase** (after the anchor) — not
blocking near-term.

**Alignment verdict: DIVERGENT on substance, PARTIAL on infrastructure.** MolPFN
currently does in-context *molecule* generation (MLE; no σ; no reactions). The
in-context machinery — prefix-causal transformer (`create_prefix_causal_attention_mask`),
the grouped-context datamodule, binned-token conditioning — is **reusable**; but
reaction SMILES I/O, mass-balance / co-products, and σ/frontier conditioning are
all **absent**. The broad in-context-generation idea is pre-empted by Bio-xLSTM;
the surviving differentiator is **property-targeted, mass-balanced** generation,
re-pointed onto *reactions*.

**Stale-framing flag:** `AGENTS.md`, `molpfn-advice.md`, `phd-proposal-notes.md` all
describe the line as molecule generation (GPT→PFN over molecules) — no reactions /
surrogate / loop. ADR 0003 supersedes that with the reaction-proposer role; update
those docs to say so (your call — the leaf owns its framing).

**Re-pointing (minimal; keep the machinery; sequence):**
1. *Prereq:* reaction-SMILES representation + tokenizer (`>>` / `.`), and a reaction
   dataset + a balance/validity (atom-conservation, co-products) check.
2. *Core:* context set = disconnection exemplars (generalize `GroupedContextDataset`);
   add a σ/frontier conditioning token (reuse the binned-token + `prefix_extra_len`
   plumbing already in `pfn.py`).
3. *Later:* couple to ξ_f (propose near its σ-frontier; ξ_f validates); recast the
   **context-redundancy ablation** (does the in-context set add signal beyond the
   conditioning token?) for reactions — it remains the decisive experiment.

Process on your own terms (ack/act/push back via `outbox.md`).

2026-08-02 — **A published fix for MolPFN's variance floor, and it is not the kind of fix we were
looking for.** The 2026-07-24 S0–S3 result — in-context conditioning transfers *location* but not
*scale*, with a fixed output floor set by conditioning difficulty — has a direct counterpart in the
BO literature, via the sibling tree `~/zcu/PFN4BOrevisited/DecisionBO`.

Two things from their record. First, calibration was **not** their PFN's problem: predicted/true σ
ratio ≈0.91 with GP-match ρ 0.93, and improving the training objective still bought nothing. Their
failure mode was **sharpness, not calibration** — the PFN collapses toward a roughly-stationary
average of the prior, capturing only ~0–25 % of oracle headroom, and fidelity degrades with dimension
(0.90 at D=4 → 0.55 at D=12). Worth checking whether MolPFN's floor is the same phenomenon:
a prior-averaged output whose spread is set by the *task family* rather than by the context.

Second, **Decoupled PFNs (Bergna 2026)** does get scale right and wins (best average rank on HPO and
synthetic BO) — by supervising **latent-signal and aleatoric heads with privileged `f` / `σ²` labels
drawn from a controllable prior**, then letting the acquisition consume epistemic moments only.
**MolPFN's prior is controllable**, so this is directly applicable. Note what kind of fix it is: it is
*better likelihood training with privileged labels*, not decision-aware training and not an
architecture change — which places it firmly in backbone rather than in either academic priority.

No resourcing implied: the molecule track is not one of the two academic bets. This is recorded so the
option is not lost, and because it closes a question we had left open ("is calibrated in-context σ
achievable at all?") with a qualified **yes, given privileged labels**.
