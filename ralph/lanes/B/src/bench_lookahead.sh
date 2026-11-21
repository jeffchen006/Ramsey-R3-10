#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
out=work/lookahead
mkdir -p "$out"

for degree in 4 5 6; do
    input=val/r3_6_$((21-degree)).g6
    flags=(-k 6 -d "$degree" -m "$degree" -M 6 -E 63 -e 63 -A 0 -B 0 -C 0 -S 5)
    for depth in 1 2 3 4 5 6; do
        LOOKAHEAD_DEPTH="$depth" timeout 30s build/gluelook "${flags[@]}" <"$input" >"$out/cal$degree.$depth"
        cmp "$out/cal$degree.$depth" "work/anchor/cal$degree.ref"
    done
done
printf 'all root-degree/depth controls match the independent filter\n'

for level in "$@"; do
    case "$level" in
        52) degree=6 ;;
        44) degree=7 ;;
        *) exit 2 ;;
    esac
    for block in 1 2 3 4; do
        key=e${level}_b${block}
        flags=(-k 8 -d "$degree" -m 2 -M 8 -E 88 -e 88 -A 58 -B 51 -C 43 -S 5)
        for variant in ref 3 4 6; do
            binary=gluelook
            [[ $variant != ref ]] || binary=gluelook_ref
            printf '%s %s\n' "$key" "$variant"
            LOOKAHEAD_DEPTH="$variant" /usr/bin/time -f 'CPU %U+%S wall %e' timeout 2m build/"$binary" "${flags[@]}" \
                <"work/paired_speed/$key.in" >"$out/$key.$variant"
            cmp "$out/$key.$variant" "work/anchor/$key.ref"
            /usr/bin/time -f 'shortg CPU %U+%S wall %e' timeout 30s ../../opt/bin/shortg -q -Twork "$out/$key.$variant" "$out/$key.$variant.canon"
        done
    done
done
printf 'all timed controls match the independent filter\n'
