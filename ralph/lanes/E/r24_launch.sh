#!/bin/bash
set -euo pipefail
[[ $(basename "$PWD") == r24_deck ]]
slot=$1 log=$2 wall=$3 cpu=$4
shift 4
[[ "$slot" =~ ^[0-9]+$ && "$slot" -ge 0 && "$slot" -lt 22 && ! -e "$log" ]]
export LC_ALL=C TMPDIR="$PWD" PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
exec {guard}>".lease.$slot"
flock -n "$guard"
start=$(date +%s)
deadline=$(date -d "@$((start+wall+5))" -Is)
printf -v command '%q ' "$@"
setsid nohup nice -n 5 timeout -k 5s "${wall}s" bash -c '
log=$1 cpu=$2; shift 2
ulimit -v 2097152 || exit 1
ulimit -f 172032 || exit 1
/usr/bin/time -f "wall=%e cpu=%U+%S RSS=%M exit=%x" prlimit --cpu="$cpu:$((cpu+1))" -- "$@"
status=$?
printf "%s\t%s\t%s\n" "$(date -Is)" "$log" "$status" >> exits.tsv
exit "$status"
' bash "$log" "$cpu" "$@" > "$log" 2>&1 </dev/null &
wrapper=$!
printf '%s\t%s\t%s\t1\t%s\t%s\t%s\n' "$wrapper" "$(date -d "@$start" -Is)" "$deadline" "$log" "$command" "$slot" | tee -a jobs.tsv
