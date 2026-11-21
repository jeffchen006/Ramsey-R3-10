#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

slice_pid=${1:?running one-core up86 supervisor}
slice_tick=${2:?start tick of that supervisor}
level=${3:?e43 or e44}
source_dir=../../ralph/lanes/B/src
printf 'queued behind PID %s (%s) at %s\n' "$slice_pid" "$slice_tick" "$(date -Ins)"
while [[ $(awk '{print $22}' "/proc/$slice_pid/stat" 2>/dev/null || true) == "$slice_tick" ]]; do
    sleep 30
done
printf 'starting d7 tail level %s at %s\n' "$level" "$(date -Ins)"
exec /usr/bin/time -f 'tail CPU %U+%S wall %e' python3 "$source_dir/n30_tail7.py" "$level" --workers 1
