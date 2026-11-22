#!/bin/bash
set -eu
lane=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$lane/../../.." && pwd)
case "$PWD" in "$root"/scratch/F/*) ;; *) echo 'run in a new empty directory below scratch/F' >&2; exit 2;; esac
test -z "$(ls -A .)" || { echo 'expected an empty directory' >&2; exit 2; }
ulimit -v 4194304
run(){ nice -n 5 timeout 50 prlimit --cpu=40 -- "$@"; }
py(){ run "$root/opt/venv/bin/python" -B "$lane/$1.py" "${@:2}"; }
run g++ -std=c++17 -O3 -mbmi2 -mpopcnt "$lane/marked_price.cpp" -o price
run g++ -std=c++20 -O3 -march=native "$lane/column_join.cpp" -o join
run ./price control 1 small; run ./price smallpole 1 smallpole
py marked_windows control small wsmall 1; py marked_windows smallpole smallpole wspole 1
py marked_audit control; py marked_replay control; py marked_joint control; py marked_sample control
py marked_prism control; py hole_lrat control; py marked_audit geometry
run ./price price 1 full; run ./price pole 1 pole
py marked_windows price full wmark 1; py marked_windows pole pole wpole 1
py marked_replay target; py marked_joint price
py marked_sample target; py marked_nine extract; py marked_nine cert
py marked_prism bank; py marked_prism price; py marked_finish
