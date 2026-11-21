#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
out=work/rows
mkdir -p "$out"

for variant in ref rows support both nocolor; do
    for degree in 4 5 6; do
        input=val/r3_6_$((21-degree)).g6
        flags=(-k 6 -d "$degree" -m "$degree" -M 6 -E 63 -e 63 -A 0 -B 0 -C 0 -S 5)
        timeout 30s build/glueperf_"$variant" "${flags[@]}" <"$input" >"$out/cal$degree.$variant"
        cmp "$out/cal$degree.$variant" "work/anchor/cal$degree.ref"
    done
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
        flags=(-k 8 -d "$degree" -m 2 -M 8 -E 88 -e 88 -S 5)
        for variant in ref rows support both nocolor; do
            for scope in target relaxed; do
                if [[ $scope == target ]]; then
                    exclusions=(-A 58 -B 51 -C 43)
                    expected="work/anchor/$key.ref"
                else
                    exclusions=(-A 0 -B 0 -C 0)
                    expected="work/relaxed_r4/$key.ref"
                fi
                printf '%s %s %s\n' "$key" "$variant" "$scope"
                /usr/bin/time -f 'CPU %U+%S wall %e' timeout --kill-after=10s 2m build/glueperf_"$variant" \
                    "${flags[@]}" "${exclusions[@]}" <"work/paired_speed/$key.in" >"$out/$key.$variant.$scope"
                cmp "$out/$key.$variant.$scope" "$expected"
                /usr/bin/time -f 'shortg CPU %U+%S wall %e' timeout 30s ../../opt/bin/shortg -q -Twork \
                    "$out/$key.$variant.$scope" "$out/$key.$variant.$scope.canon"
            done
        done
    done
done
printf 'all timed controls match the independent filter\n'
