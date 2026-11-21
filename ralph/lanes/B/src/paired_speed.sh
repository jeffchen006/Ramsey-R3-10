#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
source_dir=../../ralph/lanes/B/src
mkdir -p work/paired_speed

for level in "$@"; do
    case "$level" in
        43|44) order=22; degree=7; source=val/r38_22_le44.g6 ;;
        52) order=23; degree=6; source=val/r38_23_le52.g6 ;;
        *) exit 2 ;;
    esac
    for block in 1 2 3 4; do
        tag="work/paired_speed/e${level}_b${block}"
        python3 "$source_dir/sample_levels.py" "$source" "$order" "$level" 8 "$((56187 + 100 * level + block))" >"$tag.in"
        sha256sum "$tag.in"
        for variant in gluetrans gluecheap; do
            /usr/bin/time -f "%U %S %e" -o "$tag.$variant.time" timeout 3m nice -n 5 \
                "build/$variant" -k 8 -d "$degree" -m 2 -M 8 -E 88 -e 88 \
                <"$tag.in" >"$tag.$variant.g6" 2>"$tag.$variant.log"
        done
        cmp "$tag.gluetrans.g6" "$tag.gluecheap.g6"
        python3 "$source_dir/profile_filter.py" 88 58 51 42 <"$tag.gluetrans.g6" >"$tag.tail.ref"
        /usr/bin/time -f "%U %S %e" -o "$tag.tail.time" timeout 3m nice -n 5 \
            build/gluecheap -k 8 -d "$degree" -m 2 -M 8 -E 88 -e 88 -A 58 -B 51 -C 42 \
            <"$tag.in" >"$tag.tail.g6" 2>"$tag.tail.log"
        cmp "$tag.tail.ref" "$tag.tail.g6"
        printf '%s\n' "$tag"
        for variant in gluetrans gluecheap tail; do
            printf '%-10s %s, %s raw outputs\n' "$variant" "$(cat "$tag.$variant.time")" "$(wc -l <"$tag.$variant.g6")"
        done
    done
done
