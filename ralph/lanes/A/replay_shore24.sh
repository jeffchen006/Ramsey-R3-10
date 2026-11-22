#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
run=${1:-r24-replay}
[[ $run =~ ^r24-[a-zA-Z0-9_-]+$ ]]
cd "$root"
sha256sum -c ralph/lanes/A/TRANSPORT23_V1.sha256
sha256sum -c ralph/lanes/A/BLOCKERS23_V2.sha256
sha256sum -c ralph/lanes/A/SHORE24.sha256
mkdir "scratch/A/$run"
cd "scratch/A/$run"
ln -s ../r24/inputs inputs
ulimit -v 524288
export PYTHONDONTWRITEBYTECODE=1
tool="$root/ralph/lanes/A/shore_blocker24.py"
/usr/bin/time -o controls.time -f '%U %S %M %e %x' nice -n 5 timeout 60s prlimit --cpu=40 -- \
    python3 "$tool" controls > controls.json
/usr/bin/time -o targets.time -f '%U %S %M %e %x' nice -n 5 timeout 60s prlimit --cpu=50 -- \
    python3 "$tool" target d175_1 d185_1 d246_1 d252_1 d275_1 d281_1 > targets.json
cmp controls.json ../r24/controls.json
cmp targets.json ../r24/targets.json
echo 'Both one-shore receipts replay byte for byte.'
