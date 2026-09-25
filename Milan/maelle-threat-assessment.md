# MAELLE vs AFM — threat assessment for the ICLR 2027 submission

**Date 2026-09-21.** Written after fetching and reading the full preprint.
Pooled: `~/agents/library/nguyen2026_maelle.{pdf,txt,md,bib}` (bib verified against the
arXiv API, not against a search snippet).

**Paper.** Nguyen Xuan-Vu, Octavian Susanu, Daniel Armstrong, Philippe Schwaller (EPFL /
NCCR Catalysis), *Mechanistic Reaction Prediction via Discrete Flow Matching on
Graph-Structured Electron Occupation* (MAELLE), arXiv:2608.27429, v1 27 Aug 2026,
v2 28 Aug 2026. Preprint, no venue.

---

## Verdict first

**Not a novelty kill. One serious threat, one that needs a paragraph, two that are cheap.**
The formal overlap is real and close, but MAELLE resolves the central constraint the
*opposite* way from AFM, and its own footnotes concede the weaker guarantee. Written
correctly, it makes AFM's theorem the organizing result that explains both papers.

The danger is not being scooped. It is being reviewed by someone holding MAELLE's Table 1,
which marks the FlowER family ✗ on "mechanistic-step label-free" and ✗ on "broad coverage",
and having no answer on the page.

---

## 1. What MAELLE actually is

- **State.** Integer occupation vector `o` over a fixed electron-site set: bonding sites
  `e_ij`, lone-pair sites `e_ii`, one pooled hydrogen site per heavy atom. The heavy-atom
  set is preserved and adjacency is read off occupation, `a_ij = 1[o_eij > 0]`.
- **Alphabet, three moves.** `FLOW(e_src → e_snk)` moves one electron pair (conserving);
  **`DEL(e)` removes a pair; `ADD(e)` adds a pair** (both non-conserving).
- **Move recovery.** No elementary-step labels. A **balanced integer Optimal Transport**
  problem over sites yields an unordered move set, with **a virtual sink/source `e_∅`
  added explicitly "to handle reactions where the total electron count is not conserved"**
  (§4.3).
- **Path.** Each move applied independently with probability κ(t); discrete flow matching
  over a CTMC.
- **Benchmark.** USPTO-480K forward product prediction, top-1 **0.872**, below
  Graph2SMILES 0.903 and NERF 0.907, comparable to MEGAN 0.863.
- **OOD.** Two constructed splits of the same corpus: **OOD Mass** (high-MW products held
  out) and **OOD Ester** (non-methyl esterifications held out), plus an IID control.
  Transformation models hold up on OOD Mass where SMILES models decay with molecular
  weight; MAELLE is best on OOD Ester.

---

## 2. The decisive technical fact, and it runs in our favour

**MAELLE does not conserve electrons.** Its own Table 1 footnote reads:

> "§ MAELLE is heavy-atom conservative because protonation and deprotonation are simplified."

`ADD` and `DEL` change the electron count by construction, and `e_∅` exists precisely to
absorb non-conservation. There is **no valence/octet admissibility table and no validity
guarantee** on emitted or intermediate states. The authors call the trajectories
**"pseudo mechanistic"** — their own §4 title.

Against AFM's claim of electron, atom **and proton** conservation of exactly one at every
model size, plus validity as a mask on one softmax class:

| | MAELLE | AFM |
|---|---|---|
| heavy-atom conservation | ✓ by construction | ✓ |
| electron conservation | **✗ — ADD/DEL + virtual reservoir** | ✓ algebraic identity |
| proton / hydrogen conservation | **✗ — "simplified"** | ✓ |
| validity of emitted state | **no guarantee** | ✓ Prop. 2, table-masked |
| impossibility theorem | none | the paper's core result |
| mechanism labels needed | no | yes (FlowER corpus) |

**The framing that turns this into an asset.** Both papers face the same obstruction: a
product measure on the level set of a non-trivial linear functional must be a point mass.
There are exactly two ways out. **MAELLE relaxes the constraint** — add a reservoir so the
state no longer lives on the level set. **AFM keeps the constraint and changes the
elementary event** so the increments cancel identically. Concurrent, independent arrival
at the same obstruction is evidence the theorem matters, and only one of the two papers
states it. Write that paragraph.

---

## 3. Threats, ranked

### T1 — The constructed OOD arm. **HIGH. This is the real one.**

MAELLE builds two OOD splits and reports beating all baselines on both. We measured that
FlowER's released split contains **0.076 %** unseen core arrow patterns (1.91 % at 1-hop),
i.e. it asks for no extrapolation, and concluded an extrapolation test must be
*constructed*. It has not been. A reviewer will ask why the competitor did it and we did
not.

Worse, MAELLE's stated mechanism for its OOD gain is an AFM-style argument made by someone
else: the model "has seen the intermediate graph states of reactions similar to
esterification, such as amide coupling". That is a shared-move-alphabet argument, with
evidence attached.

**Mitigation, and it is mostly already done.** We hold per-test-step novelty bins for all
218,997 test steps (`analysis/results/test_bins_new.tsv.gz`), the signature-novelty scan,
the polar-only retrain arm (§8 of `RESULTS.md`) which is already an extrapolation control
and showed the degradation is *data provenance, not chemistry*, and the RMechDB transfer
result (0 % → 85–90 % on multi-move radical classes from ~3,500 chemist steps). An OOD
section can be assembled from existing artefacts. **Highest-value action.**

### T2 — "Requires elementary-step annotations". **MODERATE-HIGH. Needs a paragraph.**

Table 1 marks FlowER ✗ on label-free and ✗ on broad coverage, footnoted as "covers 86
expert-curated reaction types and requires a mechanistic dataset with imputed elementary
steps". **AFM trains on that corpus and inherits the criticism verbatim.**

**MEASURED 2026-09-21 — the answer is now empirical, see `maelle-ot-recovery-result.md`.**
Their label-free move recovery was reimplemented from §4.3 and Appendix C and run on
12,799 curated polar mechanisms. Its transport objective attains cost **zero in every
reaction**; the chemist's mechanism is optimal in **100 %** of them and uniquely optimal
in **1.9 %**, with a mean of **11.9** distinct optima per reaction (lower bound, 20
re-solves). So the label-free route does not identify a mechanism — it returns an
arbitrary member of a large equivalence class, and that is what their model trains on.
Separately, their pair-valued state cannot represent **5,355 / 5,426** curated radical
steps at all. This converts T2 from a rebuttal into a result.

**The rest of the answer, which must also be on the page.** (i) Our model-free
measurement decomposes **99.73 %** of 17,671 curated steps with *no network*, so the
alphabet is not a property of the corpus. (ii) ~3,500 chemist steps move the radical
sector from 0 % to 85–90 %, so the annotation requirement is small, not large. (iii)
MAELLE's moves are recovered by optimal transport from endpoints and are **never validated
against chemist arrows**. We have that validation: 92.0 % rank-1 agreement with the
chemist on the 624 reactions where the model had a genuine choice. **That discriminator is
ours alone and MAELLE cannot answer it.**

### T3 — ArrowFinder is still uncited. **LOW on novelty, MODERATE on credibility.**

Miller, Dashuta, Rudisill, Van Vranken, Baldi, *JACS* 147(44):41168–41176 (2025),
`10.1021/jacs.5c16838`, pooled. Flagged in `plan.md` on 15 September; the 20–21 September
Overleaf commits did not add it. In a paper citing Kayala & Baldi three times, omitting the
same group's 2025 JACS paper on the same task reads as incomplete.

It also **helps us**: its 101/1331 = **7.6 %** "functionally equivalent but
representationally different" is an *independent* measurement of Limitation (ii), so the
order ambiguity becomes a known, quantified property of the task rather than a weakness we
are conceding. And its 99.55 % recovery is the number our 99.73 % should be stated against.

### T4 — The non-learned enumeration lineage. **LOW. One sentence.**

YARP (Zhao & Savoie, *Nat. Comput. Sci.* 1:479–490, 2021, `10.1038/s43588-021-00101-3`),
Chemoton 2.0 (Unsleber, Grimmel, Reiher, *JCTC* 18:5393–5409, 2022,
`10.1021/acs.jctc.2c00193`), AFIR/GRRM (Maeda, Ohno, Morokuma, *PCCP* 15:3683, 2013,
`10.1039/c3cp44063j`), GSM (Zimmerman, *J. Chem. Phys.* 138, 2013, `10.1063/1.4804162`).
YARP matters most: it enumerates over the bond-electron matrix, our own state object,
without learning. *(Note: "Pathfinder", listed in an earlier note of mine, does not survive
Crossref verification and should not be cited.)*

---

## 4. What is NOT a threat

- **No head-to-head exists.** MAELLE explicitly excludes FlowER and ELECTRO as baselines
  because they cannot be trained on USPTO-480K. Different corpus, different task (forward
  product prediction vs elementary-step mechanism). No number of theirs contradicts any
  number of ours.
- **MAELLE is not state of the art in-distribution.** 0.872 top-1, behind two of its own
  reported baselines.
- **Timing.** v1 is 27 August 2026. Under normal concurrent-work conventions a submission
  is not obliged to beat something posted weeks before the deadline. Citing and contrasting
  is sufficient — *not* citing is what costs.

---

## 5. Recommended actions, in order

1. **Add the OOD section** from existing artefacts (T1). Largest reviewer-facing gain.
2. **Write the two-ways-out-of-one-obstruction paragraph** (§2) and cite MAELLE as
   concurrent work. Turns the competitor into support for the theorem.
3. **Write the annotation-cost rebuttal** (T2), leading with 99.73 % model-free coverage
   and the 92.0 % chemist agreement.
4. **Cite ArrowFinder** and use its 7.6 % to support Limitation (ii) (T3).
5. **One sentence** on the enumeration lineage (T4).

Items 2–5 are writing, not experiments. Item 1 is analysis on data already on disk.
