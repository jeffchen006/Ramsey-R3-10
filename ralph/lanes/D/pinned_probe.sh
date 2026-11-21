#!/bin/bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
index=$1
out=$2
seconds=$3
ulimit -v 16777216
ulimit -c 0
while read -r kernel side line path; do
    [[ $kernel == "$index" ]] || continue
    stem="$out/k$kernel-$side-line$line"
    set +e
    /usr/bin/time -f 'cpu=%U+%S wall=%e rss=%M' timeout --kill-after=2 "$((seconds*3))" \
        prlimit --cpu="$seconds:$((seconds+1))" "$root/opt/venv/bin/python" -B \
        "$root/ralph/lanes/D/pinned_side.py" 9 catalogues/R3.g6 "$kernel" "$side" "$path" "$stem.g6" \
        --line "$line" --min-edge --mode first > "$stem.log" 2>&1
    status=$?
    set -e
    printf '%s\t%s\t%s\t%s\n' "$kernel" "$side" "$line" "$status"
done < "$out/manifest.tsv"
