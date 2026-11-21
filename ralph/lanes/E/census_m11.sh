#!/bin/bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
lane=$root/ralph/lanes/E
core=$1
shift
cpu=${CENSUS_CPU:-105}
limited() {
    local budget=$1
    shift
    nice -n 5 timeout "$((budget + 155))" bash "$lane/limited.sh" "$budget" "$@"
}
limited "$cpu" python3 -B "$lane/m11_support.py" census ../r5_saturated/e11.g6 "cover.$core.jsonl" --core "$core" "$@"
limited "${SCAN_CPU:-100}" python3 -B "$lane/m11_prop.py" m11_prop.so scan "cover.$core.jsonl" "checked.$core.jsonl"
wc -lc "cover.$core.jsonl" "checked.$core.jsonl"
