#!/usr/bin/env bash
set -euo pipefail
lane_dir=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$lane_dir/../../.." && pwd)
calibration=$(realpath "$1"); shift
if ! python3 -I "$root/.hmz/flows/r310_ralph/gate.py" "$root" check "$calibration" 39 10 \
    | python3 -c 'import json, sys; sys.exit(not any(row["ok"] for row in json.load(sys.stdin)["graphs"]))'; then
    echo 'Require a gate-checked random-start 39 calibration file' >&2
    exit 2
fi
for tag in "$@"; do
    opts=()
    case "$tag" in
        p2f*) sym=2; opts=(-sym 2 -symf "${tag#p2f}");;
        p3f*) sym=3; opts=(-sym 3 -symf "${tag#p3f}");;
        b8m5) sym=5; opts=(-sym 5);;
        b5m8) sym=8; opts=(-sym 8);;
        b4m10) sym=10; opts=(-sym 10);;
        p4free) sym=4; opts=(-sym 4);;
        p4mixed) sym=4; opts=(-symcycles 4,4,4,4,4,4,4,4,4,2,1,1);;
        *) printf 'Unrecognized tag: %s\n' "$tag" >&2; exit 2;;
    esac
    hot=$((sym+1)); cold=$(awk -v symmetry="$sym" 'BEGIN { print symmetry / 10 }')
    bash "$lane_dir/launch.sh" "pilot_$tag" 110 95 bash ../../../ralph/lanes/F/run40.sh "pilot_$tag" \
        -time 90 -symfast -symbatch -T0 "$hot" -T1 "$cold" -sweep 200000 -focus .55 \
        -seed 20261121 "${opts[@]}"
done
