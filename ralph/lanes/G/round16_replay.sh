#!/bin/bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$root/scratch/G/round16"
export PYTHONDONTWRITEBYTECODE=1 LC_ALL=C TMPDIR=$PWD OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 16777216
ulimit -t 360
work=$(mktemp -d "$PWD/replay.XXXXXX")
trap 'rm -rf "$work"' EXIT
run() { nice -n 5 timeout "$@"; }

run 60s g++ -O3 -I "$root/gluing/src" smallcrown.cc -o "$work/smallcrown"
for order in 15 16; do
    if [ "$order" = 15 ]; then
        input="$root/scratch/B/val/r3_6_15.g6"
    else
        input="$root/gluing/val/r3_6_16.g6"
    fi
    run 30s "$work/smallcrown" < "$input" > "$work/scan"
    run 30s "$work/smallcrown" "$order" > "$work/generate"
    for arm in scan generate; do
        run 30s "$root/opt/bin/labelg" -q "$work/$arm" | sort -u > "$work/$arm.set"
    done
    cmp "$work/scan.set" "$work/generate.set"
    cmp "$work/scan.set" "$root/scratch/ideas/r015_N/small.$order.extract.set"
    printf 'order %s control canonical classes: ' "$order"
    wc -l < "$work/scan.set"
done
run 40s "$root/opt/venv/bin/python" -B project.py --control
run 700s "$root/opt/venv/bin/python" -B "$root/ralph/lanes/G/round16_pilot.py" final
