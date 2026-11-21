#!/bin/bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
worker=$1
shift
outdir=${MASK_OUTDIR:-r3_mask}
extra_flags=()
if [[ ${MASK_LAZY_ROWS:-0} == 1 ]]; then
    extra_flags+=(--lazy-rows --supergraph-cut)
fi
for index in "$@"; do
    set +e
    /usr/bin/time -f 'cpu=%U+%S wall=%e rss=%M' nice -n 5 timeout 135 prlimit --cpu=60:61 --as=17179869184 \
        "$root/opt/venv/bin/python" -B "$root/ralph/lanes/D/mask_sat.py" 40 9 3 catalogues/R3.g6 "$index" \
        --min-edge --extra-cuts --models 5000 "${extra_flags[@]}" > "$outdir/k${index}.log" 2>&1
    outcome=$?
    set -e
    printf '%s %d %d\n' "$worker" "$index" "$outcome"
done
