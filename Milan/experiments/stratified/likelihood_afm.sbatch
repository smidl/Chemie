#!/bin/bash
#SBATCH --job-name=lik_afm
#SBATCH --partition=main
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --output=/data/smidl/ArrowFlowMatching/logs/%x-%j.log
# Rank-free: teacher-force the recorded step's own move sequence and compare its
# trajectory log-probability with the model's best sampled one. Neither number
# is produced by a ranking rule, so this separates "the model prefers other
# chemistry on long steps" from "the ranking rule buries the right answer".
set -e
cd $HOME/Public/ArrowFlowMatching
export CUDA_VISIBLE_DEVICES=1 PYTHONPATH=. PYTORCH_ALLOC_CONF=expandable_segments:True
D=/data/smidl/ArrowFlowMatching
.venv/bin/python strata_likelihood.py \
  --ckpt $D/outputs/runs/afm_nano/checkpoints/best.ckpt \
  --files $D/outputs/strata/test_m1.txt $D/outputs/strata/test_m2.txt \
          $D/outputs/strata/test_m3to5.txt $D/outputs/strata/test_m6plus.txt \
          $D/outputs/strata/test_cyclic.txt \
  --limit 800 --width 10 --batch 8 \
  --out $D/outputs/strata_likelihood_afm.json
