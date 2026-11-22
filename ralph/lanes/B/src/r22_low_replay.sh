#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
ulimit -v 16777216
ulimit -f 32768
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../../.." && pwd)
[[ $PWD == "$root/scratch/B/"* ]]
code=$root/ralph/lanes/B/src/r22_low.py
geng=$root/opt/bin/geng
labelg=$root/opt/bin/labelg

compare() {
    local order=$1 degree=$2 prefix=low$1
    "$geng" -q -t -d"$degree" -D"$degree" "$order" > "$prefix.geng.raw"
    python3 "$code" filter "$order" "$degree" "$prefix.geng.raw" > "$prefix.geng.filtered"
    python3 "$code" rooted "$order" "$degree" > "$prefix.rooted.raw"
    "$labelg" -q < "$prefix.rooted.raw" | sort -u > "$prefix.rooted.g6"
    "$labelg" -q < "$prefix.geng.filtered" | sort -u > "$prefix.geng.g6"
    cmp "$prefix.geng.g6" "$prefix.rooted.g6"
    printf '%s/d%s geng %s→%s; rooted %s labelled; %s matching classes\n' "$order" "$degree" \
        "$(wc -l < "$prefix.geng.raw")" "$(wc -l < "$prefix.geng.filtered")" \
        "$(wc -l < "$prefix.rooted.raw")" "$(wc -l < "$prefix.rooted.g6")"
}

compare 5 2
python3 "$code" circulant 5 1 | "$labelg" -q | cmp low5.rooted.g6 -
python3 "$code" controls
compare 12 4
compare 13 4
python3 "$code" circulant 13 1 5 | "$labelg" -q | cmp low13.rooted.g6 -
python3 "$code" inspect low12.rooted.g6 low13.rooted.g6
