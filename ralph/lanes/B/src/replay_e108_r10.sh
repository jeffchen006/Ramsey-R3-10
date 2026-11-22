#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
ulimit -t 750
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
src=../../ralph/lanes/B/src
out=${1:?new replay directory}
original=work/e108_r10_stitch2

bash "$src/e108_stitch_r10.sh" control "$out"
bash "$src/e108_stitch_r10.sh" prepare "$out"
for slice in a b; do
    bash "$src/e108_stitch_r10.sh" generate "$out" "$slice"
    bash "$src/e108_stitch_r10.sh" lift "$out" "$slice"
done
bash "$src/e108_stitch_r10.sh" repuncture "$out"
for item in "$original"/{seed128.g6,withheld.g6,previous.parents,?.seed,[ab].*.selected,[ab].*.keys,[ab].*.novel,[ab].*.withheld,micro.98.selected,micro.keys,micro.novel}; do
    cmp "$item" "$out/${item##*/}"
done
for level in 98 99 100 101; do
    sources=("$out/a.$level.selected" "$out/b.$level.selected")
    if (( level == 98 )); then sources+=("$out/micro.98.selected"); fi
    cat "${sources[@]}" | sort -u > "$out/combined.$level.selected"
    test "$(wc -l < "$out/combined.$level.selected")" -eq 256
    comm -12 "$out/combined.$level.selected" "$out/previous.parents" | cmp - /dev/null
    timeout 30s build/audit_duals 31 "$level" 9 256 < "$out/combined.$level.selected"
    timeout 30s build/irreducible 9 < "$out/combined.$level.selected" | cmp - "$out/combined.$level.selected"
done
echo 'PASS byte-identical control and target replay; all 1,024 parents critical, distinct and outside recorded prior pools'
