#!/usr/bin/env bash
set -euo pipefail
diagonal=$1
shard=$2
lane=../../ralph/lanes/C
python=../../opt/venv/bin/python
catalogue=../../gluing/val/r3_7_22.g6
bin=../../opt/bin
work=p3flex-pilot
prefix=p3r5-e64-$diagonal-$shard
ulimit -v 16777216
arguments=("$catalogue" "$bin" "$work" --diagonal "$diagonal" --edges 64 --shards 3 --shard "$shard")
pilot=(--skip-row 0 --skip-row 95 --skip-row 139 --skip-row 163)
"$python" -B "$lane/p3_flexible.py" "${arguments[@]}" "${pilot[@]}" --seconds 65 --produce > "$prefix-produce.log"
mapfile -t rows < <(awk '$1=="row" && $3=="checked" {print $2}' "$prefix-produce.log")
for row in 0 95 139 163; do
    if (( row % 3 == shard )); then rows+=("$row"); fi
done
if (( ${#rows[@]} )); then
    reuse=()
    for row in "${rows[@]}"; do reuse+=(--row "$row"); done
    "$python" -B "$lane/p3_flexible.py" "${arguments[@]}" "${reuse[@]}" --verify > "$prefix-replay.log"
else
    printf 'EMPTY no checked keys to replay\n' > "$prefix-replay.log"
fi
