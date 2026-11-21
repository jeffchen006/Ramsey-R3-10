#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
out=work/order_bench
mkdir -p "$out"

for degree in 4 5 6; do
    input=val/r3_6_$((21-degree)).g6
    common=(-k 6 -d "$degree" -m "$degree" -M 6 -E 63 -e 63 -A 0 -B 0 -C 0 -S 5)
    timeout 1m nice -n 5 build/glueorder "${common[@]}" -R <"$input" >"$out/cal$degree.raw"
    timeout 1m nice -n 5 ../../opt/bin/labelg -q "work/anchor/cal$degree.ref" "$out/cal$degree.ref.label"
    timeout 1m nice -n 5 ../../opt/bin/labelg -q "$out/cal$degree.raw" "$out/cal$degree.test.label"
    timeout 1m nice -n 5 sort "$out/cal$degree.ref.label" -o "$out/cal$degree.ref.sort"
    timeout 1m nice -n 5 sort "$out/cal$degree.test.label" -o "$out/cal$degree.test.sort"
    cmp "$out/cal$degree.ref.sort" "$out/cal$degree.test.sort"
done
printf 'largest-first matches e63 canonical multisets, including multiplicities\n'

for block in 1 2 3 4; do
    tag="e52_b$block"
    common=(-k 8 -d 6 -m 2 -M 8 -E 88 -e 88 -A 58 -B 51 -C 43 -S 5)
    /usr/bin/time -f 'CPU %U+%S wall %e' timeout 2m nice -n 5 build/glueorder "${common[@]}" -R \
        <"work/paired_speed/$tag.in" >"$out/$tag.raw"
    timeout 1m nice -n 5 ../../opt/bin/labelg -q "work/anchor/$tag.ref" "$out/$tag.ref.label"
    timeout 1m nice -n 5 ../../opt/bin/labelg -q "$out/$tag.raw" "$out/$tag.test.label"
    timeout 1m nice -n 5 sort "$out/$tag.ref.label" -o "$out/$tag.ref.sort"
    timeout 1m nice -n 5 sort "$out/$tag.test.label" -o "$out/$tag.test.sort"
    cmp "$out/$tag.ref.sort" "$out/$tag.test.sort"
    printf '%s largest-first exact, %s raw outputs\n' "$tag" "$(wc -l <"$out/$tag.raw")"
done
