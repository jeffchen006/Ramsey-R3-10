#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
ulimit -t 90
ulimit -f "${RAW_BLOCKS:-32768}"
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
tools=../../opt/bin
python=../../opt/venv/bin/python
src=../../ralph/lanes/B/src
job=${1:?rank directory}
mode=${2:-produce}
cross=${3:-273}
minindep=${4:-0}
variant=${5:-legacy}
flags=()
[[ $variant == legacy || $variant == compact || $variant =~ ^(6(77|78|88)|777)$ ]]
if [[ $variant == compact ]]; then flags+=(--compact); fi
if [[ $variant =~ ^(6(77|78|88)|777)$ ]]; then flags+=(--one-low "$variant"); fi
[[ $mode == produce || $mode == replay ]]
timefmt='cpu=%U+%S wall=%e rss=%M'
if [[ $mode == produce ]]; then
    /usr/bin/time -o "$job/build.time" -f "$timefmt" \
        timeout --kill-after=2s 35s "$python" "$src/paircut_r23.py" \
        --cross "$cross" --min-stem-indep "$minindep" "${flags[@]}" "$job/stem.g6" "$job/lift.cnf"
    rc=0
    /usr/bin/time -o "$job/solve.time" -f "$timefmt" \
        timeout --kill-after=2s 65s "$tools/cadical" --lrat --no-binary \
        "$job/lift.cnf" "$job/lift.lrat" >"$job/solve.log" || rc=$?
    if [[ $rc != 20 ]] || ! grep -q '^s UNSATISFIABLE$' "$job/solve.log"; then
        printf 'OPEN solver rc=%s\n' "$rc"
        exit 1
    fi
fi
/usr/bin/time -o "$job/cake.time" -f "$timefmt" \
    timeout --kill-after=2s 35s "$tools/cake_lpr" "$job/lift.cnf" "$job/lift.lrat" >"$job/cake.log"
grep -Fxq 's VERIFIED UNSAT' "$job/cake.log"
/usr/bin/time -o "$job/lrat.time" -f "$timefmt" \
    timeout --kill-after=2s 35s "$tools/lrat-check" "$job/lift.cnf" "$job/lift.lrat" >"$job/lrat.log"
grep -Fxq 'c VERIFIED' "$job/lrat.log"
printf 'DUAL %s cnf=%s lrat=%s\n' "$job" "$(stat -c %s "$job/lift.cnf")" "$(stat -c %s "$job/lift.lrat")"
