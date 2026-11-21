#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
source_dir=../../ralph/lanes/B/src
out=work/round4_holdout
mkdir -p "$out"
variants=("$@")
if (( ${#variants[@]} < 2 )); then exit 2; fi

input="$out/e52_inputs.g6"
timeout 1m python3 "$source_dir/sample_levels.py" val/r38_23_le52.g6 23 52 128 549122 >"$input"
timeout 1m python3 "$source_dir/ecount.py" "$input" 52:128
sha256sum "$input"

for variant in "${variants[@]}"; do
    combined="$out/control22.$variant.raw"
    : >"$combined"
    for degree in 4 5 6; do
        timeout 1m "build/glueperf_$variant" -k 6 -d "$degree" -m "$degree" -M 6 \
            <"val/r3_6_$((21-degree)).g6" >>"$combined"
    done
    timeout 1m ../../opt/bin/shortg -q -Twork "$combined" "$out/control22.$variant.g6"
    cmp "$out/control22.$variant.g6" work/cal22_reference.g6
    printf 'control22 %s %s canonical graphs\n' "$variant" "$(wc -l <"$out/control22.$variant.g6")"
done

for flags in target relaxed; do
    case "$flags" in
        target) profile=(-A 58 -B 51 -C 43) ;;
        relaxed) profile=(-A 0 -B 0 -C 0) ;;
    esac
    for variant in "${variants[@]}"; do
        printf 'e52 holdout %s %s\n' "$variant" "$flags"
        raw="$out/$variant.$flags.raw"
        /usr/bin/time -f 'CPU %U+%S wall %e' timeout --kill-after=10s 3m "build/glueperf_$variant" \
            -k 8 -d 6 -m 2 -M 8 -E 88 -e 88 -S 5 "${profile[@]}" <"$input" >"$raw"
        cmp "$raw" "$out/${variants[0]}.$flags.raw"
        /usr/bin/time -f 'shortg CPU %U+%S wall %e' timeout 30s ../../opt/bin/shortg -q -Twork \
            "$raw" "$out/$variant.$flags.canon"
        printf 'labelled=%s canonical=%s\n' "$(wc -l <"$raw")" "$(wc -l <"$out/$variant.$flags.canon")"
    done
done
printf 'holdout exact\n'
