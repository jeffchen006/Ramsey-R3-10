#!/usr/bin/env bash
set -euo pipefail
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
ulimit -v 16777216
ulimit -t 85
ulimit -f 12288
root=$(cd "$(dirname "$0")/../../../.." && pwd)
base="$root/scratch/B/work/e108_r24_high"
rank=${1:?frozen rank}
output=${2:?new replay directory in caller scratch}
receipt=${3:-$base/e48.terminal.tsv}
[[ $rank =~ ^[1-9][0-9]*$ ]]
record=$(awk -F'\t' -v rank="$rank" '$1==rank {print; count++} END {exit count!=1}' "$receipt")
IFS=$'\t' read -r indexed level marked stem payload digest cnf_hash lrat_hash cpu <<< "$record"
[[ $indexed == "$rank" && $level =~ ^4[89]$ && $marked =~ ^[0-9]+(,[0-9]+){3}$ ]]
[[ $digest =~ ^[a-f0-9]{64}$ && $cnf_hash =~ ^[a-f0-9]{64}$ && $lrat_hash =~ ^[a-f0-9]{64}$ ]]
archive="$base/normalized/$rank/lift.lrat.xz"
depth=$(<"$base/normalized/$rank/depth")
[[ $depth =~ ^[056]$ && $(stat -c %s "$archive") == "$payload" ]]
printf '%s  %s\n' "$digest" "$archive" | sha256sum --check --status
mkdir -- "$output"
printf '%s\n' "$stem" > "$output/stem.g6"
timeout --kill-after=2s 35s "$root/opt/venv/bin/python" "$root/ralph/lanes/B/src/high_r24_lift.py" \
    --normalized --min-stem "$depth" "$marked" "$output/stem.g6" "$output/lift.cnf" > "$output/build.log"
timeout --kill-after=2s 15s xz -dc "$archive" > "$output/lift.lrat"
printf '%s  %s\n%s  %s\n' "$cnf_hash" "$output/lift.cnf" "$lrat_hash" "$output/lift.lrat" | \
    sha256sum --check --status
timeout --kill-after=2s 35s "$root/opt/bin/cake_lpr" "$output/lift.cnf" "$output/lift.lrat" > "$output/cake.log"
timeout --kill-after=2s 35s "$root/opt/bin/lrat-check" "$output/lift.cnf" "$output/lift.lrat" > "$output/lrat.log"
rg -Fxq 's VERIFIED UNSAT' "$output/cake.log"
rg -Fxq 'c VERIFIED' "$output/lrat.log"
printf 'fresh dual rank=%s edge=%s marks=%s bytes=%s\n' "$rank" "$level" "$marked" "$payload"
