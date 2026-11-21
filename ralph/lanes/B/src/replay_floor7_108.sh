#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

lane=../../ralph/lanes/B
directory=work/e162_r5
input="$directory/lateral2.union.g6"
cliques="$directory/e107_cliques_full.cliq.tsv"
complement="$directory/e107_cliques_full.missing.tsv"
pins="$directory/pins7.tsv"
proofs="$directory/e107_pin_full"
manifest=logs/e107_pin_full.log

timeout 30s sha256sum -c "$lane/FLOOR7_108.sha256"
timeout 2m build/audit_duals 32 107 9 234681 < "$input"
timeout 2m ../../opt/bin/shortg -t -u -T"$directory" "$input" 2> "$directory/floor108.traces"
rg -q '^>Z 234681 graphs read ' "$directory/floor108.traces"
rg -qx '>Z 234681 graphs produced' "$directory/floor108.traces"
test "$(wc -l < "$cliques")" -eq 231455
test "$(wc -l < "$complement")" -eq 3226
test "$(wc -l < "$pins")" -eq 3226
timeout 3m python3 -B ../../ralph/lanes/G/verify_uncovered.py "$input" "$cliques" --degree 7 --unproved "$complement"
timeout --kill-after=30s 10m python3 -B "$lane/src/e107_core_proofs.py" "$complement" "$proofs" --pins "$pins" --verify-only > "$directory/floor108.rechecked.log"
awk '$2=="cert"' "$directory/floor108.rechecked.log" > "$directory/floor108.rechecked.index"
awk '$2=="cert"' "$manifest" > "$directory/floor108.production.index"
test "$(wc -l < "$directory/floor108.rechecked.index")" -eq 3226
cmp "$directory/floor108.production.index" "$directory/floor108.rechecked.index"
printf 'complete e107 cover: 231455 demand cliques plus 3226 rebuilt, dual-checked LRATs\n'
