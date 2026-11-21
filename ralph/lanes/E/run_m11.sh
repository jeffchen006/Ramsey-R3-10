#!/bin/bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
lane=$root/ralph/lanes/E
tools=$root/opt/bin
manifest=$1
index=$2
lift=$3
mode=$4
prefix=$5
shift 5
options=()
case "$mode" in
  all) ;;
  single) options=(--one-window) ;;
  small) options=(--omit-small) ;;
  *) exit 2 ;;
esac

limited() {
    local budget=$1
    shift
    nice -n 5 timeout "$((budget + 25))" bash "$lane/limited.sh" "$budget" "$@"
}

fast_options=()
if [[ -n ${M11_FASTCUTS:-} ]]; then fast_options=(--fast "$M11_FASTCUTS"); fi
limited "${ENCODE_CPU:-12}" python3 -B "$lane/m11_sat.py" "${fast_options[@]}" encode "$manifest" "$index" "$lift" "$prefix.cnf" \
  "${options[@]}" "$@"
status=0
limited "${SOLVE_CPU:-15}" "$tools/cadical" -q --lrat "$prefix.cnf" "$prefix.lrat" > "$prefix.solve.log" 2>&1 || status=$?
printf 'solver_exit=%s\n' "$status"
case "$status" in
  10) printf 'SAT RELAXATION\n' ;;
  20)
    limited "${CHECK_CPU:-12}" "$tools/cake_lpr" "$prefix.cnf" "$prefix.lrat" > "$prefix.lrat.log" 2>&1
    rg -qx 's VERIFIED UNSAT' "$prefix.lrat.log"
    printf 'CHECKED UNSAT\n' ;;
  *) exit "$status" ;;
esac
