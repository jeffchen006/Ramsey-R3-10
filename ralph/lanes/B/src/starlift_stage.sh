#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

source_dir=../../ralph/lanes/B/src
parent=work/edgeup2/up86/e87.g6
prior=work/edgeup2/up86/e88.g6
out=work/starlift/up86parents
mkdir "$out"
timeout 1m python3 "$source_dir/ecount.py" "$parent" 87:133434
/usr/bin/time -f 'starlift CPU %U+%S wall %e' timeout 15m build/starlift -a 8 -s 1 -c \
    <"$parent" >"$out/raw.g6" 2>"$out/starlift.log"
cat "$out/starlift.log"
rg -Fq 'starlift: in=133434 ' "$out/starlift.log"
/usr/bin/time -f 'labelg CPU %U+%S wall %e' timeout 3m ../../opt/bin/labelg -q "$out/raw.g6" "$out/labelled.g6"
timeout 2m sort -u "$out/labelled.g6" -o "$out/canon.g6"
timeout 3m comm --check-order -23 "$out/canon.g6" "$prior" >"$out/new.g6"
/usr/bin/time -f 'critical CPU %U+%S wall %e' timeout 3m build/irreducible 9 \
    <"$out/new.g6" >"$out/critical.g6"
count=$(wc -l <"$out/critical.g6")
wc -l "$out/"{raw,canon,new,critical}.g6
if (( count )); then
    timeout 2m python3 "$source_dir/ecount.py" "$out/critical.g6" "88:$count"
fi
/usr/bin/time -f 'MTF scan CPU %U+%S wall %e' timeout 25m python3 "$source_dir/scan_mtf.py" \
    "$out/critical.g6" --workers 1 --edge 88 --label star_up86
timeout 2m python3 "$source_dir/audit_chunks.py" work/mtf_star_up86_e88 9 "$count" 1024
printf 'star_up86 terminal; exact %s globally edge-critical e88 inputs scanned\n' "$count"
