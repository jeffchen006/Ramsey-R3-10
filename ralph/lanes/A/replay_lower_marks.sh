#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
source=../../G/round7/lowdegree25.raw.g6
tool=../path7/replay_strip_marks
shard="${1:?choose 0 or 1}"
[[ "$shard" == 0 || "$shard" == 1 ]]
count=9166691
if [[ "$shard" == 1 ]]; then
    count=9166690
fi
skip=$((shard * 9166691))
dd if="$source" iflag=skip_bytes,count_bytes bs=1M skip=$((skip*52)) count=$((count*52)) status=none |
    "$tool" 4 4 5 | awk -v offset="$skip" '{$1+=offset;print}'
