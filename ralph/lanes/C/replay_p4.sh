#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "$0")/../../.." && pwd -P)
lane="$root/ralph/lanes/C"
cd "$root/scratch/C"
ulimit -v 16777216

case "${1:-}" in
    high) mode=(--min-e 79 --join) ;;
    low) mode=(--max-e 78 --pins) ;;
    *) echo "usage: bash replay_p4.sh {high|low} SHARD" >&2; exit 2 ;;
esac
part=$1
shard=${2:-}
case "$shard" in 0|1|2|3) ;; *) exit 2;; esac
original="p4proof-$part-$shard.log"
replayed="p4replay-$part-$shard.log"

nice -n 5 timeout 900 python3 -B "$lane/p4_factor_proofs.py" p4_forced_full.g6 \
    "$root/opt/bin" "p4proof-$part" --verify "${mode[@]}" --shards 4 --shard "$shard" >"$replayed"
awk '/^row / && $5 == "checked" {print $1,$2,$3,$4,$5,$6,$7,$8,$9,$10}' "$original" >"$replayed.orig-index"
awk '/^row / && $5 == "checked" {print $1,$2,$3,$4,$5,$6,$7,$8,$9,$10}' "$replayed" >"$replayed.new-index"
test -s "$replayed.orig-index"
diff -u "$replayed.orig-index" "$replayed.new-index"
if rg -q '^row .* unresolved' "$replayed"; then
    echo "replay has unresolved rows" >&2
    exit 1
fi
printf 'IDENTICAL %s shard %s (%s checked CNFs)\n' "$part" "$shard" "$(wc -l <"$replayed.new-index")"
