#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
source "$root/opt/env.sh"
cd "$root/scratch/A/rc7"
ulimit -v 16777216
( cd "$root"; sha256sum -c ralph/lanes/A/R7_INPUTS.sha256 )
nice -n 5 g++ -std=c++20 -O3 -mpopcnt -Wall -Wextra "$root/ralph/lanes/A/r7_audit.cpp" -o r7_replay
python "$root/tools/check_graph.py" --n 27 --k 8 r38_27_e85.g6
test "$(labelg -q < r38_27_e85.g6 | sort -u | wc -l)" = 4
python - "$root/scratch/C" <<'PY'
from pathlib import Path
import sys

proof_dir = Path(sys.argv[1])
graphs = Path('r38_27_e85.g6').read_text().splitlines()
if len(graphs) != 4:
    raise SystemExit('expected four X seeds')
for index, line in enumerate(graphs):
    bits = ''.join(f'{ord(char) - 63:06b}' for char in line[1:])
    adj = [0] * 27
    endpoints = ((left, right) for right in range(27) for left in range(right))
    edges = 0
    for bit, (left, right) in zip(bits, endpoints):
        if bit == '1':
            adj[left] |= 1 << right
            adj[right] |= 1 << left
            edges += 1
    with (proof_dir / f'R7_full.{index}.txt').open() as source:
        header = source.readline().split()
        masks = list(map(int, source.readline().split()))
    if edges != 85 or header != ['9', '7', '27'] or masks != adj:
        raise SystemExit(f'mismatched R7 seed {index}')
print('PASS all four proof inputs match the distinct e85 graph6 seeds')
PY
for index in 0 1 2 3; do
    /usr/bin/time -f 'TIMING wall=%e user=%U sys=%S rss=%M' \
        nice -n 5 timeout 180 prlimit --cpu=120:125 ./r7_replay --cover \
        "$root/scratch/C/R7_full.$index.txt" "$root/scratch/C/R7_trace.$index.bin" 2>&1 | tee "replay-X$index.log"
    rg -q '^s VERIFIED packing replay ' "replay-X$index.log"
    rg -q '^s VERIFIED side cover ' "replay-X$index.log"
done
