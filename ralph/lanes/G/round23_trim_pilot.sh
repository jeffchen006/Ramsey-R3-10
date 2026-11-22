#!/usr/bin/env bash
set -euo pipefail
root=$(realpath "$(dirname "$0")/../../..")
base="$root/scratch/G/round23"
test "$PWD" = "$base/trim"
ulimit -v 5242880
run() {
    local timer=$1
    shift
    /usr/bin/time -o "$timer" -f '%U %S %M %e %x' timeout --kill-after=5 125 prlimit --cpu=80:80 -- "$@"
}
for id in "$@"; do
    cnf="$base/work/$id/grid.cnf"
    original="$base/archive/$id.lrat.zst"
    count=$(awk 'NR==1{print $4}' "$cnf")
    run "$id.unzip.time" zstd -q -d "$original" -o "$id.orig.lrat"
    run "$id.slice.time" ./slice_lrat "$count" "$id.orig.lrat" "$id.trim.lrat" >"$id.slice.log" 2>&1
    run "$id.lrat.time" "$root/opt/bin/lrat-check" "$cnf" "$id.trim.lrat" >"$id.lrat.log"
    run "$id.cake.time" "$root/opt/bin/cake_lpr" --CML_HEAP_SIZE=512 --CML_STACK_SIZE=48 "$cnf" "$id.trim.lrat" >"$id.cake.log"
    rg -qx 'c VERIFIED' "$id.lrat.log" && rg -qx 's VERIFIED UNSAT' "$id.cake.log"
    run "$id.zstd.time" zstd -q -3 -T1 "$id.trim.lrat" -o "$id.trim.lrat.zst"
    printf '%s %s %s %s %s\n' "$id" "$(stat -c %s "$id.orig.lrat")" "$(stat -c %s "$id.trim.lrat")" \
        "$(stat -c %s "$original")" "$(stat -c %s "$id.trim.lrat.zst")"
    sha256sum "$id.trim.lrat" "$id.trim.lrat.zst" >"$id.sha256"
    rm "$id.orig.lrat" "$id.trim.lrat"
done
