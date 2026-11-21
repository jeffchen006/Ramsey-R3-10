#!/bin/bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
lane=$root/ralph/lanes/E
tools=$root/opt/bin
shard=$1
stride=$2

limited() {
    local budget=$1
    shift
    nice -n 5 timeout "$((budget + 125))" bash "$lane/limited.sh" "$budget" "$@"
}

awk -v shard="$shard" -v stride="$stride" '(NR-1)%stride==shard' addswap2.g6 > "pair.$shard.inputs.g6"
limited 70 python3 -B "$lane/pairlift74.py" puncture "pair.$shard.inputs.g6" |
    limited 55 "$tools/shortg" -q > "pair.$shard.parents.g6"
limited 80 ./pairlift74 7 74 < "pair.$shard.parents.g6" |
    cat addswap2.g6 - | limited 60 "$tools/shortg" -q > "pair.$shard.g6"
comm -13 addswap2.g6 "pair.$shard.g6" > "pair.$shard.new.g6"
wc -l "pair.$shard"*.g6
