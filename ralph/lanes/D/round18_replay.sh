#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
cd "$root"
dest=${1:?supply a fresh audit directory in your scratch area}
mkdir "$dest"
dest=$(cd "$dest" && pwd)
lane="$root/ralph/lanes/D"
source_dir="$root/scratch/D/triple18"
sha256sum -c "$lane/ROUND18_FREEZE.sha256"
cd "$dest"
ulimit -v 524288
run() { (ulimit -t 120; exec nice -n 5 timeout 150 python3 -B "$@"); }
run "$lane/triple18.py" controls > controls.log
run "$lane/triple18.py" census roster.jsonl > census.log
run "$lane/triple18_audit.py" roster.jsonl witnesses.tsv > audit.log
run "$lane/triple18_price.py" roster.jsonl > price.log
for file in controls.log census.log roster.jsonl witnesses.tsv audit.log; do cmp "$file" "$source_dir/$file"; done
diff <(sed '$d' price.log) <(sed '$d' "$source_dir/price.log")
echo 'PASS five byte-identical artifacts and deterministic pricing; zero target wing pairs constructed'
