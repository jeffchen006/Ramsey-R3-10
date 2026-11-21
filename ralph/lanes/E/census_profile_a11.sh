#!/bin/bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
lane=$root/ralph/lanes/E
offset=$1
stride=$2

limited() {
    local budget=$1
    shift
    nice -n 5 timeout "$((budget+65))" bash "$lane/limited.sh" "$budget" "$@"
}

for ((core=offset; core<19; core+=stride)); do
    if [[ $core =~ ^(0|9|18)$ ]]; then continue; fi
    limited 25 python3 -B "$lane/profile_a11.py" census ../r5_saturated/e11.g6 --core "$core" --manifest "cover.a$core.jsonl"
    limited 25 python3 -B "$lane/profile_a11.py" verify ../r5_saturated/e11.g6 --core "$core" --manifest "cover.a$core.jsonl"
    limited 45 python3 -B "$lane/m11_prop.py" m11_prop.so scan "cover.a$core.jsonl" "checked.a$core.jsonl" --projection-only
    wc -l "cover.a$core.jsonl" "checked.a$core.jsonl"
done
