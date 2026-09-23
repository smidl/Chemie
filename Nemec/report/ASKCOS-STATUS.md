# ASKCOS on RCI — Path A (HTTP services), status 2026-09-04

**Result so far: viable, and the hard part is done.** ASKCOS's one-step
retrosynthesis model is running on RCI and answering queries about MU1700.

## What was established

| question | answer |
|---|---|
| Has ASKCOS been run in this project before? | **Yes.** `data/2-raw/askcos/` holds results for 6 benchmark sets, 190/190 targets at ~30 s each, produced 2025-12-04 by a pipeline called **`retrocast`** (`scripts/askcos/1-run-askcos.py`) against `http://0.0.0.0:9321/get_buyable_paths` |
| Which planner was that? | Port 9321 = **`tree_search_retro_star`** — the Retro\* controller, from `module_config_retro_minimal.py`. Not MCTS (that is 9311) |
| Where is `retrocast`? | **Not found** on RCI, in `$HOME`, or in `~/AIC` / `~/agents`. Unknown provenance — worth asking whoever ran it |
| Is the code public? | **Yes.** `askcos2_core` and all 34 modules in the minimal-retro config clone anonymously over HTTPS from `gitlab.com/mlpds_mit/askcosv2/...` |
| Are prebuilt images available? | **No.** `ASKCOS_REGISTRY` is a *push* target; the registry has no tags for `app`, `celery`, `retro/template_relevance`, `tree_search/retro_star`, `value_network` |
| Can we build images on RCI? | **No.** No Docker daemon (`Cannot connect to the Docker daemon`), and `singularity build --fakeroot` fails — no `/etc/subuid` mapping for `smidlva1`. Singularity 3.8.7 can *pull and run*, not build |
| Are the trained models gated? | **Partly.** `cas`, `reaxys`, `reaxys_biocatalysis`, `pistachio`, `pistachio_ringbreaker`, `bkms_metabolic` need `DROPBOX_ACCESS_TOKEN` + `DROPBOX_LINK_PASSWORD` (MLPDS membership). **`uspto_higher_level` is ungated** and downloads with plain `wget` |

## The route taken: skip containers entirely

Each module ships a `singularity_cpu.def` whose `%post` is nothing but conda and
pip installs. That is a dependency spec, not a container requirement — so the
services can be installed **natively**, which sidesteps the fakeroot blocker.

Done:
- `/mnt/data/resynthesis/askcos2_core` — core repo cloned (public, current `main`)
- `/mnt/data/resynthesis/askcos_mods/{template_relevance,expand_one,retro_star,value_network}` — the four modules the minimal retro config needs
- `template_relevance/mars/uspto_higher_level.mar` — **756 MB, ungated USPTO model**
- conda env **`askcos_tr`** built to the module's own spec: python 3.8.20, rdkit 2020.09.5, openjdk 11, pytorch 1.12.1 (cpu), rdchiral_cpp 1.1.2, torchserve 0.3.1
- **Service verified working** (SLURM job 11483880): torchserve serves the model on
  9410/9411 and returns templates for MU1700 and for Němec's compound 4.
- `retro_star/saved_models/best_epoch_final_4.pt` — Retro\*'s value network is
  bundled in-repo, no download needed.

### What it returns — and why it matters to us

Top-2 disconnections for MU1700, with **literature precedent counts**:

| template | score | `num_examples` |
|---|---|---|
| carbamate / N–H on the piperazine | 0.656 | **22,059** |
| biaryl (Suzuki) coupling | 0.337 | **35,278** |

Same chemistry family AiZynthFinder proposes, but each template carries its
precedent count. That is exactly the signal our own pipeline throws away —
`avg_template_occurrence` reads 0.000 for all 63 routes because CLOVER discards
template metadata. **ASKCOS supplies it natively.**

## What remains

1. Build two more conda envs from `retro_star/singularity_cpu.def` (python 3.10.12,
   fastapi, uvicorn, pymongo, redis — spec already read) and the `expand_one`
   equivalent.
2. Start the chain: `template_relevance` (9410) → `expand_one` → `retro_star` (9321).
3. `grep` finds **no mongo/redis usage in `expand_one/*.py` or `retro_star/*.py`**,
   so the buyables source is likely supplied per request rather than via a seeded
   database — needs confirming, and it is the main remaining unknown.
4. Point a client at `:9321/get_buyable_paths` with MU1700 and our 313k stock.

## Caveats
- Only the **USPTO** model is available to us. ASKCOS's headline performance is
  usually quoted with Reaxys/Pistachio models, which we cannot legally obtain
  without MLPDS membership. Any comparison must say which model set was used.
- Licence: `askcos2_core` is MIT-licensed; the Reaxys-derived model carries
  CC-BY-NC 4.0 (`LICENSE_REAXYS_MODEL`). We are using neither.
- Everything above ran on `cpufast`; no GPU needed for the CPU model.
