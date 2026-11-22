#!/bin/bash
set -eu
lane=$(cd "$(dirname "$0")" && pwd);root=$(cd "$lane/../../.." && pwd)
case "$PWD" in "$root"/scratch/F/*) ;; *) echo 'use an empty directory inside scratch/F' >&2; exit 2;; esac
test -z "$(ls -A .)" || exit 2
ulimit -v 524288
run(){ nice -n 5 timeout 30 prlimit --cpu=20 -- "$@"; }
py(){ run "$root/opt/venv/bin/python" -B "$lane/$1.py" "${@:2}"; }
run g++ -std=c++20 -O3 -march=native "$lane/marked_bank.cpp" -o bank
py marked_bank control; run ./bank small.q 4 small.bank small.rows small.trace 8 > small.out
py marked_bank_check small small.rows small.bank small.trace; py marked_bank_check tamper
py marked_bank prepare
for tag in pilot target;do
    run ./bank core.q 10 frozen.bank "$tag.rows" "$tag.trace" 8 > "$tag.out"
    py marked_bank_check "$tag" "$tag.rows" frozen.bank "$tag.trace"
done
py marked_bank finish;py marked_bank extend
for tag in restpilot rest;do
    run ./bank core.q 10 wider.bank "$tag.rows" "$tag.trace" 8 > "$tag.out"
    py marked_bank_check "$tag" "$tag.rows" wider.bank "$tag.trace"
done
py marked_bank final
orig=$root/scratch/F/r18
for file in *.checked *.trace *.bank *.rows *.left *.q *.tsv *.g6;do cmp "$file" "$orig/$file";done
echo 'All bank, roster, receipt, checked cut, marginal, physical graph and price files matched.'
