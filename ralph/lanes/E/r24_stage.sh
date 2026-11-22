#!/bin/bash
set -euo pipefail
[[ $(basename "$PWD") == r24_deck ]]
src=../../../ralph/lanes/E
python=../../../opt/venv/bin/python
while :; do
    for slot in {14..20} {0..13} 21; do
        if bash "$src/r24_launch.sh" "$slot" stage15.log 360 240 bash -e -c '
"$1" -B "$2/audit_deck24.py" --compare --prefix stage
"$1" -B "$2/shape_deck24.py"
for core in 2 8; do
    if [[ $core == 2 ]]; then key="G?r@\`_"; else key="G?qa\`_"; fi
    for profile in 0 1; do
        "$1" -B "$2/profile15_deck24.py" "$key" "$profile" "profile15.$core.$profile"
    done
done
' bash "$python" "$src"; then
            exit 0
        fi
        [[ ! -e stage15.log ]] || exit 1
    done
    sleep 0.5
done
