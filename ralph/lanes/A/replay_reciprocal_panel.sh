#!/bin/bash
set -euo pipefail
root=$(realpath "$(dirname "$0")/../../..")
lane="$root/ralph/lanes/A"
scout="$root/scratch/ideas/r012_R"
work="$root/scratch/A/panel13"
mkdir -p "$work"
cd "$work"
export LC_ALL=C TMPDIR="$PWD" PYTHONDONTWRITEBYTECODE=1
ulimit -v 16777216
ulimit -c 0
measured() {
    local tag=$1
    shift
    nice -n 5 timeout 110 prlimit --cpu=75:80 /usr/bin/time -f '%U %S %e %M' -o "$tag.time" "$@"
}
measured build g++ -std=c++17 -O3 -Wall -Wextra -Werror "$lane/audit_reciprocal_panel.cpp" -o audit
measured controls ./audit controls "$root/gluing/val" > small.atlas 2> controls.log
cmp small.atlas "$scout/direct-small.txt"
measured slice ./audit slice "$root/gluing/val" "$scout/frames17-5-2.txt" target.atlas > slice.depths 2> slice.log
cmp target.atlas "$scout/direct21.txt"
cmp target.atlas "$scout/liftrows.txt"

ln -sfn "$scout/frames17-5-2.txt" frames17-5-2.txt
ln -sfn "$scout/liftrows.txt" liftrows.txt
python3 -B - "$scout/stitch.cpp" > ref-depth.cpp <<'PY'
import pathlib
import sys

data = pathlib.Path(sys.argv[1]).read_text()

def replace(old, new):
    global data
    assert data.count(old) == 1, old
    data = data.replace(old, new)

replace('int main(int argc', 'struct Receipt { unsigned first, second, flip; int depth = 1; '
        "~Receipt() { cout<<first<<' '<<second<<' '<<flip<<' '<<depth<<'\\n'; } };\nint main(int argc")
replace("if(headers)cout<<first<<' '<<second<<' '<<flip<<'\\n';", 'Receipt receipt{first,second,flip};')
for stage in range(1, 5):
    replace(f'good[{stage}]++;', f'good[{stage}]++; receipt.depth++;')
replace("if(!headers)cout<<first<<' '<<second<<' '<<flip<<'\\n';", '')
sys.stdout.write(data)
PY
measured ref-build g++ -std=c++17 -O3 ref-depth.cpp -o ref-depth
measured ref ./ref-depth slice 0 > ref.depths 2> ref.log
diff -u ref.depths slice.depths > id-disagreements.diff
test "$(wc -l < slice.depths)" -eq 498668
awk '$4==5 {exit 1}' slice.depths

measured held ./audit slice "$root/gluing/val" "$scout/frames17-5-2.txt" held.atlas "$scout/held.txt" > held.depths 2> held.log
cmp target.atlas held.atlas
test "$(wc -l < held.depths)" -eq 100
awk '$4!=5 {exit 1}' held.depths
cut -d ' ' -f 1-3 held.depths | cmp - "$scout/held.txt"

sha256sum "$lane/audit_reciprocal_panel.cpp" "$lane/replay_reciprocal_panel.sh" \
    "$root/gluing/val/"{r3_4_8,r3_5_10,r3_6_17,r3_7_22}.g6 \
    "$scout/"{direct-small.txt,direct21.txt,liftrows.txt,frames17-5-2.txt,stitch.cpp,held.txt} \
    small.atlas target.atlas controls.log slice.depths slice.log ref.depths ref.log id-disagreements.diff held.depths held.log \
    > round13.sha256
cat controls.log slice.log ref.log held.log
printf 'CPU/wall/RSS: user-s system-s elapsed-s max-KiB\n'
for tag in build controls slice ref-build ref held; do printf '%-11s %s\n' "$tag" "$(cat "$tag.time")"; done
