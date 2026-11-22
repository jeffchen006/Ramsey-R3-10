#!/usr/bin/env bash
set -euo pipefail
lane=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo=$(cd -- "$lane/../../.." && pwd)
work=$(realpath -m -- "${1:-$repo/scratch/C/r18-replay}")
source=$(realpath -- "${2:-$repo/scratch/A/r18}")
[[ $work == "$repo/scratch/C/"* && $source == "$repo/scratch/A/"* ]]
mkdir -p -- "$work"
cd -- "$work"
test -z "$(ls -A)"
unset PYTHONOPTIMIZE
export TMPDIR=$PWD LC_ALL=C
ulimit -v 524288 -f 262144 -c 0
timed() {
    local name=$1 wall=$2 cpu=$3
    shift 3
    nice -n 5 timeout "$wall" prlimit --cpu="$cpu:$((cpu+2))" /usr/bin/time -o "$name.time" -f '%U %S %e %M' "$@"
}
prior="$repo/scratch/C/r16"
weighted="$repo/scratch/C/r17"
a_small="$repo/scratch/A/r16"
a_weights="$repo/scratch/A/r17-stream"
cat16="$repo/gluing/val/r3_6_16.g6"
cat17="$repo/gluing/val/r3_6_17.g6"
timed build 85 60 g++ -std=c++17 -O3 -Wall -Wextra -Werror "$lane/panel16.cpp" -o panel16
timed native-controls 45 25 ./panel16 "$prior/control6.g6" "$prior/control7.g6" "$prior/controls.tsv" controls.fills controls.stats 5 4 5 2
timed audit-controls 45 25 python3 -B "$lane/panel16_audit.py" audit "$prior/control6.g6" "$prior/control7.g6" "$prior/controls.tsv" controls.fills controls.stats 5 4 5 2 --plants "$prior/plants.tsv" > audit-controls.log
timed bound-control 45 25 python3 -B "$lane/panel18_bind.py" control "$prior/control6.g6" "$prior/control7.g6" "$prior/controls.tsv" "$prior/plants.tsv" controls.fills > bound-control.log
timed marginal-control 50 30 python3 -B "$lane/panel18_marginals.py" control "$a_small/small6.g6" "$a_small/small7.g6" "$a_weights/small.weights6.tsv" "$a_weights/small.weights7.tsv" "$weighted/small.buckets.tsv" marginal-control.buckets.tsv --receipts "$source/small/receipts.tsv" > marginal-control.log
timed bound-target 30 20 python3 -B "$lane/panel18_bind.py" target "$cat16" "$cat17" "$source/survivors.cases.tsv" "$weighted/target.count.log" "$prior/bound.cases.tsv" "$source/survivors.tsv" target.groups.tsv > bound-target.log
timed native-target 90 60 ./panel16 "$cat16" "$cat17" "$source/survivors.cases.tsv" target.fills target.stats 9 5 9 4
timed audit-target 510 300 python3 -B "$lane/panel16_audit.py" audit "$cat16" "$cat17" "$source/survivors.cases.tsv" target.fills target.stats 9 5 9 4 --timing > audit-target.log
timed marginal-target 240 180 python3 -B "$lane/panel18_marginals.py" target "$cat16" "$cat17" "$a_weights/weights16.tsv" "$a_weights/weights17.tsv" "$source/survivors.cases.tsv" marginal-target.buckets.tsv --receipts "$source/receipts.tsv" > marginal-target.log
timed summary 30 15 python3 -B "$lane/panel18_summary.py" "$source" "$prior" . > summary.log
cat summary.log
