#!/bin/bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
lane=$root/ralph/lanes/E
core=$1
offset=$2
stride=$3
mode=${4:-single}
cut_size=${5:-8}
while read -r index lift; do
    base="pins.$core/$index.$mode"
    status=0
    nice -n 5 timeout 100 bash "$lane/run_m11.sh" "cover.$core.jsonl" "$index" "$lift" "$mode" "$base" \
        --cut-size "$cut_size" > "$base.log" 2>&1 || status=$?
    if [[ $status == 0 ]] && rg -qx 's VERIFIED UNSAT' "$base.lrat.log" 2>/dev/null; then
        printf '%s\t%s\tCHECKED\n' "$index" "$lift"
    elif [[ $status == 0 ]] && rg -qx 'SAT RELAXATION' "$base.log"; then
        printf '%s\t%s\tSAT_RELAXATION\n' "$index" "$lift"
    else
        printf '%s\t%s\tINCOMPLETE_%s\n' "$index" "$lift" "$status"
    fi
done < <(awk -v o="$offset" -v s="$stride" '(NR-1)%s==o' "todo.$core.tsv")
