#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
if [[ $# != 1 ]]; then
    echo 'Usage: replay_panel17.sh CALLER_OWNED_EMPTY_WORKDIR' >&2
    exit 2
fi
mkdir -p "$1"
cd "$1"
[[ ! -e panel17 && ! -e pilot.ids ]]
export TMPDIR="$PWD" LC_ALL=C PYTHONDONTWRITEBYTECODE=1
ulimit -v 16777216 -c 0 -t 180
src="$root/ralph/lanes/C"
ref="$root/scratch/ideas/r012_R"
record="$root/scratch/C/r13"
val="$root/gluing/val"
bin="$root/opt/venv/bin/python"
args=("$val/r3_6_17.g6" "$ref/liftrows.txt" "$ref/frames17-5-2.txt")
run() { nice -n 5 timeout 150 "$@"; }
(cd "$root"; sha256sum -c "$src/ROUND13_INPUTS.sha256")
run g++ -O3 -Wall -Wextra -Werror -std=c++20 "$src/panel17.cpp" -o panel17
run g++ -O3 -std=c++20 "$record/audit_A.cpp" -o audit_A
run ./audit_A controls "$val" > A.small-atlas 2>A.controls.log
cmp A.small-atlas "$ref/direct-small.txt"
run ./panel17 controls < "$ref/panel-controls.txt"
run "$bin" -B "$src/verify_panel17.py" controls > terminal.controls
run ./panel17 terminal-controls < terminal.controls
for row in '147031 20000000' '6035 200000' '441703 12000'; do
    read -r seed draws <<< "$row"
    run ./panel17 legacy "${args[@]}" "$seed" "$draws" > "legacy.$seed.ids"
done
cmp legacy.441703.ids "$ref/headers.txt"
cat legacy.*.ids > legacy.ids
run sort -u legacy.ids > legacy.unique
run sort -u "$ref/held.txt" "$ref/livepilot.txt" > legacy.survivors
comm -23 legacy.survivors legacy.unique > legacy.missing
test ! -s legacy.missing
run ./panel17 pilot "${args[@]}" legacy.ids pilot.strata > pilot.ids 2>pilot.roster.log
run "$bin" -B "$src/verify_panel17.py" roster > pilot.audit.log
run ./panel17 triple "${args[@]}" legacy.ids triple.strata > triple.ids 2>triple.roster.log
for scope in pilot triple; do
    run ./panel17 stages "${args[@]}" < "$scope.ids" > "C.$scope.stages" 2>"C.$scope.log"
    run ./audit_A slice "$val" "$ref/frames17-5-2.txt" A.atlas "$scope.ids" \
        > "A.$scope.stages" 2>"A.$scope.log"
    cmp "C.$scope.stages" "A.$scope.stages"
    cmp A.atlas "$ref/direct21.txt"
    cmp A.atlas "$ref/liftrows.txt"
done
awk '$4 == 5 {print $1, $2, $3}' C.pilot.stages > A.pilot.live
test "$(wc -l < A.pilot.live)" -eq 327
test "$(awk '$4 == 5 {count++} END {print count+0}' C.triple.stages)" -eq 0
run ./panel17 terminal "${args[@]}" < A.pilot.live > C.terminal.tsv
for input in frames17-5-2.txt liftrows.txt; do cp "$ref/$input" "$input"; done
run "$bin" -B "$src/verify_panel17.py" scout A.pilot.live > scout.perid.tsv
cut -d' ' -f1-8 C.terminal.tsv > terminal.keyed
cut -d' ' -f1-8 scout.perid.tsv > scout.keyed
cmp terminal.keyed scout.keyed
run "$bin" -B "$src/verify_panel17.py" summary C.terminal.tsv
sha256sum -c "$src/ROUND13_RESULTS.sha256"
