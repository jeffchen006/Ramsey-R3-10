#!/bin/bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
work=$(realpath -m "$1")
case "$work" in
    "$root/scratch/G/"*|"$root/scratch/critic/"*) ;;
    *) exit 2 ;;
esac
mkdir "$work"
cd "$work"
mkdir controls
export PYTHONDONTWRITEBYTECODE=1 LC_ALL=C TMPDIR=$PWD OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTHONPATH="$root/scratch/G/round16"
ulimit -v 524288
ulimit -t 600
nice -n 5 timeout 45s g++ -O3 -I "$root/gluing/src" "$root/scratch/G/round16/smallcrown.cc" -o controls/smallcrown
for order in 15 16; do
    input="$root/scratch/B/val/r3_6_15.g6"
    if [[ $order == 16 ]]; then input="$root/gluing/val/r3_6_16.g6"; fi
    nice -n 5 timeout 30s controls/smallcrown < "$input" > "controls/$order.scan"
    nice -n 5 timeout 30s controls/smallcrown "$order" > "controls/$order.gen"
    for arm in scan gen; do
        nice -n 5 timeout 30s "$root/opt/bin/labelg" -q "controls/$order.$arm" | sort -u > "controls/$order.$arm.set"
    done
done
exec nice -n 5 timeout --kill-after=3s 900s "$root/opt/venv/bin/python" -B \
    "$root/ralph/lanes/G/round18_review.py"
