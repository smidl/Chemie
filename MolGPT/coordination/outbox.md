# Outbox — MolGPT (leaf)

Append-only, skimmable. Outward-relevant state the Chemie orchestrator pulls on
`status`. One line per entry: `YYYY-MM-DD — summary`.

2026-06-15 — Coordination channel established (flat structure). Role accepted into
inbox: candidate-proposer (T3) in the active-acquisition loop — in-context reaction
generator. Current state: MolPFN = in-context molecule generation (mid-debug);
re-point to reactions is expansion-phase, not started.
2026-06-18 — IN-CONTEXT SOTA CONSOLIDATED (literature/sota.md + references.md). The ICL
search was real but distributed (pool + synthesis §ICL) & molecule-centric; now consolidated
node-local and reframed for GENERATIVE REACTION modeling, with 2023–25 reaction top-ups pooled
(reactiont5, qiang2023 rxn-pretrain→gen, batgpt-chem, lin2025 dual-task). Verdict: broad ideas
taken (Bio-xLSTM=in-context chem sequences; FusionRetro=in-context retro; ChemLLMBench=frozen-LLM
ICL; ReactionT5/Molecular Transformer=generative-not-in-context). Surviving slice = a TRAINED
in-context reaction proposer (support set=disconnection exemplars) with structured output + σ/
frontier conditioning, loop-coupled to ξ_f. Decisive test stays the context-redundancy ablation
recast for reactions (does the context set add signal beyond the conditioning token?).
