#!/usr/bin/env bash
set -eu
index=$1
root=$(cd "$(dirname "$0")/../../.." && pwd)
out=${2:-links}
panel=${3:-}
mkdir -p "$out"
ulimit -v 16777216
if [[ -n $panel ]]; then
    profile=$index
    index=$index-$panel
    nice -n 5 timeout 60 prlimit --cpu=45:46 "$root/opt/venv/bin/python" -B "$root/ralph/lanes/D/${PANEL_DRIVER:-path_panel.py}" path.tsv --index "$profile" --panel "$panel" --out "$out/$index.cnf" ${EXTRA_LINK_ARGS:-} >"$out/$index.build"
else
    nice -n 5 timeout 60 prlimit --cpu=45:46 "$root/opt/venv/bin/python" -B "$root/ralph/lanes/D/path_links.py" path.tsv --index "$index" --out "$out/$index.cnf" ${EXTRA_LINK_ARGS:-} >"$out/$index.build"
fi
set +e
/usr/bin/time -f 'CPU %U %S RSS %M status %x' -o "$out/$index.time" nice -n 5 timeout 65 prlimit --cpu=20:21 "$root/opt/bin/cadical" -q -n --lrat --no-binary "$out/$index.cnf" "$out/$index.lrat" >"$out/$index.log" 2>&1
status=$?
set -e
if [[ $status = 20 ]]; then
    witness=$out/$index.lrat
    if rg -q '^0$' "$out/$index.cnf"; then
        witness=$out/$index.empty.lrat
        awk 'NR==1 {last=$4} /^0$/ {print last+1,0,NR-1,0; exit}' "$out/$index.cnf" >"$witness"
    fi
    nice -n 5 timeout 60 prlimit --cpu=45:46 "$root/opt/bin/cake_lpr" "$out/$index.cnf" "$witness" >"$out/$index.cake"
    nice -n 5 timeout 60 prlimit --cpu=45:46 "$root/opt/bin/lrat-check" "$out/$index.cnf" "$witness" >"$out/$index.check"
    rg -q '^s VERIFIED UNSAT' "$out/$index.cake" && rg -q '^c VERIFIED' "$out/$index.check"
fi
