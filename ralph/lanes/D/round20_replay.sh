#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$root"
dest=${1:?supply a fresh directory under your scratch area}
mkdir "$dest"
dest=$(cd "$dest" && pwd)
lane=$root/ralph/lanes/D
frozen=$root/scratch/D/wing20
roster=$root/scratch/D/triple18/roster.jsonl
old=$root/scratch/D/wing19/counts.tsv
sha256sum -c "$lane/ROUND19_FREEZE.sha256" >"$dest/inputs.log"
sha256sum -c "$lane/ROUND20_FREEZE.sha256"
cd "$dest"
run() { (ulimit -v 65536; ulimit -t "$1"; shift; exec nice -n 5 timeout 120 python3 -B "$@"); }
run 15 "$lane/wing20.py" controls >controls.log
run 15 "$lane/wing20_audit.py" toy >toy.log
run 30 "$lane/wing20.py" "$roster" "$old" counts.tsv >target.log
run 60 "$lane/wing20_audit.py" "$roster" "$old" counts.tsv >audit.log
run 10 "$lane/wing20_nextprice.py" >nextprice.log
for item in inputs.log controls.log toy.log counts.tsv target.log audit.log; do cmp "$item" "$frozen/$item"; done
diff <(sed -E 's/(CPU-s) [0-9.]+$/\1/' nextprice.log) <(sed -E 's/(CPU-s) [0-9.]+$/\1/' "$frozen/nextprice.log")
echo 'PASS two-site count, all 267 old/new/removed fixed counts and 162 hosts; next-price toy only'
