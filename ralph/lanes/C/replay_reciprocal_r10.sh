#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
lane="$root/ralph/lanes/C"
scout="$root/scratch/ideas/r009_R"
host="$root/gluing/val/r3_7_22.g6"
py="$root/opt/venv/bin/python"
work="$root/scratch/C/r10-replay"
mkdir -p "$work"
cd "$work"
ulimit -v 16777216
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 TMPDIR="$work"
run() { nice -n 5 timeout "$@"; }
run 45 g++ -std=c++20 -O3 -mpopcnt -Wall -Wextra "$lane/reciprocal_stream.cpp" -o reciprocal_stream
run 35 "$py" -B "$lane/reciprocal_audit.py" controls
for order in 10 11; do head -6 "cal-$order.g6" > "cal-small-$order.g6"; done
for mode in direct indexed; do
  run 60 ./reciprocal_stream "$mode" cal-small-10.g6 cal-small-11.g6 10 11 6 6 2 3 "cal-small-$mode.tsv"
done
run 45 ./reciprocal_stream planted cal-10.g6 cal-11.g6 10 11 6 6 2 3 cal-planted-indexed.tsv
run 60 "$py" -B "$lane/reciprocal_audit.py" control-check
run 35 "$py" -B "$lane/reciprocal_audit.py" sample
run 100 "$py" -B "$lane/reciprocal_audit.py" source-check
run 10 "$root/opt/bin/shortg" -q "$host" source22-shortg.g6
test "$(wc -l < source22-shortg.g6)" -eq 191
cat pilot-21.g6 "$scout/held21.g6" "$scout/dispersed21.g6" > sample-combined.g6
test "$(wc -l < sample-combined.g6)" -eq 9490
run 60 "$root/opt/bin/shortg" -q sample-combined.g6 sample-combined-shortg.g6
test "$(wc -l < sample-combined-shortg.g6)" -eq 9490
run 60 ./reciprocal_stream indexed "$host" "$host" 22 22 9 5 3 10 equal22.tsv
test ! -s equal22.tsv
run 120 ./reciprocal_stream cards "$host" "$host" 22 22 9 5 3 9 fixed22.tsv
cmp fixed22.tsv "$scout/wide22.tsv"
run 480 prlimit --cpu=300:305 ./reciprocal_stream indexed "$host" pilot-21.g6 22 21 9 5 3 9 pilot.tsv
run 60 "$scout/reciprocal" 40 pilot-21.g6 scout-right.tsv 5 21 12
run 60 "$scout/mixed" "$host" fixed22.tsv pilot-21.g6 scout-right.tsv scout-left-live.tsv scout-right-live.tsv
run 200 prlimit --cpu=165:170 "$py" -B "$lane/reciprocal_audit.py" audit
for mode in control pilot; do
  run 90 "$py" -B "$lane/reciprocal_proof_pilot.py" "$mode"
  run 180 prlimit --cpu=115:120 "$py" -B "$lane/reciprocal_proof_pilot.py" "$mode" --thin
done
run 35 "$py" -B "$lane/reciprocal_proof_pilot.py" compare
for artifact in pilot-ids.tsv pilot-21.g6 fixed22.tsv pilot.tsv scout-left-live.tsv scout-right-live.tsv; do
  cmp "$artifact" "$root/scratch/C/r10/$artifact"
done
(cd "$root" && sha256sum -c "$lane/ROUND9_REPLAY.sha256" --quiet)
