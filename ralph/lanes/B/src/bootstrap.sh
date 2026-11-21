#!/usr/bin/env bash
set -euo pipefail
root=$(cd "$(dirname "$0")/../../../.." && pwd)
scratch=$root/scratch/B
cd "$scratch"
export PYTHONDONTWRITEBYTECODE=1
ulimit -v 16777216
export B_GLUE_BIN="$scratch/build" B_LABELG="$root/opt/bin/labelg"
shortg=$root/opt/bin/shortg
source_dir=$root/ralph/lanes/B/src
check=$root/tools/check_graph.py
op=$scratch/build/onepoint
export LC_ALL=C
mkdir -p val logs work
for target in glue glue2 glue5 onepoint; do
    gcc -O3 -march=native "${source_dir}/$target.c" -o "build/$target"
done
for spec in '30 86 1800' '31 95 560'; do
    read -r order edges count <<< "$spec"
    file="ref/Ramseygraphs_3_9_${order}_e${edges}.g6"
    python3 "$source_dir/ecount.py" "$file" "$edges:$count"
    "$shortg" -q "$file" "work/hog_${order}_$edges.canon"
    test "$(wc -l < "work/hog_${order}_$edges.canon")" -eq "$count"
    timeout 180 python3 "$check" --n "$order" --k 9 "$file" > "logs/hog_${order}_$edges.log"
done
for spec in 'Ramseygraphs_3_9_35_e140 8 8 140' 'exoo39 9 6 167'; do
    read -r name alpha minimum edges <<< "$spec"
    timeout 480 python3 "$source_dir/selftest.py" "ref/$name.g6" "$alpha" 1 -m "$minimum" -e "$edges" -E "$edges" | tee "logs/$name.selftest"
done
for order in {9..11} 16 17; do
    ln -sf "$root/gluing/val/r3_6_$order.g6" "val/r3_6_$order.g6"
done
for spec in '12 116792' '13 275086' '14 263520' '15 64732'; do
    read -r order historical_count <<< "$spec"
    path="val/r3_6_$order.g6"
    if [[ ! -s $path ]]; then
        timeout 600 "$op" -k 6 < "val/r3_6_$((order-1)).g6" | timeout 600 "$shortg" -q -Twork > "$path.tmp"
        mv "$path.tmp" "$path"
    fi
    echo "R(3,6;$order) = $(wc -l < "$path"), historical file implies $historical_count"
    test "$(wc -l < "$path")" -eq "$historical_count"
done

for degree in 3 4 5 6; do
    order=$((20-degree))
    path="work/r37_21_$degree.g6"
    if [[ ! -s $path ]]; then
        timeout 900 build/glue -k 6 -d "$degree" < "val/r3_6_$order.g6" | timeout 900 "$shortg" -q -Twork > "$path.tmp"
        mv "$path.tmp" "$path"
    fi
done
cat work/r37_21_?.g6 | timeout 900 "$shortg" -q -Twork > "val/r3_7_21.g6"
python3 "$source_dir/ecount.py" val/r3_7_21.g6 51:4,52:70,53:717,54:5167,55:27289,56:97249,57:219623,58:307464,59:267374,60:142741,61:43923,62:6484,63:331
