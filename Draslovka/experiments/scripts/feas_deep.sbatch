#!/bin/bash
#SBATCH -J drasfeasd
#SBATCH -p cpufast
#SBATCH -t 1:00:00
#SBATCH -c 4
#SBATCH --mem=8G
#SBATCH -o /mnt/data/resynthesis/draslovka/feasdeep_%j.log
export HF_HOME=/mnt/data/resynthesis/hf_cache
cd /mnt/data/resynthesis/draslovka
V=/mnt/data/resynthesis/rxnt5_venv
echo "=== deep L* routes ==="
$V/bin/python scripts/draslovka_feas_deep.py --routes out/deep_lstar.json    --out out/feas_deep_lstar.json
echo "=== deep standard routes ==="
$V/bin/python scripts/draslovka_feas_deep.py --routes out/deep_standard.json --out out/feas_deep_standard.json
echo DONE_FEASDEEP
