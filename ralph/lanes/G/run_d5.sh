#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
ulimit -v 16777216

if [[ $# != 1 || ! $1 =~ ^[0-7]$ ]]; then exit 2; fi
for ((index=$1; index<32; index+=8)); do
    printf -v shard '%02d' "$index"
    prefix="d5/full.$shard"
    [[ ! -e "$prefix.done" ]] || exit 3
    timeout 300s ./maximal_prefilter 8 5 < "$prefix.in" > "$prefix.max" 2> "$prefix.max.log"
    timeout 300s ./glue6 -k 8 -d 5 -m 5 -e 121 < "$prefix.max" > "$prefix.out" 2> "$prefix.out.log"
    sha256sum "$prefix."{in,max,out,max.log,out.log} > "$prefix.sha256"
    date -Is > "$prefix.done"
done
