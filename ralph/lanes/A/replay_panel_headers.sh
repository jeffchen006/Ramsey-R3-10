#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
work="$root/scratch/A/r14"
mkdir -p "$work"
cd "$work"
export TMPDIR="$PWD" LC_ALL=C
ulimit -v 16777216 -c 0 -t 120
mode=${1:-packed}
extra=()
case "$mode" in
    packed) extra=(packed) ;;
    text) ;;
    *) exit 2 ;;
esac
source_dir="$root/ralph/lanes/A"
graphs="$root/gluing/val/r3_6_17.g6"
frames="$root/scratch/ideas/r012_R/frames17-5-2.txt"
run() { nice -n 5 timeout 90 "$@"; }
run g++ -O3 -Wall -Wextra -Werror -std=c++20 "$source_dir/audit_panel_headers.cpp" -o headers
run ./headers control "$root/gluing/val/r3_7_22.g6" | tee controls.log
test "$(cat controls.log)" = 'regular=10 oriented_squares=2118 frames=1336 planted=1336 nonempty_planted_squares=334 exact_smaller_headers=399584'

reject() {
    local label=$1
    shift
    local status=0
    run "$@" > "bad-${label}.stdout" 2> "bad-${label}.stderr" || status=$?
    test "$status" -eq 2 && test ! -s "bad-${label}.stdout" || exit 1
    printf '%s rejected (exit 2, no output)\n' "$label"
}
{
    reject missing-graph ./headers ./not-a-graph-input.g6 "$frames" 0 1
    reject missing-frame ./headers "$graphs" ./not-a-frame-input.txt 0 1
    head -n 55054 "$frames" > incomplete.frames
    reject truncated-frame ./headers "$graphs" incomplete.frames 0 1
    rm incomplete.frames
} | tee input-negatives.log

bind() {
    local low=$1 high=$2 digest
    digest=$(run ./headers "$graphs" "$frames" "$low" "$high" "${extra[@]}" 2>count.tmp | run sha256sum)
    printf '%s %s\n' "$(cat count.tmp)" "${digest%% *}"
}
{
    printf 'low high flip0 flip1 sha256_canonical_%s\n' "$mode"
    for (( low=0; low<55055; low+=2048 )); do
        high=$((low + 2048))
        if (( high > 55055 )); then high=55055; fi
        bind "$low" "$high"
    done
} > "headers.$mode.shards.tsv"
bind 0 55055 > "headers.$mode.full.tsv"
rm count.tmp
awk 'NR>1 {if ($1 != last || $2 <= $1) exit 1; last=$2; zero+=$3; one+=$4}
     END {if (last!=55055 || zero+one!=157472001) exit 1; print last,zero,one}' "headers.$mode.shards.tsv" \
    > totals.tmp
read -r end summed0 summed1 < totals.tmp
read -r full_low full_high full0 full1 _ < "headers.$mode.full.tsv"
test "$full_low $full_high $full0 $full1" = "0 $end $summed0 $summed1"
test "$(awk 'NR==2 {print $1,$2,$3+$4}' "headers.$mode.shards.tsv")" = '0 2048 4322749'
rm totals.tmp
cat "headers.$mode.shards.tsv" "headers.$mode.full.tsv"
