#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 1 || $# -gt 3 ]]; then
    echo 'usage: replay_panel16.sh EMPTY_OWNED_DIRECTORY [comparison|full] [A_MANIFEST]' >&2
    exit 2
fi
lane=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
repo=$(cd -- "$lane/../../.." && pwd)
mode=${2:-comparison}
source_dir=$(realpath -- "${3:-$repo/scratch/A/r16}")
case $mode in comparison|full) ;; *) exit 2 ;; esac
mkdir -p -- "$1"
cd -- "$1"
test -z "$(ls -A)"
test "${PWD#"$repo/"}" != "$PWD"
ulimit -v 524288
ulimit -f 262144
timed() {
    local tag=$1 wall=$2 soft=$3 hard=$4
    shift 4
    nice -n 5 timeout "$wall" prlimit --cpu="$soft:$hard" /usr/bin/time -o "$tag.time" -f '%U %S %e %M' "$@"
}
export TMPDIR=$PWD
small="$repo/gluing/val/r3_6_16.g6"
large="$repo/gluing/val/r3_6_17.g6"
timed build 90 60 65 g++ -O3 -Wall -Wextra -std=c++17 "$lane/panel16.cpp" -o panel16
timed plants 45 30 32 python3 -B "$lane/panel16_audit.py" controls "$small" . > plants.log
timed controls 45 30 32 ./panel16 control6.g6 control7.g6 controls.tsv controls.fills controls.stats 5 4 5 2
timed audit-controls 45 30 32 python3 -B "$lane/panel16_audit.py" audit control6.g6 control7.g6 controls.tsv controls.fills controls.stats 5 4 5 2 --plants plants.tsv > controls.log
python3 -B "$lane/panel16_summary.py" manifest "$source_dir" cases.tsv
timed pilot 100 75 80 ./panel16 "$small" "$large" cases.tsv pilot.fills pilot.stats 9 5 9 4
timed preflight 90 60 65 ./panel16 "$small" "$large" cases.tsv preflight.fills preflight.stats 9 5 9 4 preflight
if [[ $mode == full ]]; then
    timed audit 540 420 430 python3 -B "$lane/panel16_audit.py" audit "$small" "$large" cases.tsv pilot.fills pilot.stats 9 5 9 4 --screen --timing > audit.log
    python3 -B "$lane/panel16_summary.py" summary "$source_dir" . > summary.log
fi
