#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
lane="$root/ralph/lanes/A"
prior="$root/scratch/A/r16"
other="$root/scratch/C/r16"
g16="$root/gluing/val/r3_6_16.g6"
g17="$root/gluing/val/r3_6_17.g6"
mode=${1:-all}
[[ $mode = all || $mode = small ]]
work="$root/scratch/A/${2:-r17-replay}"
[[ ${work##*/} =~ ^r17(-[[:alnum:]_]+)?$ && $work = "$root/scratch/A/"* ]]
mkdir -p "$work"
cd "$work"
export TMPDIR="$PWD" LC_ALL=C
ulimit -v 524288 -c 0 -t 150
run() { /usr/bin/time -o "$1.time" -f '%U %S %e %M' nice -n 5 timeout 120 "${@:2}"; }
audit() { run "$1" python3 -B "$lane/audit_direction_profiles.py" "$@"; }

run build_oracle g++ -std=c++20 -O3 -Wall -Wextra -Werror "$lane/profile_oracle.cpp" -o oracle
run small_oracle ./oracle small "$prior/small6.g6" "$prior/small7.g6" "$prior/small6.frames" "$prior/small7.frames" > small.oracle.tsv
audit small "$prior/small6.g6" "$prior/small7.g6" "$prior/small6.frames" "$prior/small7.frames" small.oracle.tsv \
    "$other/controls.tsv" "$other/control6.g6" "$other/control7.g6" > small.log
cat small.log
if [[ $mode = all ]]; then
    run build_frames g++ -std=c++20 -O3 -Wall -Wextra -Werror "$lane/one_neutral_frames.cpp" -o frames
    for order in 16 17; do
        if [[ $order == 16 ]]; then catalogue=$g16; count=2576; else catalogue=$g17; count=7; fi
        run "frames$order" ./frames frames "$catalogue" "$order" "$count" 4 9 5 5 0 "$count" |
            run "weights$order" python3 -B "$lane/audit_direction_profiles.py" weights "$catalogue" "$prior/count$order.tsv" > "weights$order.tsv"
    done
    audit mass "$g16" "$g17" weights16.tsv weights17.tsv "$prior/strata.tsv" > mass.log
    cat mass.log
    run pilot_oracle ./oracle pilot "$g16" "$g17" "$other/bound.cases.tsv" > pilot.oracle.tsv
    audit pilot "$g16" "$g17" weights16.tsv weights17.tsv "$other/bound.cases.tsv" pilot.oracle.tsv "$other/pilot.stats" > pilot.log
    cat pilot.log
fi
audit cross "$prior/small6.g6" "$prior/small7.g6" "$prior/small6.frames" "$prior/small7.frames" small.oracle.tsv \
    "$root/scratch/C/r17/small.groups.tsv" > cross.log
cat cross.log
