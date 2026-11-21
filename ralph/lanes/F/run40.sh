#!/usr/bin/env bash
set -eu
tag=$1; shift
rc=0
"${F_LS:-../build/ls_sym}" -n 40 -k 10 -w9 0 -maxdeg 9 -out "$tag" "$@" &
solver=$!
printf '%s\n' "$solver" > "$tag.solver.pid"
wait "$solver" || rc=$?
if [[ -s $tag.found.g6 ]]; then
    python3 -B ../../../ralph/lanes/F/audit.py --publish "$tag.found.g6"
fi
exit "$rc"
