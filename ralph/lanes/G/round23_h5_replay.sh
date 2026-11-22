#!/usr/bin/env bash
set -euo pipefail
root=$(realpath "$(dirname "$0")/../../..")
stage="$root/scratch/G/round23"
source="$root/ralph/lanes/G"
old="$root/scratch/G/round22/h5"
tools="$root/opt/bin"
test "$PWD" = "$stage"
export PYTHONDONTWRITEBYTECODE=1 LC_ALL=C
ulimit -v 5242880
mkdir -p fresh-replay
run() { timeout --kill-after=5 250 prlimit --cpu=145:145 -- "$@"; }
for ident in "$@"; do
  receipt="$stage/work/$ident"
  rg -q '^CHECKED ' "$receipt/result"
  mkdir "fresh-replay/$ident"
  (
    cd "fresh-replay/$ident"
    read -r board prefix mode saved < "$receipt/job"
    test "$ident" = "$saved"
    encoder="$source/round23_h5.py"
    auditor="$source/round23_h5_audit.py"
    options=()
    if [[ $mode == *D* ]]; then
      encoder="$source/round23_deficit.py"
      auditor="$source/round23_deficit_audit.py"
      options+=(--deficit)
    fi
    if rg -q '^physical exterior maximality delta:' "$receipt/audit.log"; then
      encoder="$source/round23_mtf.py"
      auditor="$source/round23_mtf_audit.py"
    fi
    if [[ $mode == *B* ]]; then options+=(--budget); fi
    if [[ $mode == *M* ]]; then
      cp "$receipt/witness.jsonl" witness.jsonl
      options+=(--witnesses "$PWD/witness.jsonl")
    fi
    run "$root/opt/venv/bin/python" -B "$encoder" emit "$old/manifest.json" "$board" "$prefix" "${options[@]}" \
      >grid.cnf 2>binding.json
    cmp grid.cnf "$receipt/grid.cnf"
    cmp binding.json "$receipt/binding.json"
    run "$root/opt/venv/bin/python" -B "$auditor" "$old/manifest.json" "$old" "$board" "$prefix" "$mode" >audit.log 2>&1
    run sha256sum -c <(tail -1 "$receipt/sha256")
    run zstd -qdc "$stage/archive/$ident.lrat.zst" >grid.lrat
    run sha256sum -c <(head -2 "$receipt/sha256")
    run "$tools/lrat-check" grid.cnf grid.lrat >lrat.log
    run "$tools/cake_lpr" --CML_HEAP_SIZE=512 --CML_STACK_SIZE=48 grid.cnf grid.lrat >cake.log
    rg -qx 'c VERIFIED' lrat.log
    rg -qx 's VERIFIED UNSAT' cake.log
    rm grid.lrat
    printf '%s %s %s dual recheck\n' "$ident" "$board" "$prefix"
  )
done
