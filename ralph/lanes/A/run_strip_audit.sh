#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
root=../../..
source7=../../G/round7
source8=../../G/round8
python="$root/opt/venv/bin/python"
code="$root/ralph/lanes/A/audit_strip_extensions.py"
mode="${1:?choose lower, continued or mixed}"
shift

if [[ "$mode" == mixed || "$mode" == mixed-prefix ]]; then
    reader="$source7"
    if [[ "$mode" == mixed-prefix ]]; then reader=mixed-prefix; fi
    exec "$python" -B "$code" replay "$source7/mixed-j4.keys" audit-mixed \
        --schedule "$source7/mixed-j4.pilot.keys" \
        --batch "$source7/proof-mixed-pilot" "$reader"/proof-mixed-pilot.{0,1}.log \
        --schedule "$source7/mixed-j4.pending.keys" \
        --batch "$source7/proof-mixed" "$reader"/proof-mixed.{0,1}.log "$@"
fi

options=()
if [[ "$mode" == continued ]]; then
    options=(--resume "$source8/c1.first/unclosed.keys"
             --continuation "$source8/proof-c1retry" "$source8"/proof-c1retry.{0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15}.log
             --allow-overlap pilot.resume.overlaps)
elif [[ "$mode" != lower ]]; then
    exit 2
fi
exec "$python" -B "$code" replay "$source7/lowdegree25.canon.keys" audit-lower \
    --schedule "$source7/lowdegree25.pilot.keys" \
    --batch "$source7/proof-low25-eager" "$source7"/proof-low25-eager.{0,1,2}.log \
    --schedule "$source7/lowdegree25.pending.keys" \
    --batch "$source7/proof-low25" "$source7"/proof-low25.{0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15}.log \
    "${options[@]}" "$@"
