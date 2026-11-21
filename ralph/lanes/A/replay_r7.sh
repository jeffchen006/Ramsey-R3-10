#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
lane="$root/ralph/lanes/A"
if (( $# < 1 || $# > 2 )); then
    echo "usage: replay_r7.sh NEW_SCRATCH_OUTPUT_DIR [PROOF_INPUT_DIR]" >&2
    exit 2
fi
proof_dir=$(realpath -e -- "${2:-$root/scratch/A/r7-proof-v1}")
output=$(realpath -m -- "$1")
case "$output/" in
    "$proof_dir/"*) echo "output must be separate from proof inputs" >&2; exit 2 ;;
esac
case "$output" in
    "$root/scratch/"*) ;;
    *) echo "output must be inside workspace scratch" >&2; exit 2 ;;
esac
export PYTHONDONTWRITEBYTECODE=1
ulimit -v 16777216
mkdir -- "$output"
cd -- "$output"
export TMPDIR="$output"
( cd "$root"; sha256sum --strict -c "$lane/R7_CODE.sha256" ) | tee code-manifest.log
( cd "$proof_dir"; sha256sum --strict -c "$lane/R7_INPUTS.sha256" ) | tee input-manifest.log
nice -n 5 timeout 60 g++ -std=c++20 -O3 -mpopcnt -Wall -Wextra "$lane/r7_audit.cpp" -o r7_replay
python3 "$lane/r7_seeds.py" "$proof_dir" | tee seeds.log
for index in 0 1 2 3; do
    /usr/bin/time -f 'TIMING wall=%e user=%U sys=%S rss=%M' \
        nice -n 5 timeout 180 prlimit --cpu=120:125 ./r7_replay --cover \
        "$proof_dir/R7_full.$index.txt" "$proof_dir/R7_trace.$index.bin" 2>&1 | tee "replay-X$index.log"
    grep -q '^s VERIFIED packing replay ' "replay-X$index.log"
    grep -q '^s VERIFIED side cover ' "replay-X$index.log"
done
echo 'PASS all four R(7) covers and traces'
