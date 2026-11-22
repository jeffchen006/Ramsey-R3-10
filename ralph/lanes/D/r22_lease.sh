#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
lane="$root/ralph/lanes/D"; base="$root/scratch/D/m14r22"; shard=$1; shift
parent=$(awk -v i="$shard" '$1==i{print $2}' "$base/pids.tsv")
[[ $(ps -o args= -p "$parent") == "$root/opt/venv/bin/python -B $lane/m14queue22.py worker $shard" ]]
cd "$base"
trap 'kill -CONT "$parent"' EXIT
kill -STOP "$parent"
while ps -o state= --ppid "$parent" | rg -q '[^ Z]'; do sleep .5; done
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 2097152; ulimit -t 3600
if [[ ${1:-} == replay ]]; then
    shift
    /usr/bin/time -f '%U %S %e %M' -o "audit$shard.time" nice -n 5 timeout -k 12 1800 "$root/opt/venv/bin/python" -B "$lane/m14replay22.py" "archive$shard" "$@" >"audit$shard.log" 2>&1
else
    /usr/bin/time -f '%U %S %e %M' -o "lease$shard.time" nice -n 5 timeout -k 12 1800 "$root/opt/venv/bin/python" -B "$lane/prefix22.py" work "$@" >"lease$shard.log" 2>&1
fi
