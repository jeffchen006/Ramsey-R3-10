#!/bin/bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
for index in "$@"; do
    set +e
    /usr/bin/time -f 'cpu=%U+%S wall=%e rss=%M' nice -n 5 timeout 135 prlimit --cpu=60:61 --as=17179869184 \
        "$root/opt/venv/bin/python" -B "$root/ralph/lanes/D/mask_sat.py" 40 9 3 catalogues/R3.g6 "$index" \
        --min-edge --extra-cuts --supergraph-cut --native --models 5000 > "r3_mask_native/k${index}.log" 2>&1
    outcome=$?
    set -e
    printf '%d %d\n' "$index" "$outcome"
done
