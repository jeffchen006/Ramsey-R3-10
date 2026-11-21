#!/usr/bin/env bash
set -eo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
source "$root/opt/env.sh"
cd "$root/scratch/A/rc7"
ulimit -v 16777216
ulimit -f 262144
mkdir -p fresh-sample
cp L300.log fresh-sample/cubing.snapshot.log
python "$root/ralph/lanes/A/rc7_inputs.py" extract fresh-sample/cubing.snapshot.log fresh-sample/cubes
for cube in "$@"; do
    out="fresh-sample/c$cube"
    python "$root/ralph/lanes/A/rc7_inputs.py" units Rc7b.cnf fresh-sample/cubes "$out.cnf" "$cube"
    status=0
    /usr/bin/time -f 'TIMING wall=%e user=%U sys=%S rss_kb=%M exit=%x' \
        nice -n 5 timeout 80 prlimit --cpu=45:48 smsg -v 40 --dimacs "$out.cnf" \
        --forbid-independent-set 10 --initial-partition 1 7 2 1 2 27 --proof-log "$out.plog" \
        --sym-break-clauses "$out.sym.json" > "$out.log" 2>&1 || status=$?
    printf '%s %s\n' "$cube" "$status" | tee -a fresh-sample/status
    if test "$status" -eq 20; then
        nice -n 5 timeout 90 python "$root/ralph/lanes/A/check_sms.py" "$out.cnf" "$out.plog" "$out.sym.json" \
            --n 40 --k 10 --blocks 1 7 2 1 2 27 --allow-input-extras > "$out.check.log" 2>&1 || :
    elif test "$status" -eq 10; then
        printf 'SAT on fresh probe %s; inspect %s.log\n' "$cube" "$out"
        exit 10
    fi
done
