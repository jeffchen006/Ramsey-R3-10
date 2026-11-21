#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
workers=${1:?workers}
source_dir=../../ralph/lanes/B/src
while [[ ! -s val/r38_23_le51.g6 && ! -s val/r38_23_le52.g6 ]]; do
    sleep 30
done
python3 "$source_dir/n30.py" 88 --prefix --workers "$workers" --program mixed
python3 "$source_dir/scan_mtf.py" val/r39_30_le88_mixed_prefix.g6 --workers "$workers" --edge 88 --label prefix
