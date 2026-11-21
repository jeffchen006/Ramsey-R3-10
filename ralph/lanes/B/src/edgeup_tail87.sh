#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
ulimit -v 16777216

source_dir=../../ralph/lanes/B/src
prior=work/edgeup2/up86
out=work/edgeup2/up87tail
prefix=val/r39_30_le88_mixed_prefix.g6
mkdir "$out"
rg -Fq 'exact e86 HoG equality and GR T14 lower-level counts checked; full through e=87' logs/prefix_pipeline.log
rg -Fq 'MTF up86 e=88 checked all input chunks; output 0 graphs' logs/edgeup2_full86.log
timeout 5m ../../opt/bin/pickg -q -e87 "$prefix" "$out/all87.g6"
timeout 5m python3 "$source_dir/ecount.py" "$out/all87.g6" 87:147335
timeout 5m sort -cu "$out/all87.g6"
timeout 5m sort -cu "$prior/e87.g6"
timeout 5m comm -23 "$prior/e87.g6" "$out/all87.g6" >"$out/bad.g6"
test ! -s "$out/bad.g6"
timeout 5m comm -23 "$out/all87.g6" "$prior/e87.g6" >"$out/tail87.g6"
timeout 5m python3 "$source_dir/ecount.py" "$out/tail87.g6" 87:13901
/usr/bin/time -f 'edgeup CPU %U+%S wall %e' timeout 15m build/edgeup <"$out/tail87.g6" >"$out/e88.raw"
/usr/bin/time -f 'shortg CPU %U+%S wall %e' timeout 20m ../../opt/bin/shortg -q -Twork "$out/e88.raw" "$out/e88.g6"
rm "$out/e88.raw"
timeout 5m comm -23 "$out/e88.g6" "$prior/e88.g6" >"$out/tail88.g6"
wc -l "$out/tail88.g6"
/usr/bin/time -f 'MTF scan CPU %U+%S wall %e' timeout 2h python3 "$source_dir/scan_mtf.py" "$out/tail88.g6" --workers 1 --edge 88 --label up87tail
