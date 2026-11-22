#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
root=../../..
workers=()
for shard in 0 1 2 3 4 5; do
    /usr/bin/time -f 'CPU_SECONDS %U %S WALL %e' nice -n 5 timeout -k 8s 720s \
        "$root/opt/venv/bin/python" -B "$root/ralph/lanes/G/prove_pure_pivot.py" \
        pure-pivot.pending.keys proof-pure --eager 10000 --shard "$shard" 6 \
        >"proof-pure.$shard.log" 2>"proof-pure.$shard.time" &
    workers+=("$!")
    printf '%d %d\n' "$shard" "$!" >> proof-pure.worker.pids
done
status=0
for pid in "${workers[@]}"; do
    wait "$pid" || status=1
done
awk '{print $2}' proof-pure.[0-9]*.log | sort | uniq -c
date -Is
exit "$status"
