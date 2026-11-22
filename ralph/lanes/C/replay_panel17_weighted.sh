#!/usr/bin/env bash
set -euo pipefail
lane=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo=$(cd -- "$lane/../../.." && pwd)
mode=${1:-controls}
work=${2:-$repo/scratch/C/r17-replay}
weights=${3:-$repo/scratch/A/r17-stream}
case $mode in controls|stratum|full) ;; *) exit 2 ;; esac
work=$(realpath -m -- "$work")
[[ $work == "$repo/scratch/C/"* ]]
mkdir -p -- "$work"
cd -- "$work"
test -z "$(ls -A)"
export TMPDIR=$PWD LC_ALL=C
ulimit -v 524288 -f 262144 -c 0
timed() {
    local tag=$1 wall=$2 soft=$3 hard=$4
    shift 4
    nice -n 5 timeout "$wall" prlimit --cpu="$soft:$hard" /usr/bin/time -o "$tag.time" -f '%U %S %e %M' "$@"
}
small="$repo/scratch/A/r16"
prior="$repo/scratch/C/r16"
cat16="$repo/gluing/val/r3_6_16.g6"
cat17="$repo/gluing/val/r3_6_17.g6"
audit="$lane/panel17_audit.py"
timed build 75 55 60 g++ -std=c++17 -O3 -Wall -Wextra -pedantic -Werror "$lane/panel17_weighted.cpp" -o panel17
timed small-prepare 40 25 30 python3 -B "$audit" small-prepare "$small"/{small6,small7}.g6 "$small"/{small6,small7}.frames small.weights small.cases small.literal > small-prepare.log
timed small-cases 40 25 30 ./panel17 CASES "$small"/{small6,small7}.g6 small.cases small.cases.groups 5 4 5 2 > small.cases.log
timed small-count 40 25 30 ./panel17 COUNT "$small"/{small6,small7}.g6 small.weights small.groups.tsv 5 4 5 2 small.buckets.tsv > small.count.log
timed small-check 40 25 30 python3 -B "$audit" small-check "$small"/{small6,small7}.frames small.literal small.cases.log small.buckets.tsv > small.check.log
timed pilot 60 45 50 ./panel17 CASES "$cat16" "$cat17" "$prior/bound.cases.tsv" pilot.groups.tsv 9 5 9 4 > pilot.log
timed pilot-audit 235 190 200 python3 -B "$audit" pilot "$cat16" "$cat17" "$prior/bound.cases.tsv" "$prior/pilot.stats" pilot.log > pilot.audit.log
if [[ $mode != controls ]]; then
    declare -a filter=()
    test -s "$weights/weights16.tsv" && test -s "$weights/weights17.tsv"
    if [[ $mode == stratum ]]; then filter=(71 5); fi
    merge_weights() { cat "$weights/weights16.tsv" && tail -n +2 "$weights/weights17.tsv"; }
    timed target-count 420 320 330 ./panel17 COUNT "$cat16" "$cat17" <(merge_weights) target.groups.tsv 9 5 9 4 target.buckets.tsv "${filter[@]}" > target.count.log
    timed target-arith 120 85 90 python3 -B "$audit" target-arith <(merge_weights) "$small/strata.tsv" target.count.log target.buckets.tsv > target.arith.log
    timed target-receipts 120 85 90 python3 -B "$audit" receipts "$cat16" "$cat17" target.groups.tsv 6 > target.receipts.log
    timed forward-zero 120 85 90 python3 -B "$audit" forward-zero <(merge_weights) "$cat17" 71 5 > forward-zero.log
fi
