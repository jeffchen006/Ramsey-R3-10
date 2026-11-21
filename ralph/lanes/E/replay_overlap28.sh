#!/bin/bash
set -euo pipefail
lane=../../ralph/lanes/E
tools=../../opt/bin
catalogue="$lane/overlap17.g6"
echo "3286c5366ddc70f349c3f7e798d7acbc79dc026c7abe0c8f406cad41ca990361  $catalogue" | sha256sum -c -
limited() { local budget=$1; shift; nice -n 5 timeout "$((budget + 15))" bash "$lane/limited.sh" "$budget" "$@"; }
limited 5 "$tools/shortg" -q -T"$PWD" "$catalogue" overlap17.canon.g6
test "$(wc -l < overlap17.canon.g6)" = 7
limited 10 python3 -B "$lane/overlap_scalar.py" "$catalogue"
