#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
if [[ $# != 1 ]]; then
    echo 'Usage: replay_panel17_r14.sh CALLER_OWNED_EMPTY_WORKDIR' >&2
    exit 2
fi
mkdir -p "$1"
cd "$1"
test -z "$(ls -A)"
ulimit -v 16777216 -c 0 -t 600
export TMPDIR="$PWD" LC_ALL=C PYTHONDONTWRITEBYTECODE=1
source_dir="$root/ralph/lanes/C"
reference="$root/scratch/ideas/r012_R"
results="$root/scratch/C/r14"
run() { nice -n 5 timeout 120 "$@"; }
(cd "$root"; sha256sum -c "$source_dir/ROUND13_INPUTS.sha256"; sha256sum -c "$source_dir/ROUND14_INPUTS.sha256")
for binary in 'panel17.cpp panel17' 'panel17_shard_C.cpp scan_C' 'panel17_shard_A.cpp scan_A'; do
    read -r code output <<< "$binary"
    run g++ -O3 -Wall -Wextra -Werror -std=c++20 "$source_dir/$code" -o "$output"
done
run ./scan_A controls "$root/gluing/val" > A.small-atlas 2>A.controls.log
cmp A.small-atlas "$reference/direct-small.txt"
run ./panel17 controls < "$reference/panel-controls.txt"
run python3 -B "$source_dir/verify_panel17.py" controls > terminal.controls
run ./panel17 terminal-controls < terminal.controls
run python3 -B "$source_dir/audit_panel17_r14.py"
run python3 -B "$source_dir/panel17_round14.py" "$PWD" first | tee first.log
run python3 -B "$source_dir/audit_panel17_r14.py" "$PWD" "$results/A.coverage.tsv" | tee audit.log
head -n 2 "$results/coverage.tsv" | cmp coverage.tsv -
