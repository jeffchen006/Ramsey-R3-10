#!/usr/bin/env bash
set -euo pipefail
lane=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo=$(cd -- "$lane/../../.." && pwd)
work=$(realpath -m -- "${1:-$repo/scratch/C/r22-review}")
[[ $work == "$repo/scratch/C/"* ]]
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
original="$repo/scratch/C/r22"
timed selection 60 35 python3 -B "$lane/panel22_select.py" "$repo" . > selection.log
head -2 chosen.tsv > sample.tsv
timed opt-control 90 45 python3 -B "$lane/panel22_budget.py" "$repo" > opt-control.log
timed opt-sample 135 75 python3 -B "$lane/panel22_budget.py" "$repo" --cases sample.tsv --detail opt-sample.rows.tsv > opt-sample.log
timed build 120 65 g++ -std=c++17 -O3 -Wall -Wextra -Werror "$lane/panel16.cpp" -o panel16
timed old 100 60 ./panel16 "$cat16" "$cat17" chosen.tsv old.fills old.stats 9 5 9 4
timed audit 175 100 python3 -B "$lane/panel16_audit.py" audit "$cat16" "$cat17" chosen.tsv old.fills old.stats 9 5 9 4 --timing > audit.log
timed summary 25 12 python3 -B "$lane/panel22_compare.py" . "$original" > summary.log
for artifact in selection.log chosen.tsv opt-control.log opt-sample.log opt-sample.rows.tsv old.fills summary.log; do
    cmp -- "$artifact" "$original/$artifact"
done
cat summary.log
