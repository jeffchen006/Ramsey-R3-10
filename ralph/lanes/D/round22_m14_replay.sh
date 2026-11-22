#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
lane="$root/ralph/lanes/D"; base="$root/scratch/D/m14r22"; python="$root/opt/venv/bin/python"
work=$(realpath -m "${1:?give a new directory in your own scratch}"); shift
workers=${1:-2}; [[ $workers =~ ^([1-9]|1[0-9]|2[0-4])$ ]]; if (( $# )); then shift; fi
mkdir "$work"; cd "$work"; export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 2097152; ulimit -t 17500
(cd "$root"; sha256sum --quiet -c "$lane/ROUND22_M14.sha256")
nice -n 5 timeout 180 "$python" -B "$lane/m14verify22.py"
nice -n 5 timeout 180 "$python" -B "$lane/prefix22_audit.py" D_471 D_474 D_2478 D_5011 D_5247
if (( $# )); then printf '%s\n' "$@" > keys; else awk '$2~/^D_/{print $2}' "$base/dispatch.tsv" > keys; [[ $(wc -l < keys) == 539 ]]; fi
for ((shard=0;shard<workers;shard++)); do
    mapfile -t keys < <(awk -v i="$shard" -v n="$workers" '(NR-1)%n==i{print}' keys)
    if (( ${#keys[@]} )); then nice -n 5 timeout -k 10 18000 "$python" -B "$lane/m14replay22.py" "$work/shard$shard" "${keys[@]}" >"$work/check$shard.log" & pids[$shard]=$!; fi
done
for pid in "${pids[@]}"; do wait "$pid"; done
printf 'dual replay: %s leaves on %s keys\n' "$(cat check*.log | wc -l)" "$(wc -l < keys)"
