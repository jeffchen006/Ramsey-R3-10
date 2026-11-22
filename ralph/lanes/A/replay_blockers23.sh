#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../.." && pwd)
run=${1:-r23-replay}
[[ $run =~ ^r23-[a-zA-Z0-9_-]+$ ]]
cd "$root"
sha256sum -c ralph/lanes/A/TRANSPORT23_V1.sha256
sha256sum -c ralph/lanes/A/BLOCKERS23_V2.sha256
mkdir "scratch/A/$run"
cd "scratch/A/$run"
ulimit -v 524288
for kind in transport physical; do
    if [[ $kind == transport ]]; then
        tool=transport23.py
        version=v1
    else
        tool=physical_blocker23.py
        version=v2
    fi
    /usr/bin/time -o "$kind.time" -f '%U %S %M %e %x' nice -n 5 timeout 30s prlimit --cpu=20 -- \
        python3 "$root/ralph/lanes/A/$tool" > "$kind.$version.json"
    cmp "$kind.$version.json" "../r23/$kind.$version.json"
done
echo 'Two versioned fixtures reproduce byte for byte.'
