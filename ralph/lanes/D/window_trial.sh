#!/usr/bin/env bash
set -eu
ulimit -v 16777216
root=$(cd "$(dirname "$0")/../../.." && pwd)
tag=$1 cap=$2 index=$3; shift 3
mkdir -p windows
cd windows
/usr/bin/time -f 'CPU %U %S RSS %M' -o "$tag.btime" nice -n 5 timeout 170 prlimit --cpu=120:121 "$root/opt/venv/bin/python" -B "$root/ralph/lanes/D/joint_windows.py" ../../punct8/path.tsv --index "$index" --out "$tag.cnf" "$@" >"$tag.build"
set +e
/usr/bin/time -f 'CPU %U %S RSS %M status %x' -o "$tag.time" nice -n 5 timeout "$((3*cap+15))" prlimit --cpu="$cap:$((cap+1))" "$root/opt/bin/cadical" -q --lrat --no-binary "$tag.cnf" "$tag.lrat" >"$tag.sol" 2>&1
status=$?
set -e
if [[ $status == 20 ]]; then
    witness=$tag.lrat
    if rg -q '^0$' "$tag.cnf"; then
        witness=$tag.empty.lrat
        awk 'NR==1 {last=$4} /^0$/ {print last+1,0,NR-1,0; exit}' "$tag.cnf" >"$witness"
    fi
    for checker in cake_lpr lrat-check; do
        /usr/bin/time -f 'CPU %U %S RSS %M' -o "$tag.$checker.time" nice -n 5 timeout 320 prlimit --cpu=200:201 "$root/opt/bin/$checker" "$tag.cnf" "$witness" >"$tag.$checker.log"
    done
    rg -q '^s VERIFIED UNSAT' "$tag.cake_lpr.log" && rg -q '^c VERIFIED' "$tag.lrat-check.log"
else rm -f "$tag.lrat"; fi
printf '%s\t%s\n' "$tag" "$status" > "$tag.status"
