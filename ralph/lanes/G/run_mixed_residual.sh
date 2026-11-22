#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
root=../../..
prefix=$1
slots=$2
wall=$3
conflicts=$4
cpu=$5
shift 5
workers=()
for ((index=0; index<slots; index++)); do
    /usr/bin/time -f 'CPU_SECONDS %U %S WALL %e' nice -n 5 timeout -k 8s "$wall" \
        "$root/opt/venv/bin/python" -B "$root/ralph/lanes/G/prove_strip_windows.py" \
        "$prefix.keys" "$prefix" --mixed --residual --eager 10000 --conflicts "$conflicts" --cpu "$cpu" \
        --shard "$index" "$slots" "$@" >"$prefix.$index.log" 2>"$prefix.$index.time" &
    workers+=("$!")
    printf '%d %d\n' "$index" "$!" >>"$prefix.worker.pids"
done
status=0
for worker_pid in "${workers[@]}"; do
    wait "$worker_pid" || status=1
done
awk '{print $2}' "$prefix".[0-9]*.log | sort | uniq -c
date -Is
exit "$status"
