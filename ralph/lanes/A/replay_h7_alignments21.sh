#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
cd "$root"
name=${1:-r21-review}
phase=${2:-replay}
[[ $name =~ ^r21-[a-zA-Z0-9_-]+$ ]]
[[ $phase == replay || $phase == full ]]
cpu=25 wall=35
if [[ $phase == full ]]; then cpu=100 wall=130; fi
sha256sum -c --quiet ralph/lanes/A/ROUND21_FREEZE.sha256
mkdir "scratch/A/$name"
cd "scratch/A/$name"
nice -n 5 timeout -k 4s "${wall}s" prlimit --cpu="$cpu" --as=536870912 -- \
  /usr/bin/time -f '%U %S %e %M %x' -o "$phase.time" python3 -B -u \
  "$root/ralph/lanes/A/count_h7_alignments21.py" "$phase" > "$phase.log" 2>&1
for table in alignments.tsv prefix.tsv; do
  cmp "$table" "../r21/$table"
done
echo 'PASS: both TSV tables byte-identical'
