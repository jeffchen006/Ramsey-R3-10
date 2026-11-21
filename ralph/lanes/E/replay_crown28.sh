#!/bin/bash
set -euo pipefail
if [[ $# -lt 2 || $# -gt 3 ]]; then
    echo 'Usage (from scratch/E): bash ../../ralph/lanes/E/replay_crown28.sh W INDEX [verify|rebuild]' >&2
    exit 2
fi
size=$1
index=$2
mode=${3:-verify}
test "$mode" = verify || test "$mode" = rebuild
lane=../../ralph/lanes/E
tools=../../opt/bin
prefix="crown_cert/w$size.$index"
mkdir -p crown_cert
read -r found core < <(awk -v target="$index" '$1 == target { print }' "crown_w$size.rows.tsv")
test "$found" = "$index"
limited() { local budget=$1; shift; nice -n 5 timeout "$((budget + 35))" bash "$lane/limited.sh" "$budget" "$@"; }
shape=()
cnf_args=(--degree-cap --sort)
export CROWN_TRACE=1
unset CROWN_TIGHT CROWN_CLEAN CROWN_ANCHOR_SORT CROWN_SEED_PAIRS
case "$size" in
    4|5)
        if [[ "$size" = 5 ]]; then
            shape+=(3)
        else
            case "$core" in
                CC) clean=0 ;;
                CE|CQ) clean=2 ;;
                CF|CU) clean=4 ;;
                'C]') clean=6 ;;
                *) exit 2 ;;
            esac
            export CROWN_TIGHT=1 CROWN_CLEAN="$clean"
            cnf_args+=(--w-cap 8 --clean "$clean")
            if [[ "$clean" = 6 ]]; then
                export CROWN_ANCHOR_SORT=1 CROWN_SEED_PAIRS=1
                cnf_args+=(--anchor-sort)
            fi
        fi
        for ((count = 0; count < 10 - size; ++count)); do shape+=(4); done
        if [[ "$mode" = rebuild ]]; then
            limited 100 bin/crown_exact_v4 "$core" 9 6 full 6 0 1 "${shape[@]}" > "$prefix.rebuild.search.log" 2>&1
            rg -q '^EXHAUSTED models=0 ' "$prefix.rebuild.search.log"
            rg '^CUT ' "$prefix.rebuild.search.log" > "$prefix.rebuild.cuts"
            if [[ -f "$prefix.cuts" ]]; then cmp "$prefix.cuts" "$prefix.rebuild.cuts"; else mv "$prefix.rebuild.cuts" "$prefix.cuts"; fi
        fi
        cnf_args+=(--min-degree 4 --pair-threshold 8 --trace "$prefix.cuts")
        ;;
    6|7|8)
        for ((count = 0; count < 10 - size; ++count)); do shape+=(4); done
        ;;
    *) exit 2 ;;
esac
limited 20 python3 -B "$lane/crown_static.py" "${cnf_args[@]}" "$core" 4 "$prefix.regen.cnf" "${shape[@]}"
if [[ -f "$prefix.cnf" ]]; then
    cmp "$prefix.cnf" "$prefix.regen.cnf"
    rm "$prefix.regen.cnf"
else
    test "$mode" = rebuild
    mv "$prefix.regen.cnf" "$prefix.cnf"
fi
if [[ "$mode" = rebuild ]]; then
    set +e
    limited 110 "$tools/cadical" -q "$prefix.cnf" "$prefix.rebuild.drat"
    status=$?
    set -e
    test "$status" = 20
    limited 130 "$tools/drat-trim" "$prefix.cnf" "$prefix.rebuild.drat" -L "$prefix.rebuild.lrat"
    limited 25 "$tools/lrat-check" "$prefix.cnf" "$prefix.rebuild.lrat"
    if [[ ! -f "$prefix.drat" ]]; then mv "$prefix.rebuild.drat" "$prefix.drat"; fi
    if [[ ! -f "$prefix.lrat" ]]; then mv "$prefix.rebuild.lrat" "$prefix.lrat"; fi
else
    limited 25 "$tools/lrat-check" "$prefix.cnf" "$prefix.lrat"
fi
echo "COMPLETE W=$size index=$index core=$core mode=$mode"
