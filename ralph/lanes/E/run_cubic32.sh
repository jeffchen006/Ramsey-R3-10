#!/bin/bash
set -eu
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
tools=$root/opt/bin
limit=$root/ralph/lanes/E/limited.sh
index=$1
mode=$2
cpu=$3
wall=$4
prefix=${5:-$mode.$index}
case "$mode" in
  window) options=() ;;
  relax) options=(--no-alpha) ;;
  short) options=(--no-pair --cut-size "${CUT_SIZE:-8}") ;;
  *) exit 2 ;;
esac
nice -n 5 timeout 25 bash "$limit" 15 python3 -B "$root/ralph/lanes/E/cubic32.py" \
  encode windows.jsonl "$index" "$prefix.cnf" "${options[@]}"
rc=0
nice -n 5 timeout "$wall" bash "$limit" "$cpu" "$tools/cadical" -q --lrat "$prefix.cnf" "$prefix.lrat" \
  > "$prefix.solve.log" 2>&1 || rc=$?
printf 'solver_exit=%s\n' "$rc"
case "$rc" in
  10) printf 'SAT window (not a full graph)\n' ;;
  20)
    printf 'UNCHECKED_UNSAT\n'
    nice -n 5 timeout "$wall" bash "$limit" "$cpu" "$tools/cake_lpr" "$prefix.cnf" "$prefix.lrat" \
      > "$prefix.lrat.log" 2>&1 || exit 1
    grep -qx 's VERIFIED UNSAT' "$prefix.lrat.log" || exit 1
    printf 'CHECKED_UNSAT\n' ;;
esac
