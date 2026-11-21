#!/usr/bin/env bash
set -euo pipefail
tag=$1 seconds=$2 seed=$3; shift 3
rc=0
../build/ls -n 38 -k 10 -maxdeg 9 -degcap 0 -w9 0 -focus .3 -T0 2 -T1 .2 \
    -bench -sweep 500000 -time "$seconds" -seed "$seed" -out "$tag" "$@" || rc=$?
if ((rc > 1)); then exit "$rc"; fi
if [[ -s $tag.found.g6 ]]; then
    printf 'Generated %d 38-vertex graphs\n' "$(wc -l < "$tag.found.g6")"
    OMP_NUM_THREADS=1 ../build/k39 extall "$tag.found.g6" "$tag.ext39.g6"
fi
