#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
export LC_ALL=C
root=../../..
gen=../../G/round9
py="$root/opt/venv/bin/python"
tool="$root/ralph/lanes/A/check_strip_replay_union.py"
replays=(mixed.hash.{0,1,2}.log)
for file in "${replays[@]}"; do
    [[ $(wc -l <"$file") == 2389 || $(wc -l <"$file") == 2390 ]]
done
"$py" -B "$tool" mixed.terminal.tsv 7166 "${replays[@]}" > mixed.union.log
awk 'NF==5&&$2~/^[0-9a-f]+$/{print $1,$2,$3}' "$gen/mixed26.bound/certificates.tsv" | sort > mixed.G.hashes
awk 'NF==5&&$4~/^[0-9a-f]+$/{print $1,$4,$5}' "${replays[@]}" | sort > mixed.A.hashes
cmp mixed.G.hashes mixed.A.hashes
printf '7166/7166 A and G digest rows match\n' > mixed.G.join.log
