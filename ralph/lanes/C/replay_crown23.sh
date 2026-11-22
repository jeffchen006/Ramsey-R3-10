#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
if [[ $# != 1 ]]; then
    printf 'usage: %s EXISTING_DIRECTORY_UNDER_scratch/C\n' "$0" >&2
    exit 2
fi
work=$(cd "$1" && pwd -P)
case "$work" in
    "$root"/scratch/C/*) ;;
    *) printf 'work directory must be under scratch/C\n' >&2; exit 2 ;;
esac
cd "$work"
set -o noclobber
/usr/bin/time -o replay.time -f '%U %S %e %M %x' nice -n 5 timeout 165s \
    bash -c 'ulimit -v 524288; ulimit -t 120; exec python3 -B "$1"' _ \
    "$root/ralph/lanes/C/audit_crown23_factor.py" > replay.log 2> replay.stderr
