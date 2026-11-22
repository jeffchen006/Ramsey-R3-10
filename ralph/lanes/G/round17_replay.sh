#!/bin/bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$root/scratch/G/round17"
export PYTHONDONTWRITEBYTECODE=1 LC_ALL=C TMPDIR=$PWD OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTHONPATH="$root/scratch/G/round16"
ulimit -v 393216
case "${1:-}" in
    coverage) limit=240 ;;
    register) limit=15 ;;
    sample) limit=100 ;;
    replay) limit=85 ;;
    summary) limit=15 ;;
    *) exit 2 ;;
esac
ulimit -t "$limit"
if [[ $1 == coverage ]]; then
    (cd "$root" && sha256sum -c --quiet ralph/lanes/G/ROUND16_FREEZE.sha256)
    (cd ../round16 && sha256sum -c --quiet prior.freeze.sha256 && sha256sum -c --quiet proof.freeze.sha256)
    mkdir -p controls
    nice -n 5 timeout 30s g++ -O3 -I "$root/gluing/src" ../round16/smallcrown.cc -o controls/smallcrown
    for order in 15 16; do
        if [[ $order == 15 ]]; then
            input="$root/scratch/B/val/r3_6_15.g6"
        else
            input="$root/gluing/val/r3_6_16.g6"
        fi
        nice -n 5 timeout 30s controls/smallcrown < "$input" > "controls/$order.scan" 2> "controls/$order.scan.log"
        nice -n 5 timeout 30s controls/smallcrown "$order" > "controls/$order.gen" 2> "controls/$order.gen.log"
        for arm in scan gen; do
            nice -n 5 timeout 30s "$root/opt/bin/labelg" -q "controls/$order.$arm" | sort -u > "controls/$order.$arm.set"
        done
    done
fi
exec nice -n 5 timeout "$limit" "$root/opt/venv/bin/python" -B "$root/ralph/lanes/G/round17_aligned.py" "$@"
