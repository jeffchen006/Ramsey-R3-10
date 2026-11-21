#!/usr/bin/env bash
set -euo pipefail
lane_dir=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$lane_dir/../../.." && pwd)
tag=$1 wall=$2 cpu=$3; shift 3
printf -v command '%q ' "$@"
cd "$root/scratch/F/r1"
exec 9>"$root/scratch/F/.launch.lock"
flock 9
cap=$(awk -F '|' '$2 ~ /^[[:space:]]*F[[:space:]]*$/ { print int($3); exit }' "$root/ralph/ALLOC.md")
active=0
for pid in $(pgrep -x timeout || true); do
    case $(readlink "/proc/$pid/cwd" || true) in
        "$root/scratch/F"|"$root/scratch/F/"*) active=$((active+1));;
    esac
done
if [[ -z $cap ]] || ((active >= cap)); then
    printf 'Refusing %s: %s active F supervisors for cap %s\n' "$tag" "$active" "$cap" >&2
    exit 2
fi
test ! -e "$tag.stdout"
start=$(date -Is)
end=$(date -Is -d "+$wall seconds")
setsid nohup nice -n 5 timeout -k 10s "${wall}s" bash -c '
    ulimit -v 16777216
    tag=$1 cpu=$2; shift 2
    exec /usr/bin/time -f "cpu_user=%U cpu_sys=%S elapsed=%e maxrss_kb=%M exit=%x" -o "$tag.time" prlimit --cpu="$cpu:$((cpu+2))" -- "$@"
' bash "$tag" "$cpu" "$@" 9>&- > "$tag.stdout" 2>&1 &
supervisor=$!
sleep 0.12
timer=$(ps -o pid= --ppid "$supervisor" | xargs || true)
worker=-
if [[ -n $timer ]]; then worker=$(ps -o pid= --ppid "$timer" | xargs || true); fi
printf '| %s / %s | `%s` (wall %ss, CPU %ss) | `scratch/F/r1/%s.{stdout,time}` | 1 | %s | %s |\n' \
    "$supervisor" "${worker:--}" "$command" "$wall" "$cpu" "$tag" "$start" "$end" >> "$lane_dir/STATE.md"
printf '%s supervisor=%s worker=%s\n' "$tag" "$supervisor" "${worker:--}"
