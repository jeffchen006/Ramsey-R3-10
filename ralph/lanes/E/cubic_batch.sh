#!/bin/bash
set -eu
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
worker=$root/ralph/lanes/E/run_cubic32.sh
mode=$1
first=$2
stride=$3
total=$(wc -l < windows.jsonl)
for ((index=first; index<total; index+=stride)); do
  prefix=$mode.$index
  if [[ ! -f "$prefix.lrat.log" ]] || ! grep -qx 's VERIFIED UNSAT' "$prefix.lrat.log"; then
    bash "$worker" "$index" window 30 75 "$prefix" > "$prefix.log" 2>&1 || :
  fi
  if grep -qx 's VERIFIED UNSAT' "$prefix.lrat.log" 2>/dev/null; then
    printf '%s\tCHECKED\n' "$index"
  else
    printf '%s\tINCOMPLETE\n' "$index"
  fi
done
