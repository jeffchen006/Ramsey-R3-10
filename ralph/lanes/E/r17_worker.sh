#!/bin/bash
set -euo pipefail
[[ $(basename "$PWD") == r17_shared ]]
lane=../../../ralph/lanes/E
export LC_ALL=C E_FILE_BLOCKS=8192
wall=$1 cpu=$2 log=$3
shift 3
[[ ! -e "$log" ]]
nice -n 5 timeout -k 8s "${wall}s" bash "$lane/limited.sh" "$cpu" "$@" >"$log" 2>&1 &
child=$!
printf -v command '%q ' "$@"
start=$(date +%s)
end=$(date -d "@$((start+wall+8))" -Is)
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t1\n' "$child" "$(date -d "@$start" -Is)" "$wall" "$cpu" "$log" "$command" "$end" >>jobs.tsv
if wait "$child"; then result=0; else result=$?; fi
printf '%s\t%s\t%s\t%s\n' "$child" "$(date -Is)" "$result" "$log" >>exits.tsv
exit "$result"
