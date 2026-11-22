#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
source_dir="$root/ralph/lanes/A"
g16="$root/gluing/val/r3_6_16.g6"
g17="$root/gluing/val/r3_6_17.g6"
work="$root/scratch/A/r16-replay"
mkdir -p "$work"
cd "$work"
export TMPDIR="$PWD" LC_ALL=C
ulimit -v 524288 -c 0 -t 120
run() { /usr/bin/time -o "$1.time" -f '%U %S %e %M' nice -n 5 timeout 60 "${@:2}"; }

sha256sum -c <<EOF
25e35e1bb46b3131ff00b430b56e4679fcde7988211aefd9036c1e4c0cd7d2bf  $g16
3286c5366ddc70f349c3f7e798d7acbc79dc026c7abe0c8f406cad41ca990361  $g17
EOF
run build g++ -std=c++20 -O3 -Wall -Wextra -Werror "$source_dir/one_neutral_frames.cpp" -o frames
run controls python3 -B "$source_dir/one_neutral_control.py" "$g16" ./frames > controls.log
cat controls.log
run price16 ./frames price "$g16" 16 2576 4 9 5 5 0 2576 > price16.tsv
run price17 ./frames price "$g17" 17 7 4 9 5 5 0 7 > price17.tsv
run sample16 ./frames counts "$g16" 16 2576 4 9 5 5 945 1009 > sample16.tsv
run count16 ./frames counts "$g16" 16 2576 4 9 5 5 0 2576 > count16.tsv
run count17 ./frames counts "$g17" 17 7 4 9 5 5 0 7 > count17.tsv
run shortg16 "$root/opt/bin/shortg" -q "$g16" unique16.g6
run shortg17 "$root/opt/bin/shortg" -q "$g17" unique17.g6
test "$(wc -l < unique16.g6)" -eq 2576
test "$(wc -l < unique17.g6)" -eq 7
run pilot python3 -B "$source_dir/one_neutral_pilot.py" ./frames "$g16" "$g17" > pilot.log
test "$(cat pilot.log)" = 'frame16=2817701 frame17=59521 headers=15051526031 strata=34 pilot=544 unique_frame16=427 unique_frame17=423 seed=20261122'
cat pilot.log

if [[ -f "$source_dir/ROUND16_FREEZE.sha256" ]]; then
    sha256sum -c <(awk '/ scratch\/A\/r16\// && $2 !~ /public[.]sha256$/ {sub("scratch/A/r16/", "", $2); print}' "$source_dir/ROUND16_FREEZE.sha256")
fi
