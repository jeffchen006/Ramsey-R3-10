#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
work="$root/scratch/A/r15"
lane="$root/ralph/lanes/A"
verify="$root/ralph/lanes/A/ROUND14_FREEZE.sha256"
mkdir -p "$work"
cd "$work"
export TMPDIR="$PWD" LC_ALL=C
ulimit -v 16777216 -t 120 -c 0
run() { nice -n 5 timeout 150 "$@"; }
timed() {
    local file=$1
    shift
    /usr/bin/time -o "$file.time" -f '%U %S %e %M' nice -n 5 timeout 150 "$@"
}
(
    cd "$root"
    run sha256sum -c "$verify"
) > prefix.freeze.log

timed build g++ -O3 -Wall -Wextra -Werror -std=c++20 "$lane/audit_panel_exchange.cpp" \
    -Wl,-l:libcrypto.so.3 -o exchange
timed headers-build g++ -O3 -Wall -Wextra -Werror -std=c++20 "$lane/audit_panel_headers.cpp" -o headers
timed controls "$root/opt/venv/bin/python" -B "$lane/audit_exchange_controls.py" \
    "$root/gluing/val/r3_7_22.g6" ./exchange | tee controls.log

heads=./headers
frames="$root/scratch/ideas/r012_R/frames17-5-2.txt"
graphs="$root/gluing/val/r3_6_17.g6"
timed full bash -o pipefail -c '"$1" "$2" "$3" 0 55055 packed 2>ordered.stderr | ./exchange full 55055 24576 1024 > census.tmp' \
    -- "$heads" "$graphs" "$frames"
mv census.tmp census.tsv
timed first bash -o pipefail -c '"$1" "$2" "$3" 24576 25600 packed 2>first.ordered.stderr | ./exchange upper 55055 24576 25600 > first.tsv' \
    -- "$heads" "$graphs" "$frames"
awk '$1==24576 && $2==25600 && ($3=="HHrep" || $3=="HHdiag")' census.tsv > first.expected.tsv
cmp first.tsv first.expected.tsv
args=(census.tsv ../r14/headers.packed.shards.tsv ../r14/headers.packed.full.tsv ../../C/r14 ../../C/r13)
timed receipts "$root/opt/venv/bin/python" -B "$lane/audit_exchange_receipts.py" "${args[@]}" coverage.initial.tsv | tee receipts.initial.log
status=0
run "$root/opt/venv/bin/python" -B "$lane/audit_exchange_receipts.py" \
    "${args[@]}" must-not-publish.tsv --require-full > incomplete.stdout 2> incomplete.stderr || status=$?
test "$status" -eq 1 && test ! -e must-not-publish.tsv && rg -q 'HH representative partition incomplete' incomplete.stderr
if (($#)); then
    timed published "$root/opt/venv/bin/python" -B "$lane/audit_exchange_receipts.py" \
        "${args[@]}" coverage.published.tsv "$@" | tee receipts.published.log
fi
