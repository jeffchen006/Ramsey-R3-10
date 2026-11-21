#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

prefix_pid=${1:?prefix supervisor PID}
prefix_tick=${2:?prefix supervisor start tick}
source_dir=../../ralph/lanes/B/src
marker='exact e86 HoG equality and GR T14 lower-level counts checked; full through e=87'
printf 'tail87 waiting for checked census from PID %s (%s) at %s\n' "$prefix_pid" "$prefix_tick" "$(date -Ins)"
while ! rg -Fq "$marker" logs/prefix_pipeline.log; do
    if [[ $(awk '{print $22}' "/proc/$prefix_pid/stat" 2>/dev/null || true) != "$prefix_tick" ]]; then
        rg -F "$marker" logs/prefix_pipeline.log || exit 1
        break
    fi
    sleep 60
done
printf 'tail87 starts from checked census at %s\n' "$(date -Ins)"
exec bash "$source_dir/edgeup_tail87.sh"
