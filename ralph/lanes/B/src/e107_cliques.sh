#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

verifier=../../ralph/lanes/G/verify_uncovered.py
dir=work/e162_r5
control=../../ralph/lanes/G/root_certs/canon32_e104.g6
input=${1:?catalogue or sample}
out=${2:?output stem}

timeout 30s build/demand_clique 8 < "$control" > "$dir/e104.cal.cliq"
test "$(wc -l < "$dir/e104.cal.cliq")" -eq 39
timeout 30s python3 "$verifier" "$control" "$dir/e104.cal.cliq" --degree 7
/usr/bin/time -f 'search CPU %U+%S wall %e' timeout 5m build/demand_clique 8 < "$input" > "$out.cliq.tsv"
awk 'ARGIND==1 {covered[$1]=1; next} ! (FNR in covered) {print FNR "\t" $0}' "$out.cliq.tsv" "$input" > "$out.missing.tsv"
/usr/bin/time -f 'replay CPU %U+%S wall %e' timeout 6m python3 "$verifier" "$input" "$out.cliq.tsv" --degree 7 --unproved "$out.missing.tsv"
cut -f2 "$out.missing.tsv" > "$out.missing.g6"
sha256sum "$input" "$out.cliq.tsv" "$out.missing.tsv"
