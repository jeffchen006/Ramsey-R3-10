#!/bin/bash
set -euo pipefail
[[ $(basename "$PWD") == r24_deck ]]
src=../../../ralph/lanes/E
python=../../../opt/venv/bin/python
declare -A started
count=0
while (( count < 22 )); do
    for slot in {0..21}; do
        [[ ! -v 'started[$slot]' ]] || continue
        if [[ -e "C8.$slot.log" ]]; then
            started[$slot]=1
            count=$((count+1))
            continue
        fi
        if [[ $slot == 20 && ${1:-} == reserve-replay ]]; then
            if [[ ! -e replay-tail.log ]]; then
                bash "$src/r24_launch.sh" 20 replay-tail.log 2500 1100 bash "$src/r24_replay_tail.sh" || :
            fi
            [[ -e replay-tail.done ]] || continue
        fi
        if bash "$src/r24_launch.sh" "$slot" "C8.$slot.log" 14000 10500 \
                "$python" -B "$src/compact_deck24.py" run --plan C8.plan \
                --indexes "C8.prod/$slot.ids" --output "C8.prod/$slot" --archive-limit 125829120; then
            started[$slot]=1
            count=$((count+1))
        elif [[ -e "C8.$slot.log" ]]; then
            printf 'Unexpected existing log %s\n' "C8.$slot.log" >&2
            exit 1
        fi
    done
    if (( count < 22 )); then sleep 4; fi
done
