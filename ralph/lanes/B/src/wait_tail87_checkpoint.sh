#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1

e43_pid=${1:?e43 supervisor PID}
e43_tick=${2:?e43 supervisor start tick}
source_dir=../../ralph/lanes/B/src
rg -Fxq 'e86 checkpoint exact HoG equality' logs/prefix_checkpoint_r4.log
rg -Fxq 'e87 checkpoint union reaches exact published count' logs/prefix_checkpoint_r4.log
printf 'checkpoint ready; tail87 waiting for e43 PID %s (%s) at %s\n' "$e43_pid" "$e43_tick" "$(date -Ins)"
while [[ $(awk '{print $22}' "/proc/$e43_pid/stat" 2>/dev/null || true) == "$e43_tick" ]]; do
    sleep 30
done
printf 'tail87 starts from the exact checkpoint at %s\n' "$(date -Ins)"
exec bash "$source_dir/edgeup_tail87.sh" checkpoint
