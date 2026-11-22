#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$root"
dest=${1:?supply a fresh audit directory in your scratch area}
mkdir "$dest"
dest=$(cd "$dest" && pwd)
lane=$root/ralph/lanes/D
frozen=$root/scratch/D/wing19
roster=$root/scratch/D/triple18/roster.jsonl
sha256sum -c "$lane/ROUND19_FREEZE.sha256"
cd "$dest"
run() { (ulimit -v 65536; ulimit -t "$1"; shift; exec nice -n 5 timeout 120 python3 -B "$@"); }
run 15 "$lane/wing19.py" controls >controls.log
run 15 "$lane/wing19_audit.py" toy >toy.log
run 90 "$lane/wing19.py" "$roster" counts.tsv >target.log
run 15 "$lane/wing19_audit.py" price >price.log
run 90 "$lane/wing19_audit.py" "$roster" counts.tsv >audit.log
run 15 "$lane/wing19_filterprice.py" >filterprice.log
for file in counts.tsv controls.log toy.log target.log audit.log; do cmp "$file" "$frozen/$file"; done
diff <(sed -E 's/ [0-9.]+( CPU-s)?$//' price.log) <(sed -E 's/ [0-9.]+( CPU-s)?$//' "$frozen/price.log")
diff <(sed -E 's/(CPU-s) [0-9.]+$/\1/' filterprice.log) <(sed -E 's/(CPU-s) [0-9.]+$/\1/' "$frozen/filterprice.log")
echo 'PASS all 162 hosts / 267 fixed counts; five byte comparisons plus synthetic price invariants'
