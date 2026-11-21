#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C
ulimit -v 16777216
if [[ $# != 1 || ! $1 =~ ^[0-7]$ ]]; then exit 2; fi
for ((index=$1; index<32; index+=8)); do
    printf -v shard '%02d' "$index"
    prefix="d5/full.$shard"
    timeout 240s ./check_maximal_prefilter 8 5 < "$prefix.in" > "$prefix.audit" 2> "$prefix.audit.log"
    sha256sum "$prefix."{in,audit,audit.log} > "$prefix.audit.sha256"
    date -Is > "$prefix.audit.done"
done
