#!/bin/bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
out=$1
shift
mkdir -p "$out"
ulimit -v 16777216
for index in "$@"; do
    for side in 0 1; do
        for mode in shadow local; do
            flags=()
            if [[ $mode == local ]]; then flags=(--obstructions side_obstructions_orbit.json); fi
            stem="$out/k$index-$side-$mode"
            set +e
            /usr/bin/time -f 'cpu=%U+%S wall=%e rss=%M' timeout --kill-after=3 30 prlimit --cpu=15:16 \
                "$root/opt/venv/bin/python" -B "$root/ralph/lanes/D/factor_sat.py" 40 9 catalogues/R3.g6 \
                "$index" "$stem.profiles" --side "$side" --min-edge --limit 100 "${flags[@]}" > "$stem.log" 2>&1
            status=$?
            set -e
            printf 'kernel=%d side=%d mode=%s status=%d\n' "$index" "$side" "$mode" "$status"
        done
    done
done
