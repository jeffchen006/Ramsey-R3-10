#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
ulimit -t 600
ulimit -f 32768
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
base=${1:?queue directory}
slot=${2:?0 or 1}
[[ $slot == 0 || $slot == 1 ]]
src=../../ralph/lanes/B/src
job="$base/replay.$slot"
mkdir "$job"
plan="$job/plan.tsv"
awk -F '\t' 'BEGIN{OFS="\t"} NR==FNR{mode[$1]=$5; cnf[$1]=$7; proof[$1]=$8; next}
    !($1 in mode){exit 1} {print $1,$2,$5,$7,mode[$1],cnf[$1],proof[$1]}' \
    "$base/receipts.tsv" "$base/slot$slot.tsv" >"$plan"
while IFS=$'\t' read -r key cross stem degrees mode cnf proof; do
    printf '%s\n' "$stem" >"$job/stem.g6"
    printf '%s  %s\n' "$proof" "$base/archive/$key.lrat.gz" | sha256sum -c - >/dev/null
    timeout --kill-after=2s 15s gzip -dc "$base/archive/$key.lrat.gz" >"$job/lift.lrat"
    timeout --kill-after=2s 35s ../../opt/venv/bin/python "$src/paircut_r23.py" \
        --cross "$cross" --min-stem-indep "$mode" --one-low "$degrees" "$job/stem.g6" "$job/lift.cnf" >/dev/null
    printf '%s  %s\n' "$cnf" "$job/lift.cnf" | sha256sum -c - >/dev/null
    timeout --kill-after=2s 75s bash "$src/paircut_r23_job.sh" "$job" replay >"$job/run.log" 2>&1
    rg -q '^DUAL ' "$job/run.log"
    printf 'DUAL\t%s\n' "$key"
done <"$plan"
rm -f "$job/"{plan.tsv,stem.g6,lift.cnf,lift.lrat,cake.time,lrat.time,cake.log,lrat.log,run.log}
rmdir "$job"
