#!/bin/bash
#SBATCH --job-name=exact_afm
#SBATCH --partition=main
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --output=/data/smidl/ArrowFlowMatching/logs/%x-%j.log
# Fix A -- the paper's own extension: rank by the exact product likelihood,
# summed over every admissible order of a move multiset, instead of by one
# trajectory's score.
set -e
cd $HOME/Public/ArrowFlowMatching
export CUDA_VISIBLE_DEVICES=0 PYTHONPATH=. PYTORCH_ALLOC_CONF=expandable_segments:True
D=/data/smidl/ArrowFlowMatching
.venv/bin/python strata_exact_likelihood.py \
  --ckpt $D/outputs/runs/afm_nano/checkpoints/best.ckpt \
  --files $D/outputs/strata/test_m6plus.txt $D/outputs/strata/test_cyclic.txt \
          $D/outputs/strata/test_m3to5.txt $D/outputs/strata/test_m2.txt \
  --limit 200 --width 20 --max_m 10 --top_candidates 5 \
  --out $D/outputs/strata_exact_afm.json
