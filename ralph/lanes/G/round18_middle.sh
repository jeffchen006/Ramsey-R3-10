#!/bin/bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$root/scratch/G/round18"
export PYTHONDONTWRITEBYTECODE=1 LC_ALL=C TMPDIR=$PWD OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTHONPATH="$root/scratch/G/round16"
ulimit -v 524288
phase=$1
time_cap=90
cpu_cap=55
if [[ $phase == estimate || $phase == reconcile || $phase == complete ]]; then
    time_cap=30
    cpu_cap=20
fi
ulimit -t "$cpu_cap"
exec nice -n 5 timeout --kill-after=3s "${time_cap}s" "$root/opt/venv/bin/python" -B \
    "$root/ralph/lanes/G/round18_middle.py" "$@"
