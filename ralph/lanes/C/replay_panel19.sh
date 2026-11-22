#!/usr/bin/env bash
set -euo pipefail
lane=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo=$(cd -- "$lane/../../.." && pwd)
work=$(realpath -m -- "${1:-$repo/scratch/C/r19-replay}")
source=$(realpath -- "${2:-$repo/scratch/A/r19}")
[[ $work == "$repo/scratch/C/"* && $source == "$repo/scratch/A/"* ]]
mkdir -p -- "$work"
cd -- "$work"
test -z "$(ls -A)"
unset PYTHONOPTIMIZE
export TMPDIR=$PWD LC_ALL=C
ulimit -v 524288 -f 131072 -c 0
timed() {
    local name=$1 wall=$2 cpu=$3
    shift 3
    nice -n 5 timeout "$wall" prlimit --cpu="$cpu:$((cpu+2))" /usr/bin/time -o "$name.time" -f '%U %S %e %M' "$@"
}
cat16="$repo/gluing/val/r3_6_16.g6"
cat17="$repo/gluing/val/r3_6_17.g6"
timed controls-final 100 50 python3 -B "$lane/panel19_fifth.py" control > controls-final.log
timed build-frames 80 45 g++ -std=c++20 -O3 -Wall -Wextra -Werror "$repo/ralph/lanes/A/one_neutral_frames.cpp" -o frames
timed build-baseline 95 60 g++ -std=c++17 -O3 -Wall -Wextra -Werror "$lane/panel16.cpp" -o panel16
timed frames16 80 40 ./frames frames "$cat16" 16 2576 4 9 5 5 0 98 > frames16.tsv
timed frames17 80 40 ./frames frames "$cat17" 17 7 4 9 5 5 0 7 > frames17.tsv
timed binding 80 40 python3 -B "$lane/panel19_bind.py" "$cat16" "$cat17" frames16.tsv frames17.tsv \
    "$repo/scratch/C/r16/bound.cases.tsv" "$repo/scratch/critic/R18/survivors.cases" "$source" pilot.tsv > binding.log
timed baseline 90 60 ./panel16 "$cat16" "$cat17" pilot.tsv baseline.fills baseline.stats 9 5 9 4
for mode in indexed literal; do
    timed "$mode" 120 70 python3 -B "$lane/panel19_fifth.py" "$mode" --cat16 "$cat16" --cat17 "$cat17" \
        --cases pilot.tsv --root 0 --indexed "$source/cards-v1.json" --detail "$mode.rows.tsv" \
        --card-detail "$mode.cards.tsv" > "$mode.log"
done
timed signed-audit 180 110 python3 -B "$lane/panel16_audit.py" audit "$cat16" "$cat17" \
    pilot.tsv baseline.fills baseline.stats 9 5 9 4 --timing > signed-audit.log
timed summary 30 15 python3 -B "$lane/panel19_summary.py" . > summary.log
cat summary.log
