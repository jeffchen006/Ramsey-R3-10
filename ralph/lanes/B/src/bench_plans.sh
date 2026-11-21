#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
out=work/plans
mkdir -p "$out"

for degree in 4 5 6; do
    input=val/r3_6_$((21-degree)).g6
    flags=(-k 6 -d "$degree" -m "$degree" -M 6 -E 63 -e 63 -A 0 -B 0 -C 0 -S 5)
    for order in 0 1 2; do
        PLAN_ORDER="$order" timeout 30s build/glueplan "${flags[@]}" <"$input" >"$out/cal$degree.$order"
        timeout 30s sort "$out/cal$degree.$order" >"$out/cal$degree.$order.sorted"
        timeout 30s sort "work/anchor/cal$degree.ref" >"$out/cal$degree.ref.sorted"
        cmp "$out/cal$degree.$order.sorted" "$out/cal$degree.ref.sorted"
    done
done
printf 'all root-degree/order controls match the independent filter\n'

for level in "$@"; do
    case "$level" in
        52) degree=6 ;;
        44) degree=7 ;;
        *) exit 2 ;;
    esac
    for block in 1 2 3 4; do
        key=e${level}_b${block}
        flags=(-k 8 -d "$degree" -m 2 -M 8 -E 88 -e 88 -A 58 -B 51 -C 43 -S 5)
        for order in 1 0 2; do
            printf '%s %s\n' "$key" "$order"
            PLAN_ORDER="$order" /usr/bin/time -f 'CPU %U+%S wall %e' timeout --kill-after=10s 2m build/glueplan "${flags[@]}" \
                <"work/paired_speed/$key.in" >"$out/$key.$order"
            timeout 30s sort "$out/$key.$order" >"$out/$key.$order.sorted"
            timeout 30s sort "work/anchor/$key.ref" >"$out/$key.ref.sorted"
            cmp "$out/$key.$order.sorted" "$out/$key.ref.sorted"
            /usr/bin/time -f 'shortg CPU %U+%S wall %e' timeout 30s ../../opt/bin/shortg -q -Twork "$out/$key.$order" "$out/$key.$order.canon"
        done
    done
done
printf 'all timed controls match the independent filter\n'
