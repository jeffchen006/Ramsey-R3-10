#!/bin/bash
set -euo pipefail
lane=$(cd "$(dirname "$0")"&&pwd);root=$(cd "$lane/../../.."&&pwd);py="$root/opt/venv/bin/python"
test "$PWD" = "$root/scratch/F/r23";export TMPDIR=$PWD PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
ulimit -v 1048576;ulimit -f 16384;previous=$1;stage=$2
while ps -p "$previous" -o args= | grep -Fq 'six_queue.py worker all'; do sleep 5; done
printf '%s %s available after %s\n' "$(date -Is)" "$stage" "$previous"
run(){ /usr/bin/time -f '%e %U %S %M %x' -o "$1.time" nice -n 5 timeout "$2" prlimit --cpu="$3" -- "${@:4}" >"$1.stdout" 2>"$1.err"; }
case "$stage" in
 proof) cd receipts;tag=trial33854418671;run "${tag}_create" 240 205 "$py" -B "$lane/six_prefix_cert.py" "$tag" create
   run "${tag}_verify" 120 100 "$py" -B "$lane/six_prefix_cert.py" "$tag" verify
   while read -r key rest;do test -s "$key.relation" && continue;run "$key" 205 180 "$py" -B "$lane/six_receipt.py" "$key" masks pairs bind;done <"../$tag.rows";;
 score) mkdir -p near;cd near;run build 90 75 g++ -std=c++17 -O3 -march=native "$lane/six_near.cpp" -o near
   run score 300 260 "$py" -B "$lane/six_near.py";;
 five) mkdir -p five;cd five;run build 90 75 g++ -std=c++17 -O3 -march=native "$lane/six_five.cpp" -o five
   run control 240 205 "$py" -B "$lane/six_five.py" control
   run fixed 240 205 "$py" -B "$lane/six_five.py" fixed.keys fixed
   run price 240 205 "$py" -B "$lane/six_five.py" price.keys price;;
 eight) mkdir -p eight;cd eight;run build 90 75 g++ -std=c++17 -O3 -march=native "$lane/six_eight.cpp" -o eight
   run control 240 205 "$py" -B "$lane/six_eight.py" control
   run price 240 205 "$py" -B "$lane/six_eight.py" pilot;;
 *) exit 2;;
esac
printf '%s %s done\n' "$(date -Is)" "$stage"
