#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
out=work/convex
mkdir -p "$out"

for degree in 4 5 6; do
    input=val/r3_6_$((21-degree)).g6
    flags=(-k 6 -d "$degree" -m "$degree" -M 6 -E 63 -e 63 -A 0 -B 0 -C 0 -S 5)
    CONVEX_DEPTH=0 timeout 30s build/glueconvex "${flags[@]}" <"$input" >"$out/cal$degree"
    cmp "$out/cal$degree" "work/anchor/cal$degree.ref"
done
printf 'all root-degree controls match the independent filter\n'

for level in "$@"; do
    case "$level" in
        52) degree=6 ;;
        44) degree=7 ;;
        *) exit 2 ;;
    esac
    for block in 1 2 3 4; do
        key=e${level}_b${block}
        flags=(-k 8 -d "$degree" -m 2 -M 8 -E 88 -e 88 -A 58 -B 51 -C 43 -S 5)
        for depth in ref 0 2; do
            binary=glueconvex
            [[ $depth != ref ]] || binary=gluelook_ref
            printf '%s %s\n' "$key" "$depth"
            CONVEX_DEPTH="$depth" /usr/bin/time -f 'CPU %U+%S wall %e' timeout --kill-after=10s 2m build/"$binary" "${flags[@]}" \
                <"work/paired_speed/$key.in" >"$out/$key.$depth"
            cmp "$out/$key.$depth" "work/anchor/$key.ref"
            /usr/bin/time -f 'shortg CPU %U+%S wall %e' timeout 30s ../../opt/bin/shortg -q -Twork "$out/$key.$depth" "$out/$key.$depth.canon"
        done
    done
done
printf 'all timed controls match the independent filter\n'
