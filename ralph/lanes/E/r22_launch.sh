#!/bin/bash
set -euo pipefail
[[ $(basename "$PWD") == r22_shared ]]
log=$1 wall=$2 cpu=$3 file_kib=$4
shift 4
[[ ! -e "$log" ]]
export LC_ALL=C TMPDIR="$PWD"
start=$(date +%s)
deadline=$(date -d "@$((start+wall+5))" -Is)
printf -v command '%q ' "$@"
setsid nohup nice -n 5 timeout -k 5s "${wall}s" bash -c '
set -euo pipefail
log=$1 cpu=$2 files=$3; shift 3
ulimit -v 1048576
ulimit -f "$files"
set +e
/usr/bin/time -f "wall=%e cpu=%U+%S RSS=%M exit=%x" prlimit --cpu="$cpu:$((cpu+1))" -- "$@"
status=$?
printf "%s\t%s\t%s\n" "$(date -Is)" "$log" "$status" >> exits.tsv
exit "$status"
' bash "$log" "$cpu" "$file_kib" "$@" > "$log" 2>&1 </dev/null &
wrapper=$!
printf '%s\t%s\t%s\t1\t%s\t%s\n' "$wrapper" "$(date -d "@$start" -Is)" "$deadline" "$log" "$command" | tee -a jobs.tsv
