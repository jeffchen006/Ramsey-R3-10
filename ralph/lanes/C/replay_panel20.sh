#!/usr/bin/env bash
set -euo pipefail
lane=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo=$(cd -- "$lane/../../.." && pwd)
work=$(realpath -m -- "${1:-$repo/scratch/C/r20-replay}")
mode=${2:-all}
[[ $work == "$repo/scratch/C/"* ]]
mkdir -p -- "$work"
cd -- "$work"
unset PYTHONOPTIMIZE
export TMPDIR=$PWD LC_ALL=C
ulimit -v 524288 -f 131072 -c 0
timed() {
    local name=$1 wall=$2 cpu=$3
    shift 3
    nice -n 5 timeout "$wall" prlimit --cpu="$cpu:$((cpu+2))" /usr/bin/time -o "$name.time" -f '%U %S %e %M' "$@"
}
cat16="$repo/gluing/val/r3_6_16.g6"
cat17="$repo/gluing/val/r3_6_17.g6"
run_target() {
    local name=$1
    shift
    timed "$name" 70 45 python3 -B "$lane/panel20_factored.py" "$@" --cat16 "$cat16" --cat17 "$cat17" \
        --left "$repo/scratch/C/r19/frames16.tsv" --right "$repo/scratch/C/r19/frames17.tsv" \
        --old-rows "$repo/scratch/C/r19/literal.rows.tsv" --frozen "$repo/scratch/A/r19/heldout.cases.tsv" \
        --out "$name.tsv" > "$name.log"
    cat "$name.log"
}
case "$mode" in
    all|check)
        timed control 60 30 python3 -B "$lane/panel20_factored.py" --control > control.log
        cat control.log
        run_target sample --sample
        if [[ $mode == all ]]; then
            run_target right_flags
        fi
        ;;
    target)
        run_target right_flags
        ;;
    *) exit 2 ;;
esac
