#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
ulimit -t 85
ulimit -f "${FILE_BLOCKS:-32768}"
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
tools=../../opt/bin
source=../../ralph/lanes/B/src/high_r24_lift.py
python=../../opt/venv/bin/python
job=${1:?job directory}
marked=${2:?four marked sites}
mode=${3:-produce}
[[ $mode == produce || $mode == replay ]]
timefmt='cpu=%U+%S wall=%e rss=%M'
flags=()
proof_suffix=gz
if [[ ${NORMALIZED:-0} == 1 ]]; then
    flags+=(--normalized)
    proof_suffix=xz
fi
proof="$job/lift.lrat.$proof_suffix"

if [[ $mode == produce ]]; then
    for depth in 6 5 0; do
        /usr/bin/time -o "$job/build.$depth.time" -f "$timefmt" \
            timeout --kill-after=2s 30s "$python" "$source" "${flags[@]}" --min-stem "$depth" "$marked" \
            "$job/stem.g6" "$job/lift.cnf" >"$job/build.log"
        rc=0
        /usr/bin/time -o "$job/solve.$depth.time" -f "$timefmt" \
            timeout --kill-after=2s "${SOLVE_WALL:-65s}" "$tools/cadical" --lrat --no-binary \
            "$job/lift.cnf" "$job/lift.lrat" >"$job/solve.log" || rc=$?
        if [[ $rc == 20 ]] && rg -Fxq 's UNSATISFIABLE' "$job/solve.log"; then
            printf '%s\n' "$depth" > "$job/depth"
            break
        fi
        if [[ $rc != 10 ]] || ! rg -Fxq 's SATISFIABLE' "$job/solve.log" || [[ $depth == 0 ]]; then
            printf 'OPEN rc=%s min_stem=%s\n' "$rc" "$depth"
            exit 1
        fi
        rm -- "$job/lift.lrat"
    done
    if [[ $proof_suffix == xz ]]; then
        /usr/bin/time -o "$job/trim.time" -f "$timefmt" \
            timeout --kill-after=2s 20s "$python" ../../ralph/lanes/B/src/high_r24_trim.py \
            "$job/lift.cnf" "$job/lift.lrat" "$job/lift.trim" >"$job/trim.log"
        mv -- "$job/lift.trim" "$job/lift.lrat"
    fi
else
    depth=$(<"$job/depth")
    /usr/bin/time -o "$job/build.$depth.time" -f "$timefmt" \
        timeout --kill-after=2s 30s "$python" "$source" "${flags[@]}" --min-stem "$depth" "$marked" \
        "$job/stem.g6" "$job/lift.cnf" >"$job/build.log"
    sha256sum --check --status "$job/archive.sha256"
    if [[ $proof_suffix == xz ]]; then
        timeout --kill-after=2s 15s xz -d -c "$proof" >"$job/lift.lrat"
    else
        timeout --kill-after=2s 15s gzip -d -c "$proof" >"$job/lift.lrat"
    fi
    sha256sum --check --status "$job/uncompressed.sha256"
fi
/usr/bin/time -o "$job/cake.time" -f "$timefmt" \
    timeout --kill-after=2s 35s "$tools/cake_lpr" "$job/lift.cnf" "$job/lift.lrat" >"$job/cake.log"
rg -Fxq 's VERIFIED UNSAT' "$job/cake.log"
/usr/bin/time -o "$job/lrat.time" -f "$timefmt" \
    timeout --kill-after=2s 35s "$tools/lrat-check" "$job/lift.cnf" "$job/lift.lrat" >"$job/lrat.log"
rg -Fxq 'c VERIFIED' "$job/lrat.log"
if [[ $mode == produce ]]; then
    sha256sum "$job/lift.cnf" "$job/lift.lrat" >"$job/uncompressed.sha256"
    /usr/bin/time -o "$job/compress.time" -f "$timefmt" \
        timeout --kill-after=2s 15s "$([[ $proof_suffix == xz ]] && echo xz || echo gzip)" -1 -c "$job/lift.lrat" >"$proof"
    sha256sum "$proof" >"$job/archive.sha256"
fi
rm -- "$job/lift.cnf" "$job/lift.lrat"
printf 'DUAL depth=%s bytes=%s profile=%s\n' "$depth" "$(stat -c %s "$proof")" "$proof_suffix"
