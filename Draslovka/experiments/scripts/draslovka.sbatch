#!/bin/bash
#SBATCH -J draslovka
#SBATCH -p cpufast
#SBATCH -t 4:00:00
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -o draslovka_%j.log
set -e
cd /mnt/data/resynthesis/repro/SEEA_star/Retrosynthesis
PY=/home/smidlva1/.conda/envs/seea/bin/python
mkdir -p draslovka_out
echo "=== ARM 1: standard (Retro* + value net) ==="
$PY draslovka_eval.py --arm standard_valuenet --ckpt saved_model/best_epoch.pt   --candidate_size 1000000 --out draslovka_out/standard.json
echo "=== ARM 2: ours (Retro* + L*) ==="
$PY draslovka_eval.py --arm ours_lstar_retro --ckpt saved_model/lstar_broad.pt   --candidate_size 1000000 --out draslovka_out/lstar_retro.json
echo "=== ARM 3: ours-best (SeeA* + L*) ==="
$PY draslovka_eval.py --arm ours_lstar_seea  --ckpt saved_model/lstar_broad.pt   --candidate_size 50      --out draslovka_out/lstar_seea.json
echo ALL_DONE
