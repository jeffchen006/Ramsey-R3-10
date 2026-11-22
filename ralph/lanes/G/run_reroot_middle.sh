#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
root=../../..
src=$root/ralph/lanes/G
export PYTHONDONTWRITEBYTECODE=1
[[ "$PWD" == */scratch/G/round12 ]]
slots="$1"
pids=()
for ((rank=0; rank<slots; ++rank)); do
    /usr/bin/time -o "b.middle.$rank.time" nice -n 5 timeout 2200s \
        "$root/opt/venv/bin/python" -B "$src/mini_reroot.py" ../round10/short-anchor.full.keys full.v2.map \
        --type B.25.middle --type B.26.middle --selection b.middle.selection --shard "$rank" "$slots" \
        --limit 6500 --eager --sorted-groups --proof-dir b.middle.proof > "b.middle.$rank.log" 2>&1 &
    pids+=("$!")
done
printf '%s\n' "${pids[@]}" > b.middle.worker.pids
code=0
for pid in "${pids[@]}"; do
    wait "$pid" || code=1
done
awk '{status[$4]++} END {for (key in status) print key,status[key]}' b.middle.[0-9]*.log | sort
exit "$code"
