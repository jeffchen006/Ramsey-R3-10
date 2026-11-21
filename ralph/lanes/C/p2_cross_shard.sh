#!/usr/bin/env bash
set -euo pipefail
ulimit -c 0
ulimit -v 16777216
shard=$1
work=$2
shift 2
mkdir -p "$work"
exec /usr/bin/time -p python3 -B ../../ralph/lanes/C/p2_cross_cert.py run ../../opt/bin "$work" \
    "${WINDOWS:-p2r5-strong21.tsv}" "${CASES:-p2r6-window21-cross.tsv}" \
    --begin "$shard" --step 4 "$@"
