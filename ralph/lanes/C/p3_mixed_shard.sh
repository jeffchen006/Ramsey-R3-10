#!/usr/bin/env bash
set -euo pipefail
diagonal=$1
shard=$2
lane=../../ralph/lanes/C
python=../../opt/venv/bin/python
catalogue=../../gluing/val/r3_7_22.g6
bin=../../opt/bin
work=p3r5-mixed
prefix=p3r5-mixed-$diagonal-$shard
ulimit -v 16777216
arguments=("$catalogue" "$bin" "$work" --diagonal "$diagonal" --shards 3 --shard "$shard")
pilots=(13 44 79 133)
skip=()
for row in "${pilots[@]}"; do skip+=(--skip-row "$row"); done
"$python" -B "$lane/p3_mixed_arms.py" "${arguments[@]}" "${skip[@]}" --seconds 75 > "$prefix-produce.log"
mapfile -t rows < <(awk '$1=="row" && $3=="checked" {print $2}' "$prefix-produce.log")
for row in "${pilots[@]}"; do
    if (( row % 3 == shard )); then rows+=("$row"); fi
done
if (( ${#rows[@]} )); then
    reuse=()
    for row in "${rows[@]}"; do reuse+=(--row "$row"); done
    "$python" -B "$lane/p3_mixed_arms.py" "${arguments[@]}" "${reuse[@]}" --verify > "$prefix-replay.log"
else
    printf 'EMPTY no checked keys to replay\n' > "$prefix-replay.log"
fi
