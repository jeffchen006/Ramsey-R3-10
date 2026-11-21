#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
source_dir=../../ralph/lanes/B/src
out=work/anchor
mkdir -p "$out"

for degree in 4 5 6; do
    input=val/r3_6_$((21-degree)).g6
    common=(-k 6 -d "$degree" -m "$degree" -M 6 -E 63 -e 63 -A 0 -B 0 -C 0)
    timeout 1m nice -n 5 build/gluecheap "${common[@]}" <"$input" >"$out/cal$degree.raw"
    timeout 1m nice -n 5 python3 "$source_dir/profile_filter.py" 63 0 0 0 --star-minimum 5 \
        <"$out/cal$degree.raw" >"$out/cal$degree.ref"
    for overlap in off on; do
        extra=(); [[ $overlap == off ]] || extra=(-P)
        timeout 1m nice -n 5 build/glueanchor "${common[@]}" -S 5 "${extra[@]}" \
            <"$input" >"$out/cal$degree.$overlap"
        cmp "$out/cal$degree.ref" "$out/cal$degree.$overlap"
    done
done
wc -l "$out"/cal*.ref

for level in "$@"; do
    case "$level" in
        44) degree=7 ;;
        52) degree=6 ;;
        *) exit 2 ;;
    esac
    for block in 1 2 3 4; do
        tag="$out/e${level}_b${block}"
        control="work/paired_speed/e${level}_b${block}"
        common=(-k 8 -d "$degree" -m 2 -M 8 -E 88 -e 88 -A 58 -B 51 -C 43)
        timeout 1m nice -n 5 python3 "$source_dir/profile_filter.py" 88 58 51 43 --star-minimum 5 \
            <"$control.gluecheap.g6" >"$tag.ref"
        for overlap in off on; do
            extra=(); [[ $overlap == off ]] || extra=(-P)
            /usr/bin/time -f 'CPU %U+%S wall %e' timeout 3m nice -n 5 build/glueanchor \
                "${common[@]}" -S 5 "${extra[@]}" <"$control.in" >"$tag.$overlap"
            cmp "$tag.ref" "$tag.$overlap"
            printf '%s %s exact, %s raw outputs\n' "$tag" "$overlap" "$(wc -l <"$tag.$overlap")"
        done
    done
done
