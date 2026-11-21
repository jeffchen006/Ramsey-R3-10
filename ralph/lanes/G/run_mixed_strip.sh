#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
root=../../..
workers=()
for index in 0 1; do
    /usr/bin/time -f 'CPU_SECONDS %U %S WALL %e' nice -n 5 timeout -k 8s 4800s \
        "$root/opt/venv/bin/python" -B "$root/ralph/lanes/G/prove_strip_windows.py" \
        mixed-j4.pending.keys proof-mixed --mixed --eager 10000 --shard "$index" 2 \
        >"proof-mixed.$index.log" 2>"proof-mixed.$index.time" &
    workers+=("$!")
    printf '%d %d\n' "$index" "$!" >> proof-mixed.worker.pids
done
status=0
for worker_pid in "${workers[@]}"; do
    wait "$worker_pid" || status=1
done
awk '{print $2}' proof-mixed.[0-9]*.log | sort | uniq -c
date -Is
exit "$status"
