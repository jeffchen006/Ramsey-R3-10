#!/usr/bin/env bash
set -euo pipefail
ulimit -c 0
ulimit -v 16777216

if [[ $# != 7 ]]; then
    printf 'usage: %s EXE H19 H21 LIST OUT WALL CPU\n' "$0" >&2
    exit 2
fi

exe=$1
small=$2
large=$3
list=$4
out=$5
wall=$6
cpu=$7
mkdir "$out"
while IFS=$'\t' read -r maps profile; do
    [[ "$maps" =~ ^[1-9][0-9]*$ && "$profile" =~ ^[0-9]+(,[0-9]+){6}$ ]]
    printf '%s start %s maps=%s\n' "$(date +%FT%T)" "$profile" "$maps"
    timeout "$wall" prlimit --cpu="$cpu" -- "$exe" cover "$small" "$large" \
        "$out/$profile.tsv.partial" "$maps" "$profile" >"$out/$profile.log.partial" 2>&1
    mv -- "$out/$profile.tsv.partial" "$out/$profile.tsv"
    mv -- "$out/$profile.log.partial" "$out/$profile.log"
    printf '%s done %s\n' "$(date +%FT%T)" "$profile"
done < "$list"
printf '%s all profiles terminal\n' "$(date +%FT%T)"
