#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
root=../../..
worker="$root/ralph/lanes/G/prove_strip_windows.py"
slots=16
workers=()
for ((index=0; index<slots; index++)); do
    /usr/bin/time -f 'CPU_SECONDS %U %S WALL %e' nice -n 5 timeout -k 8s 2400s \
        "$root/opt/venv/bin/python" -B "$worker" lowdegree25.pending.keys proof-low25 \
        --eager 10000 --cut-budget --shard "$index" "$slots" \
        >"proof-low25.$index.log" 2>"proof-low25.$index.time" &
    workers+=("$!")
    printf '%d %d\n' "$index" "$!" >> proof-low25.worker.pids
done
status=0
for worker_pid in "${workers[@]}"; do
    wait "$worker_pid" || status=1
done
awk '{print $2}' proof-low25.[0-9]*.log | sort | uniq -c
date -Is
exit "$status"
