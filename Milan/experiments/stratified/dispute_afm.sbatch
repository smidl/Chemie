#!/bin/bash
#SBATCH --job-name=disp_afm
#SBATCH --partition=main
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --output=/data/smidl/ArrowFlowMatching/logs/%x-%j.log
# Splits the 0.89-nat margin at six or more moves into an ORDER component (same
# product, different route -- Limitation (ii), harmless) and a PRODUCT component
# (different chemistry), and dumps the small disputed cases for drawing.
set -e
cd $HOME/Public/ArrowFlowMatching
export CUDA_VISIBLE_DEVICES=1 PYTHONPATH=. PYTORCH_ALLOC_CONF=expandable_segments:True
D=/data/smidl/ArrowFlowMatching
.venv/bin/python strata_dispute.py \
  --ckpt $D/outputs/runs/afm_nano/checkpoints/best.ckpt \
  --files $D/outputs/strata/test_m2.txt $D/outputs/strata/test_m3to5.txt \
          $D/outputs/strata/test_m6plus.txt $D/outputs/strata/test_cyclic.txt \
  --limit 300 --width 10 --max_atoms_dump 40 \
  --out $D/outputs/strata_dispute_afm.json
