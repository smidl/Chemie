#!/bin/bash
#SBATCH --job-name=res_afm_nano
#SBATCH --partition=main
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --output=/data/smidl/ArrowFlowMatching/logs/%x-%j.log
set -e
cd $HOME/Public/ArrowFlowMatching
export CUDA_VISIBLE_DEVICES=1 PYTHONPATH=. PYTORCH_ALLOC_CONF=expandable_segments:True
D=/data/smidl/ArrowFlowMatching
.venv/bin/python resonance_rescore.py --model afm --name afm_nano \
  --ckpt $D/outputs/runs/afm_nano/checkpoints/best.ckpt \
  --files $D/outputs/strata/test_m6plus.txt $D/outputs/strata/test_cyclic.txt $D/outputs/strata/test_m2.txt \
  --limit 3000 --samples 10 --batch 2 --max_atoms 120 \
  --out $D/outputs/resonance_rescore_capped_afm_nano.json
