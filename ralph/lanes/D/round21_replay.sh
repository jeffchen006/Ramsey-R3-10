#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$root"
mkdir "${1:?supply a new scratch directory}"
dest=$(cd "$1" && pwd)
lane=$root/ralph/lanes/D
frozen=$root/scratch/D/wing21
roster=$root/scratch/D/triple18/roster.jsonl
old=$root/scratch/D/wing20/counts.tsv
sha256sum -c "$lane/ROUND21_FREEZE.sha256"
sha256sum -c "$lane/ROUND20_FREEZE.sha256" >"$dest/inputs.log"
cd "$dest"
run() { (ulimit -v 65536; ulimit -t "$1"; shift; exec nice -n 5 timeout 100 python3 -B "$@"); }
run 20 "$lane/wing21.py" controls >controls.log
(ulimit -v 1048576; ulimit -t 15; exec nice -n 5 timeout 25 g++ -std=c++17 -O2 -mpopcnt -fPIC -shared "$lane/wing21_literal.cc" -o literal.so)
run 15 "$lane/wing21_audit.py" "$dest/literal.so" controls >auditprice.log
run 30 "$lane/wing21.py" "$roster" "$old" counts.tsv >target.log
run 60 "$lane/wing21_audit.py" "$dest/literal.so" "$roster" "$old" counts.tsv >audit.log
run 15 "$lane/wing21_nextprice.py" >nextprice.log
for file in inputs.log controls.log counts.tsv target.log audit.log; do cmp "$file" "$frozen/$file"; done
for file in nextprice.log auditprice.log; do
  diff <(sed -E 's/(CPU-s) [0-9.]+$/\1/' "$file") <(sed -E 's/(CPU-s) [0-9.]+$/\1/' "$frozen/$file")
done
echo 'PASS independent old/new counts and all 264 action deltas, 159 marked supports; future test synthetic/plants only'
