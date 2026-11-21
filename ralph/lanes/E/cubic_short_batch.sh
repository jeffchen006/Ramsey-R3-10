#!/bin/bash
set -eu
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
worker=$root/ralph/lanes/E/run_cubic32.sh
first=$1
stride=$2
total=$(wc -l < windows.jsonl)
for ((index=first; index<total; index+=stride)); do
  prefix=short.$index
  if ! rg -qx 's VERIFIED UNSAT' "$prefix.lrat.log" 2>/dev/null; then
    bash "$worker" "$index" short 25 65 "$prefix" > "$prefix.log" 2>&1 || :
  fi
  if rg -qx 's VERIFIED UNSAT' "$prefix.lrat.log" 2>/dev/null; then
    printf '%s\tCHECKED\n' "$index"
  else
    printf '%s\tINCOMPLETE\n' "$index"
  fi
done
