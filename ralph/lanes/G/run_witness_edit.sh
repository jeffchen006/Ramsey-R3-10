#!/usr/bin/env bash
set -euo pipefail
if (( $# < 3 || $# > 4 )); then
    echo "usage: $0 input.g6 add-count output.g6 [remove-count=2] (cwd = lane scratch)" >&2
    exit 2
fi
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
ulimit -v 16777216
ulimit -t 90
{
    /usr/bin/time -f 'edit user=%U system=%S wall=%e' nice -n 5 timeout 140s ./witness_edit 8 5 "${4:-2}" "$2" < "$1" | \
        /usr/bin/time -f 'canon user=%U system=%S wall=%e' nice -n 5 timeout 140s "$root/opt/bin/shortg" -q > "$3.partial"
} 2> "$3.log"
mv -- "$3.partial" "$3"
