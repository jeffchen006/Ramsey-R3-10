#!/bin/bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
out=$1
seconds=$2
shift 2
mkdir -p "$out"
ulimit -v 16777216
flags=()
if [[ ${FACTOR_STRENGTHENED:-0} == 1 ]]; then
    flags=(--no-k33 --obstructions side_obstructions_orbit.json)
fi
for index in "$@"; do
    set +e
    /usr/bin/time -f 'cpu=%U+%S wall=%e rss=%M' timeout --kill-after=3 "$((seconds*3))" \
        prlimit --cpu="$seconds:$((seconds+1))" "$root/opt/venv/bin/python" -B \
        "$root/ralph/lanes/D/factor_sat.py" 40 9 catalogues/R3.g6 "$index" "$out/k$index.g6" \
        --min-edge --shadow-edges --limit 1 "${flags[@]}" > "$out/k$index.log" 2>&1
    status=$?
    set -e
    printf 'kernel=%d status=%d\n' "$index" "$status"
done
