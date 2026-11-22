#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
lane="$root/ralph/lanes/D"
store="$root/scratch/D/closure22"
python="$root/opt/venv/bin/python"
work=$(realpath -m "${1:?give a NEW audit directory in your own scratch}")
workers=${2:-2}
[[ $workers =~ ^([1-9]|1[0-9]|2[0-4])$ ]]
mkdir "$work"; cd "$work"
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
ulimit -v 2097152; ulimit -t 10000
(cd "$root"; sha256sum --quiet -c "$lane/ROUND22_FREEZE.sha256")
nice -n 5 timeout 180 "$python" -B "$root/scratch/ideas/r021_R/rebind.py" --cal
nice -n 5 timeout 120 "$python" -B "$lane/closure22_audit.py" > cover.txt
cmp cover.txt "$store/cover.txt"
for ((shard=0;shard<workers;shard++)); do
    mapfile -t hosts < <(awk -v i="$shard" -v n="$workers" 'NR%n==i {print $2}' "$store/manifest.tsv")
    nice -n 5 timeout -k 10 10800 "$python" -B "$lane/closure22_audit.py" "$work/shard$shard" "${hosts[@]}" >"$work/replay$shard.log" &
    ids[$shard]=$!
done
for pid in "${ids[@]}"; do wait "$pid"; done
[[ $(cat replay*.log | wc -l) == 149 ]]
printf 'Verified all 149 newly rebound unpinned m=15 proofs, not 149 edge kernels.\n'
