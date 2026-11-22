#!/bin/bash
set -euo pipefail
[[ $(basename "$PWD") == r13_shared ]]
lane=../../../ralph/lanes/E
export LC_ALL=C
wall=$1 cpu=$2 log=$3
shift 3
[[ ! -e "$log" ]]
nice -n 5 timeout -k 8s "$wall" bash "$lane/limited.sh" "$cpu" "$@" >"$log" 2>&1 &
child=$!
printf -v command '%q ' "$@"
printf '%s\t%s\t%s\t%s\t%s\n' "$child" "$(date -Is)" "$wall" "$log" "$command" >>jobs.tsv
wait "$child"
