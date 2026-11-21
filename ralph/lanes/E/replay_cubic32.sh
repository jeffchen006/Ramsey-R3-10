#!/bin/bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
lane=$root/ralph/lanes/E
tools=$root/opt/bin
mode=$1
offset=${2:-0}
stride=${3:-1}
[[ "$offset" =~ ^[0-9]+$ && "$stride" =~ ^[1-9][0-9]*$ && "$offset" -lt "$stride" ]]
limited() {
  local cpu=$1
  shift
  nice -n 5 timeout "$((cpu + 25))" bash "$lane/limited.sh" "$cpu" "$@"
}
out="$PWD/replay.$offset.$stride"
mkdir -p "$out"
case "$mode" in
  full) census=() ; options=() ; expected=1058 ;;
  short) census=(--saturated "$lane/saturated_e12.g6") ; options=(--no-pair --cut-size 8) ; expected=6904 ;;
  *) exit 2 ;;
esac
limited 25 python3 -B "$lane/cubic32.py" census "$out/windows.jsonl" "${census[@]}"
cmp windows.jsonl "$out/windows.jsonl"
test "$(wc -l < windows.jsonl)" -eq "$expected"
for ((index=offset; index<expected; index+=stride)); do
  prefix=$mode.$index
  limited 15 python3 -B "$lane/cubic32.py" encode "$out/windows.jsonl" "$index" "$out/rebuild.cnf" "${options[@]}"
  cmp "$prefix.cnf" "$out/rebuild.cnf"
  limited 30 "$tools/cake_lpr" "$out/rebuild.cnf" "$prefix.lrat" > "$out/lrat.log" 2>&1
  rg -qx 's VERIFIED UNSAT' "$out/lrat.log"
  printf '%s\tREPLAYED\n' "$index"
done
