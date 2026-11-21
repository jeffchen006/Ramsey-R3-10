#!/bin/bash
set -euo pipefail
lane=$(cd -- "$(dirname -- "$0")" && pwd)
cover=$1
plan=$2
output=$3
offset=$4
stride=$5
mkdir -p "$output"
export M11_FASTCUTS=${M11_FASTCUTS:-../r6_e11/m11_fastcuts.so}
while read -r index lift; do
    base="$output/${index}_${lift}"
    if [[ -f $base.cnf && -f $base.lrat ]] && rg -qx 's VERIFIED UNSAT' "$base.lrat.log" 2>/dev/null; then
        printf '%s\t%s\tCHECKED_REUSED\n' "$index" "$lift"
        continue
    fi
    status=0
    nice -n 5 timeout 100s bash "$lane/run_m11.sh" "$cover" "$index" "$lift" all "$base" \
        > "$base.log" 2>&1 || status=$?
    if [[ $status == 0 ]] && rg -qx 's VERIFIED UNSAT' "$base.lrat.log" 2>/dev/null; then
        printf '%s\t%s\tCHECKED\n' "$index" "$lift"
    elif [[ $status == 0 ]] && rg -qx 'SAT RELAXATION' "$base.log"; then
        printf '%s\t%s\tSAT_RELAXATION\n' "$index" "$lift"
    else
        printf '%s\t%s\tINCOMPLETE_%s\n' "$index" "$lift" "$status"
    fi
done < <(awk -v offset="$offset" -v stride="$stride" '(NR-1)%stride==offset' "$plan")
