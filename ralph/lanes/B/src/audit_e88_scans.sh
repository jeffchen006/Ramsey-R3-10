#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
source_dir=../../ralph/lanes/B/src

case ${1:?up86 or e43} in
    up86)
        rg -Fq 'MTF up86 e=88 checked all input chunks; output 0 graphs' logs/edgeup2_full86.log
        timeout 2m cmp -s work/edgeup2/up86/e88.g6 work/mtf_up86_e88/inputs.g6
        test "$(stat -c '%s' work/mtf_up86_e88/inputs.g6)" -eq $((75*4751963))
        timeout 2m python3 "$source_dir/audit_chunks.py" work/mtf_up86_e88 9 4751963 1024
        ;;
    e43)
        label=d7_e43_outside_prefix
        rg -Fq "MTF $label e=88 checked all input chunks; output 0 graphs" logs/tail7_e43.log
        timeout 1m python3 "$source_dir/ecount.py" "work/${label}_inputs.g6" 43:1521
        timeout 1m python3 "$source_dir/audit_chunks.py" "work/$label" 7 1521 32
        timeout 1m cmp -s "val/$label.g6" "work/mtf_${label}_e88/inputs.g6"
        bytes=$(stat -c '%s' "val/$label.g6")
        test $((bytes % 75)) -eq 0
        count=$((bytes / 75))
        if (( count )); then
            timeout 2m python3 "$source_dir/ecount.py" "val/$label.g6" "88:$count"
        fi
        timeout 2m python3 "$source_dir/audit_chunks.py" "work/mtf_${label}_e88" 9 "$count" 1024
        ;;
    *) exit 2 ;;
esac
printf '%s audit passed\n' "$1"
