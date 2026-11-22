#!/bin/bash
set -eu
here=$(cd "$(dirname "$0")" && pwd); root=$(cd "$here/../../.." && pwd)
case "$PWD" in "$root"/scratch/F/*) ;; *) exit 2;; esac
ulimit -v 524288
name=$1; cpu=$2; shift 2
start=$(date -Is);end=$(date -d "+$((cpu+10)) seconds" -Is)
/usr/bin/time -f '%U %S %M %x' -o "$name.time" nice -n 5 timeout "$((cpu+10))" prlimit --cpu="$cpu" -- "$@" > "$name.stdout" 2>&1 &
pid=$!;printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$name" "$pid" "$start" "$end" 1 "$*" >> jobs.tsv
wait "$pid"
