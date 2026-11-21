#!/usr/bin/env bash
set -euo pipefail

root=$(cd "$(dirname "$0")/../../.." && pwd -P)
cd "$root/scratch/C"
ulimit -v 16777216
target=${1:-p3-top-certs}
mode=${2:-produce}
if [[ $mode != produce && $mode != verify ]]; then
    exit 2
fi
case "$target" in
    p3-top-*) ;;
    *) exit 2;;
esac
if [[ $mode == produce ]]; then
    mkdir "$target"
fi
cnfs="$target/cnf-$mode"
mkdir "$cnfs"
nice -n 5 timeout 90 python3 -B "$root/ralph/lanes/C/path_three_top.py" \
    "$root/gluing/val/r3_7_22.g6" --cnf-dir "$cnfs"
[[ $(find "$cnfs" -name '*.cnf' | wc -l) -eq 10 ]]
for cnf in "$cnfs"/*.cnf; do
    name=$(basename "$cnf" .cnf)
    proof="$target/$name.lrat"
    if [[ $mode == produce ]]; then
        status=0
        nice -n 5 timeout 20 "$root/opt/bin/cadical" -q --lrat "$cnf" "$proof" >"$target/$name.solve" || status=$?
        [[ $status -eq 20 ]]
        rg -x 's UNSATISFIABLE' "$target/$name.solve"
    fi
    nice -n 5 timeout 20 "$root/opt/bin/cake_lpr" "$cnf" "$proof" >"$target/$name.$mode.check"
    rg -x 's VERIFIED UNSAT' "$target/$name.$mode.check"
    printf '%s\t%s\t%s\n' "$name" "$(sha256sum "$cnf" | cut -d' ' -f1)" "$(sha256sum "$proof" | cut -d' ' -f1)"
done >"$target/$mode.index"
if [[ $mode == verify ]]; then
    diff -u "$target/produce.index" "$target/verify.index"
fi
cat "$target/$mode.index"
rm "$cnfs"/*.cnf
rmdir "$cnfs"
echo "TERMINAL 10 checked P3-top LRAT certificates ($mode)"
