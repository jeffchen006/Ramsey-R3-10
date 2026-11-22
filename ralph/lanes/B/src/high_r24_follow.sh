#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
ulimit -t 500
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1 NORMALIZED=1 FILE_BLOCKS=12288
directory=work/e108_r24_high
slot=${1:?slot}
predecessor=${2:?predecessor}
[[ $slot == 0 || $slot == 1 ]]
[[ $predecessor =~ ^[0-9]+$ ]]
printf 'WAIT slot=%s predecessor=%s %s\n' "$slot" "$predecessor" "$(date -Is)"
while state=$(ps -o stat= -p "$predecessor") && [[ $state != Z* ]]; do
    sleep 15
done
rg -q "^FINISH slot=$slot " "$directory/queue.$slot.stdout"
printf 'START slot=%s predecessor released %s\n' "$slot" "$(date -Is)"
source=../../ralph/lanes/B/src/high_r24_job.sh
charged=0
attempted=0
while IFS=$'\t' read -r rank level marked stem; do
    if (( charged + 1000000 > 8000000 )); then
        printf 'GUARD slot=%s first_unstarted=%s charge=%s\n' "$slot" "$rank" "$charged"
        exit 2
    fi
    job="$directory/normalized/$rank"
    mkdir -- "$job"
    printf '%s\n' "$stem" > "$job/stem.g6"
    printf '%s\n' "$marked" > "$job/marked"
    rc=0
    solver_wall=65s
    (( attempted >= 2 )) || solver_wall=12s
    env SOLVE_WALL="$solver_wall" timeout --kill-after=3s 240s bash "$source" "$job" "$marked" > "$job/job.stdout" 2> "$job/job.stderr" || rc=$?
    charge=$(du -sb "$job" | cut -f1)
    charged=$((charged+charge))
    attempted=$((attempted+1))
    if [[ $rc == 0 ]] && rg -q '^DUAL depth=' "$job/job.stdout"; then
        printf '%s\t%s\tDUAL\t%s\t%s\n' "$rank" "$level" "$(stat -c %s "$job/lift.lrat.xz")" "$charged"
    else
        printf '%s\t%s\tOPEN:%s\t%s\t%s\n' "$rank" "$level" "$rc" "$charge" "$charged"
        if (( attempted <= 2 )); then exit 3; fi
    fi
    if (( attempted == 2 && charged > 700000 )); then
        printf 'PILOT_GUARD slot=%s proof payload too high charge=%s\n' "$slot" "$charged"
        exit 4
    fi
done < "$directory/follow.$slot.tsv"
printf 'FINISH slot=%s charge=%s %s\n' "$slot" "$charged" "$(date -Is)"
