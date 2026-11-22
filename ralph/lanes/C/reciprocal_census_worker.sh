#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
lane="$root/ralph/lanes/C"
scout="$root/scratch/ideas/r009_R"
lhs="$root/gluing/val/r3_7_22.g6"
py="$root/opt/venv/bin/python"
ulimit -v 16777216
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 TMPDIR="$PWD"
mode=$1
if [[ $mode = controls ]]; then
    old="$root/scratch/C/r10"
    for method in direct indexed; do
        timeout 60 ./reciprocal_stream "$method" "$old/cal-small-10.g6" "$old/cal-small-11.g6" 10 11 6 6 2 3 "$method.tsv"
        cmp "$method.tsv" "$old/cal-small-$method.tsv"
    done
    timeout 60 ./reciprocal_stream planted "$old/cal-10.g6" "$old/cal-11.g6" 10 11 6 6 2 3 planted.tsv
    cmp planted.tsv "$old/cal-planted-indexed.tsv"
    cmp indexed.tsv direct.tsv
    printf '395 positives and 4,882 no-index keys reproduce byte for byte\n'
    exit
fi
batch=$2
if [[ $mode = stream ]]; then
    timeout 1800 prlimit --cpu=1300:1310 /usr/bin/time -v -o "$batch.stream.time" \
        ./reciprocal_stream batch "$lhs" "$batch.batch" 22 21 9 5 3 9 "$batch.done.tsv" >"$batch.stream.log"
    while read -r lo hi source dest; do
        printf '%s %s ' "$lo" "$hi"
        wc -l < "$dest" | tr '\n' ' '
        stat -c '%s' "$dest" | tr '\n' ' '
        sha256sum "$source" "$dest" | paste -sd ' '
    done < "$batch.batch" > "$batch.stream.sha256.tsv"
elif [[ $mode = audit ]]; then
    completed=${3:-$batch.done.tsv}
    while read -r lo hi source dest; do
        test ! -e "$(dirname "$source")/audit.sha256" || continue
        rg -Fqx "$(printf '%s\t%s\t%s' "$lo" "$hi" "$dest")" <(cut -f1-3 "$completed")
        (
            cd "$(dirname "$source")"
            cpu_limit=385
            wall_limit=480
            if [[ $(stat -c '%s' maps.tsv) -ge 50000000 ]]; then
                cpu_limit=720
                wall_limit=920
            fi
            /usr/bin/time -f '%U %S %e %M' -o scout.time timeout 220 prlimit --cpu=190:195 \
                "$scout/reciprocal" 40 hosts.g6 scout-right.tsv 5 21 12 > scout.log
            /usr/bin/time -f '%U %S %e %M' -o index.time timeout 120 prlimit --cpu=90:95 \
                "$scout/mixed" "$lhs" "$scout/wide22.tsv" hosts.g6 scout-right.tsv scout-left-live.tsv scout-right-live.tsv > index.log
            /usr/bin/time -f '%U %S %e %M' -o audit.time timeout "$wall_limit" prlimit --cpu="$cpu_limit:$((cpu_limit+5))" \
                "$py" -B "$lane/reciprocal_census.py" audit "$lo" "$hi" > audit.log
            sha256sum scout-{right,left-live,right-live}.tsv audit.log unresolved.tsv > audit.sha256
            rm scout-right.tsv
        )
    done < "$batch.batch"
else
    exit 2
fi
