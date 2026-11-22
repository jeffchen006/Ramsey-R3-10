#!/bin/bash
set -euo pipefail
[[ $(basename "$PWD") == r20_shared ]]
wall=$1 cpu=$2 log=$3
shift 3
export LC_ALL=C TMPDIR="$PWD"
[[ ! -e "$log" ]]
nice -n 5 /usr/bin/time -f 'wall=%e cpu=%U+%S RSS=%M' timeout -k 2s "${wall}s" \
    prlimit --as=1073741824:1073741824 --cpu="$cpu:$((cpu+1))" \
    --fsize=8388608:8388608 -- "$@" >"$log" 2>&1 &
child=$!
printf -v command '%q ' "$@"
start=$(date +%s)
end=$(date -d "@$((start+wall+2))" -Is)
printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t1\n' "$child" "$(date -d "@$start" -Is)" "$wall" "$cpu" "$log" "$command" "$end" >>jobs.tsv
if wait "$child"; then result=0; else result=$?; fi
printf '%s\t%s\t%s\t%s\n' "$child" "$(date -Is)" "$result" "$log" >>exits.tsv
exit "$result"
