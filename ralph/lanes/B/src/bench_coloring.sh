#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
out=work/coloring
mkdir -p "$out"
level=${1:?52 or 44}
shift
case "$level" in
    52) degree=6 ;;
    44) degree=7 ;;
    *) exit 2 ;;
esac

for variant in "$@"; do
    for root in 4 5 6; do
        input=val/r3_6_$((21-root)).g6
        common=(-k 6 -d "$root" -m "$root" -M 6 -E 63 -e 63 -A 0 -B 0 -C 0 -S 5)
        timeout 30s "build/glueperf_$variant" "${common[@]}" <"$input" >"$out/cal$root.$variant"
        cmp "$out/cal$root.$variant" "work/anchor/cal$root.ref"
    done
done
printf 'all root-degree controls match the independent filter\n'

for block in 1 2 3 4; do
    key=e${level}_b${block}
    common=(-k 8 -d "$degree" -m 2 -M 8 -E 88 -e 88 -S 5)
    for variant in "$@"; do
        printf '%s %s\n' "$key" "$variant"
        /usr/bin/time -f 'CPU %U+%S wall %e' timeout --kill-after=10s 2m "build/glueperf_$variant" \
            "${common[@]}" -A 58 -B 51 -C 43 <"work/paired_speed/$key.in" >"$out/$key.$variant"
        cmp "$out/$key.$variant" "work/anchor/$key.ref"
        /usr/bin/time -f 'shortg CPU %U+%S wall %e' timeout 30s ../../opt/bin/shortg -q -Twork \
            "$out/$key.$variant" "$out/$key.$variant.canon"
    done
done
printf 'all timed controls match the independent filter\n'
