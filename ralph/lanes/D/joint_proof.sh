#!/usr/bin/env bash
set -eu
root=$(cd "$(dirname "$0")/../../.." && pwd)
ulimit -v 16777216
index=$1 panel=$2 arm=$3 cap=${4:-35}
tag=$index-$panel-$arm
mkdir -p arms
cd arms
run() { nice -n 5 timeout "$1" prlimit --cpu="$2" "${@:3}"; }
/usr/bin/time -f 'CPU %U %S RSS %M' -o "$tag.btime" nice -n 5 timeout 120 prlimit --cpu=90:91 "$root/opt/venv/bin/python" -B "$root/ralph/lanes/D/joint_deck.py" ../../punct8/path.tsv --index "$index" --panel "$panel" --arm "$arm" --out "$tag.cnf" > "$tag.build"
set +e
/usr/bin/time -f 'CPU %U %S RSS %M stat %x' -o "$tag.time" nice -n 5 timeout "$((3*cap+15))" prlimit --cpu="$cap:$((cap+1))" "$root/opt/bin/cadical" -q --lrat --no-binary "$tag.cnf" "$tag.lrat" > "$tag.sol" 2>&1
status=$?
set -e
if [[ $status == 20 ]]; then
    if rg -q '^0$' "$tag.cnf"; then
        awk 'NR==1 {last=$4} /^0$/ {print last+1,0,NR-1,0; exit}' "$tag.cnf" >"$tag.empty.lrat"
        witness=$tag.empty.lrat
    else witness=$tag.lrat; fi
    run 180 120:121 "$root/opt/bin/cake_lpr" "$tag.cnf" "$witness" > "$tag.cake"
    run 180 120:121 "$root/opt/bin/lrat-check" "$tag.cnf" "$witness" > "$tag.check"
    rg -q '^s VERIFIED UNSAT' "$tag.cake" && rg -q '^c VERIFIED' "$tag.check"
else rm -f "$tag.lrat"; fi
printf '%s\t%s\n' "$tag" "$status" > "$tag.status"
