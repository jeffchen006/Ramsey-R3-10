#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd); lane="$root/ralph/lanes/D"; n=$1; store="$root/scratch/D/c6r23/wing"; parent=$(awk -v n="$n" '$1==n{print $2}' "$store/pids.tsv"); expected="$root/opt/venv/bin/python -B $lane/wingproof23.py shard $n"
while [[ $(ps -o args= -p "$parent") == "$expected" ]];do
    if [[ $(readlink /proc/$parent/cwd) == "$store/"* && -n $(cat /proc/$parent/task/$parent/children) ]];then
        kill -STOP "$parent";trap 'kill -CONT "$parent" || true' EXIT
        while ps -o state= --ppid "$parent" | rg -q '[^ Z]';do sleep .3;done
        "$root/opt/venv/bin/python" -B "$lane/static23.py" "$n";exit
    fi
    sleep .25
done
