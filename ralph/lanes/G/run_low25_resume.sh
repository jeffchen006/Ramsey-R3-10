#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
root=../../..
source_dir="$root/ralph/lanes/G"
workers=()
for ((index=0; index<16; index++)); do
    /usr/bin/time -f 'CPU_SECONDS %U %S WALL %e' nice -n 5 timeout -k 8s 2250s \
        "$root/opt/venv/bin/python" -B "$source_dir/prove_strip_windows.py" c1.first/unclosed.keys proof-c1retry \
        --eager 10000 --cut-budget --shard "$index" 16 >"proof-c1retry.$index.log" 2>"proof-c1retry.$index.time" &
    workers+=("$!")
    printf '%d %d\n' "$index" "$!" >> proof-c1retry.worker.pids
done
status=0
for pid in "${workers[@]}"; do
    wait "$pid" || status=1
done
awk '{print $2}' proof-c1retry.[0-9]*.log | sort | uniq -c
date -Is
exit "$status"
