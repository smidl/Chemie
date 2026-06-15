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
