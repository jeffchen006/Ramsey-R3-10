#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
ulimit -v 16777216

first_level=${1:?first level, 86 or 87}
input=${2:?canonical census input}
label=${3:?unused output label}
case "$first_level" in
    86) expected=1800 ;;
    87) expected=147335 ;;
    *) exit 2 ;;
esac
source_dir=../../ralph/lanes/B/src
output_dir="work/edgeup2/$label"
mkdir "$output_dir"
timeout 5m python3 "$source_dir/ecount.py" "$input" "$first_level:$expected"
parent=$input
for ((edge=first_level; edge<88; ++edge)); do
    next=$((edge+1))
    raw="$output_dir/e$next.raw"
    canon="$output_dir/e$next.g6"
    /usr/bin/time -f "edgeup $edge CPU %U+%S wall %e" timeout 30m build/edgeup <"$parent" >"$raw"
    /usr/bin/time -f "shortg $next CPU %U+%S wall %e" timeout 45m ../../opt/bin/shortg -q -Twork "$raw" "$canon"
    test -s "$canon"
    wc -l "$canon"
    rm "$raw"
    parent=$canon
done
/usr/bin/time -f "MTF scan CPU %U+%S wall %e" timeout 4h python3 "$source_dir/scan_mtf.py" "$parent" --workers 1 --edge 88 --label "$label"
