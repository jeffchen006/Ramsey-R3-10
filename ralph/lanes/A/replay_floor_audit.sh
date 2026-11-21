#!/usr/bin/env bash
set -euo pipefail
root=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
lane="$root/ralph/lanes/A"
source="$root/scratch/G/round3"
producer="$root/ralph/lanes/G"
certs="$producer/root_certs"
retained="$root/scratch/A/root-residue"
if (( $# != 1 )); then
    echo "usage: $0 fresh-directory-under-scratch/A" >&2
    exit 2
fi
work=$(realpath -m -- "$1")
if [[ $work != "$root"/scratch/A/* || -e $work ]]; then
    echo 'work directory must be fresh and below scratch/A' >&2
    exit 2
fi
mkdir -- "$work"
cd -- "$work"
ulimit -v 16777216
hard_cpu=$(ulimit -Ht)
if [[ $hard_cpu == unlimited || $hard_cpu -gt 300 ]]; then
    ulimit -t 300
fi
(cd "$root" && sha256sum --strict -c "$lane/FLOOR_AUDIT.sha256") > inputs.log
(cd "$certs" && sha256sum --strict -c floor120_inputs.sha256) > pin6.log
(cd "$source" && sha256sum --strict -c "$certs/floor7_inputs.sha256") > pin7.log
nice -n 5 timeout 90s python3 -S -B "$lane/audit_floor_covers.py" calibrate "$root/gluing/val/r3_7_22.g6"
nice -n 5 timeout 90s python3 -S -B "$lane/audit_floor_covers.py" root6 "$certs" "$retained/retained-v1" "$retained/complete-v2" > root6.tsv
nice -n 5 timeout 90s python3 -S -B "$lane/residue_bundle.py" replay "$retained/complete-v2" --bin "$root/opt/bin" > replay6.log
for level in 104 105 106; do
    nice -n 5 timeout 400s python3 -S -B "$lane/audit_floor_covers.py" root7 "$source" "$level" > "e$level.log"
done
nice -n 5 timeout 90s python3 -S -B "$lane/audit_floor_delta.py" > delta.csv
cmp delta.csv "$producer/round3_cases.csv"
{
    nice -n 5 timeout 120s python3 -S -B "$producer/scan.py" --verify --output "$producer/t9_round1_certs.jsonl"
    for name in root_floor_certs root_floor120_certs root_floor7_certs root_floor7_106_certs root_floor7_107_certs; do
        printf '%s: ' "$name"
        nice -n 5 timeout 120s python3 -S -B "$producer/scan_root_floor.py" --verify --output "$producer/$name.jsonl"
    done
} > farkas.log
tail -n 1 replay6.log
awk '/^PASS/ { print }' e104.log e105.log e106.log
tail -n 1 delta.csv
