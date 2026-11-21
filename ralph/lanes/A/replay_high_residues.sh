#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
src="$root/ralph/lanes/A"
if (( $# < 1 || $# > 2 )); then
    echo "usage: $0 NEW_SCRATCH_OUTPUT_DIR [ROUND4_FROZEN_G_DIR]" >&2
    exit 2
fi
source=$(realpath -- "${2:-$root/scratch/G/round4}")
mkdir -- "$1"
cd -- "$1"
ulimit -v 16777216
hard_cpu=$(ulimit -Ht)
if [[ $hard_cpu == unlimited || $hard_cpu -gt 600 ]]; then ulimit -t 600; fi
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
timeout 40s c++ -std=c++20 -O3 -Wall -Wextra -Werror "$src/residue_moves.cpp" -o residue_moves
py="$root/opt/venv/bin/python"
time nice -n 5 timeout 120s "$py" -B "$src/audit_high_residue_proofs.py" calibrate > proof-cal.log
time nice -n 5 timeout 30s "$py" -B "$src/audit_high_residue_proofs.py" partition-controls "$source" "$PWD" > partition-negatives.log
time nice -n 5 timeout 140s python3 -S -B "$src/audit_residue_moves.py" \
    "$PWD/residue_moves" calibrate "$root/gluing/val/r3_7_22.g6" > moves-cal.log
time nice -n 5 timeout 180s python3 -S -B "$src/audit_residue_moves.py" "$PWD/residue_moves" run \
    "$root/scratch/A/root-residue/complete-v2/residues.g6" "$source/strict120.s8.g6" \
    "$source/e121.frozen.g6" --critical "$source/e121.frozen.critical.g6" > moves-full.log
time nice -n 5 timeout 850s "$py" -B "$src/audit_high_residue_proofs.py" audit \
    "$source" "$PWD/index-full.tsv" --sample 0 > proof-full.log
sha256sum index-full.tsv
