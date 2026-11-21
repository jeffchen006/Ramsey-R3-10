#!/usr/bin/env bash
set -euo pipefail
if (( $# != 2 )); then
    echo "usage: $0 previous-stage current-stage (cwd = lane scratch)" >&2
    exit 2
fi
lane=$(cd -- "$(dirname -- "$0")" && pwd)
root=$(cd -- "$lane/../../.." && pwd)
ulimit -v 16777216
ulimit -t 160
previous=$1
stage=$2
prev120="merged120.stage$previous.g6"
prev121="merged121.stage$previous.g6"
base120="merged120.stage$((previous-1)).g6"
base121="merged121.stage$((previous-1)).g6"
front120="front120.s$stage.g6"
front121="front121.s$stage.g6"
comm -13 "$base120" "$prev120" > "$front120"
comm -13 "$base121" "$prev121" > "$front121"
wc -l "$front120" "$front121"
pids=()
for job in "widen120 $front120 3" "lateral120 $front120 2" "lateral121 $front121 2" "down120 $front121 1"; do
    read -r mode input addition <<< "$job"
    bash "$lane/run_witness_edit.sh" "$input" "$addition" "$mode.s$stage.g6" &
    pids+=("$!")
done
(
    /usr/bin/time -f 'thin user=%U system=%S wall=%e' nice -n 5 timeout 30s ../root/thin 8 < "$front121" |
    nice -n 5 timeout 30s "$root/opt/bin/shortg" -q > "thin120.s$stage.g6"
) 2> "thin120.s$stage.log" &
pids+=("$!")
(
    /usr/bin/time -f 'add user=%U system=%S wall=%e' nice -n 5 timeout 30s ../round3/expand_residue_edges 8 < "$front120" |
    nice -n 5 timeout 30s "$root/opt/bin/shortg" -q > "add121.s$stage.g6"
) 2> "add121.s$stage.log" &
pids+=("$!")
status=0
for pid in "${pids[@]}"; do wait "$pid" || status=1; done
(( ! status ))
for level in 120 121; do
    cat "$prev120" "$prev121" "lateral120.s$stage.g6" "down120.s$stage.g6" "thin120.s$stage.g6" \
        "lateral121.s$stage.g6" "widen120.s$stage.g6" "add121.s$stage.g6" |
        nice -n 5 timeout 30s "$root/opt/bin/pickg" -q -e"$level" | sort -u > "merged$level.stage$stage.g6"
done
wc -l "merged120.stage$stage.g6" "merged121.stage$stage.g6"
