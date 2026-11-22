#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
root=../../..
source_dir=$root/ralph/lanes/G
export PYTHONDONTWRITEBYTECODE=1
[[ "$PWD" == */scratch/G/round12 ]]
slots="$1"
pids=()
for ((rank=0; rank<slots; ++rank)); do
    /usr/bin/time -o "b.middle.static.$rank.time" nice -n 5 timeout 750s \
        "$root/opt/venv/bin/python" -B "$source_dir/mini_reroot_column.py" ../round10/short-anchor.full.keys \
        --selection b.middle.static.selection --shard "$rank" "$slots" --limit 6500 --no-column \
        --proof-dir b.middle.static.proof > "b.middle.static.$rank.log" 2>&1 &
    pids+=("$!")
done
printf '%s\n' "${pids[@]}" > b.middle.static.worker.pids
code=0
for pid in "${pids[@]}"; do
    wait "$pid" || code=1
done
awk '{status[$4]++} END {for (key in status) print key,status[key]}' b.middle.static.[0-9]*.log | sort
exit "$code"
