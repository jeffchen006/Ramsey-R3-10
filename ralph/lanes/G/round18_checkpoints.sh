#!/bin/bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
work="$root/scratch/G/round18"
worker="$root/ralph/lanes/G/round18_middle.sh"

run() {
    local tag=$1
    shift
    /usr/bin/time -f '%U %S %e %M %x' -o "$work/$tag.time" \
        bash "$worker" "$@" > "$work/$tag.log" 2>&1
}

stop() {
    run reconcile-stop reconcile || true
    exit 1
}

sha256sum -c --quiet "$work/production-gate.sha256"
for ((lo=0;lo<1947;lo+=160)); do
    hi=$(( lo + 160 ))
    if (( hi > 1947 )); then hi=1947; fi
    printf -v low '%04d' "$lo"
    printf -v high '%04d' "$hi"
    run "make-$low-$high" make production "$lo" "$hi" || stop
    run "replay-$low-$high" replay production "$lo" "$hi" || stop
    run "estimate-$high" estimate || stop
    cat "$work/estimate-$high.log"
done
run complete complete
cat "$work/complete.log"
