#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
ulimit -t 13000
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1 NORMALIZED=1 FILE_BLOCKS=12288
directory=work/e108_r24_high
source=../../ralph/lanes/B/src/high_r24_job.sh
slot=${1:?slot}
[[ $slot == 0 || $slot == 1 ]]
destination="$directory/normalized"
charge=$(find "$destination" -mindepth 1 -maxdepth 1 -type d -printf '%f\n' | \
    awk -v s="$slot" '$1 % 2 == s' | while read -r rank; do du -sb "$destination/$rank" | cut -f1; done | \
    awk '{sum+=$1} END {print sum+0}')
limit=72000000
printf 'START slot=%s charge=%s limit=%s %s\n' "$slot" "$charge" "$limit" "$(date -Is)"
while IFS=$'\t' read -r rank level marked stem; do
    job="$destination/$rank"
    if [[ -s $job/archive.sha256 ]] && rg -q '^DUAL depth=' "$job/job.stdout"; then
        sha256sum --check --status "$job/archive.sha256"
        printf '%s\t%s\tADOPT\t%s\n' "$rank" "$level" "$(stat -c %s "$job/lift.lrat.xz")"
        continue
    fi
    if (( charge + 3000000 > limit )); then
        printf 'GUARD slot=%s charge=%s first_unstarted=%s %s\n' "$slot" "$charge" "$rank" "$(date -Is)"
        exit 2
    fi
    mkdir -- "$job"
    printf '%s\n' "$stem" > "$job/stem.g6"
    printf '%s\n' "$marked" > "$job/marked"
    rc=0
    timeout --kill-after=3s 240s bash "$source" "$job" "$marked" > "$job/job.stdout" 2> "$job/job.stderr" || rc=$?
    charged=$(du -sb "$job" | cut -f1)
    charge=$((charge+charged))
    if [[ $rc == 0 ]] && rg -q '^DUAL depth=' "$job/job.stdout"; then
        printf '%s\t%s\tDUAL\t%s\t%s\n' "$rank" "$level" "$(stat -c %s "$job/lift.lrat.xz")" "$charge"
    else
        printf '%s\t%s\tOPEN:%s\t%s\t%s\n' "$rank" "$level" "$rc" "$charged" "$charge"
    fi
done < "$directory/queue.$slot.tsv"
printf 'FINISH slot=%s charge=%s %s\n' "$slot" "$charge" "$(date -Is)"
