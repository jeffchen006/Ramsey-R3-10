#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)
work="$root/scratch/A/${1:?give a fresh scratch/A subdirectory}"
[[ $work =~ ^$root/scratch/A/[[:alnum:]_-]+$ ]]
mkdir -- "$work"
cd -- "$work"
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1 TMPDIR="$work"
ulimit -v 524288
ulimit -f 262144
python="$root/opt/venv/bin/python"
source_dir="$root/ralph/lanes/A"
timed() {
    local name=$1 cpu=$2
    shift 2
    /usr/bin/time -f 'user=%U sys=%S rss=%M elapsed=%e exit=%x' -o "$name.time" \
        nice -n 5 timeout --kill-after=2 150s prlimit --cpu="$cpu" "$@" >"$name.log" 2>&1
}
timed small 60 "$python" -B "$source_dir/two_defect_oracle22.py" full . --historical
timed boards 30 "$python" -B "$source_dir/h6_boards22.py" .
timed positive 90 "$python" -B "$source_dir/two_defect_oracle22.py" positive positive
for filename in h6.{boards,labels,holes}.tsv n{16,17}.d2.{classes.tsv,placements.jsonl} positive/n16.d2.{classes.tsv,placements.jsonl}; do
    cmp -- "$filename" "$root/scratch/A/r22/$filename"
    printf 'byte-identical %s\n' "$filename"
done
if [[ -n ${2:-} ]]; then
    for filename in n{16,17}.{mutations.json,d2.summary.tsv} positive/n16.{mutations.json,d2.summary.tsv}; do
        cmp -- "$filename" "$root/scratch/A/r22/$filename"
        printf 'byte-identical %s\n' "$filename"
    done
fi
