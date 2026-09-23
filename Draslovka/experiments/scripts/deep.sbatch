#!/bin/bash
#SBATCH -J drasdeep
#SBATCH -p cpufast
#SBATCH -t 2:00:00
#SBATCH -c 4
#SBATCH --mem=16G
#SBATCH -o drasdeep_%j.log
cd /mnt/data/resynthesis/repro/SEEA_star/Retrosynthesis
PY=/home/smidlva1/.conda/envs/seea/bin/python
mkdir -p draslovka_out
echo "=== DEEP standard (Retro* + value net) ==="
$PY draslovka_deep.py --arm deep_standard --ckpt saved_model/best_epoch.pt --candidate_size 1000000 --out draslovka_out/deep_standard.json
echo "=== DEEP ours (SeeA* + L*) ==="
$PY draslovka_deep.py --arm deep_lstar --ckpt saved_model/lstar_broad.pt --candidate_size 50 --out draslovka_out/deep_lstar.json
echo DEEP_DONE
