#!/bin/bash
#SBATCH --job-name=strat_flower_discrete_nano
#SBATCH --partition=main
#SBATCH --cpus-per-task=8
#SBATCH --mem=48G
#SBATCH --output=/data/smidl/ArrowFlowMatching/logs/%x-%j.log
# Stratified evaluation: the released nano checkpoints on strata of the test
# split cut by how many moves a step needs (analysis/concertedness.py).
# The three flow models share one body, one featurisation and one width, so the
# elementary event is the only variable between them -- which is what makes the
# trend across strata a measurement of Theorem 1's cost rather than of capacity.
set -e
cd $HOME/Public/ArrowFlowMatching
export CUDA_VISIBLE_DEVICES=1 PYTHONPATH=. PYTORCH_ALLOC_CONF=expandable_segments:True
D=/data/smidl/ArrowFlowMatching
MODEL=flower_discrete
NAME=flower_discrete_nano
BATCH=16
for S in test_cyclic test_m1 test_m2 test_m3to5 test_m6plus; do
  echo "=== $NAME $S"
  # compat_flower_cons aliases the pre-rename module names the supplied
  # checkpoints pickle; it must be imported before Lightning restores them.
  .venv/bin/python -c "
import compat_flower_cons, runpy, sys
sys.argv = ['eval.py', 'model=$MODEL', 'model_name=$NAME',
            'model.decode=sample', 'model.ranking=frequency',
            'model.emb_dim=128', 'model.enc_filter_size=512',
            'data.root=$D/outputs/strata', 'data.eval_split=$S', 'data.test_limit=6000',
            'rollout_pathways=50', 'eval_batch_size=$BATCH', 'num_workers=8',
            'ckpt_path=$D/outputs/runs/$NAME/checkpoints/best.ckpt',
            'outputs_dir=$D/outputs_strata/$S']
runpy.run_path('eval.py', run_name='__main__')
"
done
