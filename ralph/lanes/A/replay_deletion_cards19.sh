#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
lane="$root/ralph/lanes/A"
catalogue="$root/gluing/val"
name=${1:-r19-replay}
[[ $name =~ ^r19-[[:alnum:]_]+$ ]]
mkdir "$root/scratch/A/$name"
cd "$root/scratch/A/$name"
export TMPDIR="$PWD" LC_ALL=C
ulimit -v 524288 -f 262144 -c 0
run() {
    local tag=$1 cpu=$2
    shift 2
    nice -n 5 timeout 180 prlimit --cpu="$cpu:$((cpu+5))" /usr/bin/time -o "$tag.time" -f '%U %S %e %M %x' "$@"
}
python="$root/opt/venv/bin/python"
cards="$lane/deletion_cards19.py"
run small 15 "$python" -B "$cards" small "$catalogue" > small.log
run sample 15 "$python" -B "$cards" sample "$catalogue" > sample.log
run target 110 "$python" -B "$cards" target "$catalogue" cards-v1.json > target.log
run build_frames 45 g++ -std=c++20 -O3 -Wall -Wextra -Werror "$lane/one_neutral_frames.cpp" -o frames
run build_oracle 45 g++ -std=c++20 -O3 -Wall -Wextra -Werror "$lane/profile_oracle.cpp" -o oracle
run oracle_control 10 ./oracle small "$root/scratch/A/r16"/small{6,7}.g6 \
    "$root/scratch/A/r16"/small{6,7}.frames > small-oracle.tsv
cmp small-oracle.tsv "$root/scratch/A/r17-stream/small.oracle.tsv"
run bin 45 "$python" -B "$lane/bind_deletion_bin19.py" select "$root" ./frames ./oracle > bin.log
cat small.log target.log bin.log
