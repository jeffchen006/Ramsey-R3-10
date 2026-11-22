#!/usr/bin/env bash
set -euo pipefail
ulimit -v 16777216
ulimit -t 1050
ulimit -f 16384
export LC_ALL=C PYTHONDONTWRITEBYTECODE=1
directory=work/e108_r24_high
tools=../../opt/bin
slot=${1:?slot}
[[ $slot == 0 || $slot == 1 || $slot == control ]]

run() {
    local degree=$1 input=$2 stem=$3 cap=$4 program=$5
    /usr/bin/time -o "$directory/$stem.time" -f 'cpu=%U+%S wall=%e rss=%M' \
        timeout --kill-after=3s 18m "build/$program" -k6 -d"$degree" -e"$cap" \
        <"$directory/$input" >"$directory/$stem.raw" 2>"$directory/$stem.log"
    local count
    count=$(wc -l <"$directory/$input")
    grep -Fq "in=$count " "$directory/$stem.log"
    ! grep -Fq 'bad graph6' "$directory/$stem.log"
    timeout --kill-after=3s 90s "$tools/shortg" -q -T"$directory" "$directory/$stem.raw" "$directory/$stem.g6"
    printf '%s inputs=%s raw=%s canon=%s %s\n' "$stem" "$count" \
        "$(wc -l <"$directory/$stem.raw")" "$(wc -l <"$directory/$stem.g6")" "$(cat "$directory/$stem.time")"
}

if [[ $slot == control ]]; then
    for degree in 2 3 4; do
        timeout 20s "$tools/pickg" -q -e0:$((45-degree*degree)) "val/r3_6_$((19-degree)).g6" "$directory/d$degree.control.in"
        run "$degree" "d$degree.control.in" "d$degree.control" 45 glue5
    done
    cat "$directory"/d?.control.g6 | timeout 20s "$tools/shortg" -q -T"$directory" > "$directory/le45.control.g6"
    for item in '44 15' '45 479'; do
        read -r level count <<< "$item"
        test "$(timeout 20s "$tools/pickg" -q -e"$level" "$directory/le45.control.g6" | wc -l)" -eq "$count"
    done
    test "$(wc -l <"$directory/le45.control.g6")" -eq 494
    echo 'complete e44/e45 controls 15/479'
    exit 0
fi
if [[ $slot == 0 ]]; then
    run 2 d2.e49.in d2.source 49 high_r24_source
    run 3 d3.e49.in d3.source 49 high_r24_source
fi
run 4 "d4.e49.$slot.in" "d4.source.$slot" 49 high_r24_source
touch "$directory/slot$slot.complete"
