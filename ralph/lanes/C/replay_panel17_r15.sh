#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
if [[ $# != 3 || ( $3 != first && $3 != full ) ]]; then
    echo 'Usage: replay_panel17_r15.sh OWNED_EMPTY_WORKDIR A_CENSUS_TSV {first|full}' >&2
    exit 2
fi
census=$(realpath "$2")
mode=$3
mkdir -p "$1"
cd "$1"
test -z "$(ls -A)"
ulimit -v 16777216 -c 0
if [[ $mode == first ]]; then
    ulimit -t 600
else
    ulimit -t 3600
fi
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD"
source_dir="$root/ralph/lanes/C"
old="$root/scratch/C/r14"
scout="$root/scratch/ideas/r012_R"
run() { nice -n 5 timeout "$@"; }
cp "$census" A.census.tsv
for name in scan_C scan_A panel17; do
    case "$name" in
        scan_C) code=panel17_triangle_C.cpp;;
        scan_A) code=panel17_triangle_A.cpp;;
        panel17) code=panel17.cpp;;
    esac
    run 120 g++ -O3 -Wall -Wextra -Werror -std=c++20 "$source_dir/$code" -o "$name"
done
ln -s "$scout/frames17-5-2.txt" "$scout/liftrows.txt" .
run 120 python3 -B "$source_dir/verify_panel17.py" controls > terminal.controls
cmp terminal.controls "$old/terminal.controls"
run 120 ./panel17 terminal-controls < terminal.controls
run 120 python3 -B "$source_dir/panel17_fast_r15.py" controls terminal.controls
run 120 ./scan_A controls "$root/gluing/val" > A.small-atlas
cmp A.small-atlas "$scout/direct-small.txt"
run 120 ./panel17 controls < "$scout/panel-controls.txt"
cp "$root/scratch/critic/r14/C/tail/fixed" tail.expected
cp "$old/00000-02048/terminal.keyed" easy.expected
for sample in tail easy; do
    cut -d' ' -f1-3 "$sample.expected" > "$sample.ids"
    run 120 python3 -B "$source_dir/panel17_fast_r15.py" audit "$sample.ids" > "$sample.tsv" 2> "$sample.stats"
    cut -d' ' -f1-8 "$sample.tsv" | cmp "$sample.expected" -
done
run 420 python3 -B "$source_dir/panel17_round15.py" . A.census.tsv first | tee first.log
if [[ $mode == full ]]; then
    run 2500 python3 -B "$source_dir/panel17_round15.py" . A.census.tsv rest | tee rest.log
    run 100 python3 -B "$source_dir/audit_panel17_r15.py" . --require-full | tee audit.log
else
    run 100 python3 -B "$source_dir/audit_panel17_r15.py" . | tee audit.log
fi
