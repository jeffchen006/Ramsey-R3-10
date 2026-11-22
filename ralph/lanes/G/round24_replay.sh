#!/usr/bin/env bash
set -euo pipefail
root=$(realpath "$(dirname "$0")/../../..")
src="$root/ralph/lanes/G"
stage="$root/scratch/G/round24"
previous="$root/scratch/G/round22/h5"
tools="$root/opt/bin"
python="$root/opt/venv/bin/python"
test "$PWD" = "$stage"
export PYTHONDONTWRITEBYTECODE=1 LC_ALL=C
ulimit -v 5242880
run() { timeout --foreground --kill-after=5 250 prlimit --cpu=145:145 -- "$@"; }
tag=$1
shift
mkdir "replay-$tag"
for id in "$@"; do
    (
        folder="$stage/work/$id"
        archive="$stage/archive/$id.lrat.zst"
        rg -q '^CHECKED ' "$folder/result"
        mkdir "replay-$tag/$id"
        cd "replay-$tag/$id"
        read -r board prefix mode name <"$folder/job"
        test "$name" = "$id"
        case "$mode" in
            DP)
                cp "$folder/shore.jsonl" .
                run "$python" -B "$src/round24_shore.py" emit "$previous/manifest.json" "$board" "$prefix" --shore shore.jsonl >grid.cnf 2>binding.json
                run "$python" -B "$src/round24_shore_audit.py" "$previous/manifest.json" "$previous" "$board" "$prefix" "$mode" >audit.log
                ;;
            DN)
                cp "$folder/scope.json" .
                run "$python" -B "$src/round24_occupancy.py" emit "$previous/manifest.json" scope.json "$board" >grid.cnf 2>binding.json
                run "$python" -B "$src/round24_occupancy.py" audit "$previous/manifest.json" scope.json "$board" "$stage" >audit.log
                ;;
            D|DM)
                args=()
                if [[ $mode == *M* ]]; then
                    cp "$folder/witness.jsonl" .
                    args=(--witnesses witness.jsonl)
                fi
                run "$python" -B "$src/round23_deficit.py" emit "$previous/manifest.json" "$board" "$prefix" --deficit "${args[@]}" >grid.cnf 2>binding.json
                run "$python" -B "$src/round23_deficit_audit.py" "$previous/manifest.json" "$previous" "$board" "$prefix" "$mode" >audit.log
                ;;
            *) exit 2 ;;
        esac
        cmp grid.cnf "$folder/grid.cnf"
        cmp binding.json "$folder/binding.json"
        { head -1 "$folder/sha256"; tail -1 "$folder/sha256"; } | run sha256sum -c
        run bash -o pipefail -c 'zstd -qdc "$1" | sha256sum' bash "$archive" >ascii.sha256
        test "$(cut -d ' ' -f1 ascii.sha256)" = "$(awk 'NR==2{print $1}' "$folder/sha256")"
        run bash -o pipefail -c 'zstd -qdc "$1" | { "$2" grid.cnf; code=$?; cat >/dev/null; exit "$code"; }' bash "$archive" "$tools/lrat-check" >lrat.log
        run bash -o pipefail -c 'zstd -qdc "$1" | { "$2" --CML_HEAP_SIZE=512 --CML_STACK_SIZE=48 grid.cnf /dev/stdin; code=$?; cat >/dev/null; exit "$code"; }' bash "$archive" "$tools/cake_lpr" >cake.log
        rg -qx 'c VERIFIED' lrat.log
        rg -qx 's VERIFIED UNSAT' cake.log
        printf '%s %s %s %s fresh stream dual\n' "$id" "$board" "$prefix" "$mode"
    )
done
