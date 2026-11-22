#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname "$0")/../../.." && pwd); src=$root/ralph/lanes/D; data=$root/scratch/D/roles15
dest=$(realpath -m "${1:?give a writable scratch destination}"); workers=${2:-2}
[[ $workers =~ ^[1-8]$ ]]; mkdir -p "$dest";cd "$dest"; ulimit -v 16777216
export TMPDIR=$dest PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
run(){ nice -n 5 timeout 240 prlimit --cpu=190:191 "$@"; }
run g++ -O3 -std=c++17 -mpopcnt "$src/roles15_catalog.cpp" -o ./catalog
for width in 6 8;do run ./catalog "$width" >"ind-$width.pop" 2>"ind-$width.log";done
run "$root/opt/venv/bin/python" -B "$src/roles15_replay.py" catalog "$dest" >catalog.log;cat catalog.log
replay(){ local shard=$1; run "$root/opt/venv/bin/python" -B "$src/roles15_replay.py" formulas "$dest" "$shard" "$workers" >"tags.$shard" || return 1
    while read -r tag digest; do
        for checker in cake_lpr lrat-check; do run "$root/opt/bin/$checker" "$tag.cnf" "$data/$tag.lrat" >"$tag.$checker.log" || return 1; rg -q VERIFIED "$tag.$checker.log" || return 1;done
        rm "$tag.cnf";printf '%s %s\n' "$tag" "$digest"
    done <"tags.$shard"; }
pids=();for ((shard=0;shard<workers;shard++));do replay "$shard" >"checked.$shard" & pids+=("$!");done
for pid in "${pids[@]}";do wait "$pid";done
cat checked.[0-9] | sort >completed.tsv;[[ $(wc -l <completed.tsv) == 288 ]];echo 'PASS 287 cover CNFs and one alternative unsplit hex proof; both checkers on freshly generated hashes'
