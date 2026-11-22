#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
ulimit -t 600
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
base=${1:?queue directory}
slot=${2:?0 or 1}
src=../../ralph/lanes/B/src
[[ $slot == 0 || $slot == 1 ]]
exec 9>"$base/guard.lock"
job="$base/stage.$slot"
mkdir -p "$job"

while IFS=$'\t' read -r key cross edge rank stem pilot variant; do
    variant=${variant:-compact}
    if [[ -f "$base/archive/$key.lrat.gz" ]]; then
        continue
    fi
    rm -f "$job/"{stem.g6,lift.cnf,lift.lrat,proof.gz,run.log,build.time,solve.time,cake.time,lrat.time}
    printf '%s\n' "$stem" >"$job/stem.g6"
    start=$(date +%s)
    mode=6
    if [[ $pilot != - ]]; then
        cmp "$pilot/stem.g6" "$job/stem.g6"
        rg -Fxq "DUAL $pilot cnf=$(stat -c %s "$pilot/lift.cnf") lrat=$(stat -c %s "$pilot/lift.lrat")" "$pilot/pilot.log"
        cp "$pilot/"{lift.cnf,lift.lrat,build.time,solve.time,cake.time,lrat.time} "$job/"
    else
        for mode in 6 5 0; do
            if timeout --kill-after=5s 155s bash "$src/paircut_r23_job.sh" \
                    "$job" produce "$cross" "$mode" "$variant" >"$job/run.log" 2>&1; then
                break
            fi
            cat "$job/run.log"
            if ! rg -Fxq 'OPEN solver rc=10' "$job/run.log" || [[ $mode == 0 ]]; then
                printf 'OPEN\t%s\t%s\t%s\n' "$key" "$mode" "$(date -Is)" | tee -a "$base/open.$slot.tsv"
                continue 2
            fi
            printf 'ESCALATE\t%s\t%s\n' "$key" "$mode"
            rm -f "$job/lift.lrat"
        done
    fi

    if ! (ulimit -f 2048; timeout 30s gzip -n -5 -c "$job/lift.lrat" >"$job/proof.gz"); then
        printf 'OPEN\t%s\tcompressed-proof-cap\n' "$key" | tee -a "$base/open.$slot.tsv"
        continue
    fi
    timeout 15s gzip -t "$job/proof.gz"
    bytes=$(stat -c %s "$job/proof.gz")
    temporary=$(sha256sum "$job/lift.cnf"); cnf=${temporary%% *}
    temporary=$(sha256sum "$job/proof.gz"); compressed=${temporary%% *}
    cpu=$(awk -F '[=+ ]' '/^cpu=/{total+=$2+$3} END{printf "%.2f",total}' \
          "$job/"{build,solve,cake,lrat}.time)

    flock 9
    used=$(<"$base/charged")
    charge=$((bytes + 1200))
    if ((used + charge > ${ARCHIVE_CAP:-117000000})); then
        printf 'GUARD\t%s\t%s\n' "$key" "$(date -Is)" | tee -a "$base/open.$slot.tsv"
        exit 0
    fi
    printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
        "$key" "$cross" "$edge" "$rank" "$mode" "$bytes" "$cnf" "$compressed" "$cpu" >>"$base/receipts.tsv"
    mv "$job/proof.gz" "$base/archive/$key.lrat.gz"
    printf '%s\n' "$((used + charge))" >"$base/charged"
    flock -u 9
    printf 'DUAL\t%s\t%s\t%s\t%s\t%s\n' "$key" "$mode" "$bytes" "$cpu" "$(( $(date +%s)-start ))"
done <"$base/slot$slot.tsv"
rm -f "$job/"{stem.g6,lift.cnf,lift.lrat,proof.gz,run.log,build.time,solve.time,cake.time,lrat.time}
rmdir "$job"
