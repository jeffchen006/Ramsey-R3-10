#!/usr/bin/env bash
set -euo pipefail
lane_dir=$(cd "$(dirname "$0")" && pwd)
root=$(cd "$lane_dir/../../.." && pwd)
tag=$1 wall=$2 cpu=$3; shift 3
round=${F_ROUND:-r2}
[[ $round =~ ^r[0-9]+$ && $tag =~ ^[a-zA-Z0-9_]+$ ]]
printf -v command '%q ' "$@"
cd "$root/scratch/F/$round"
exec 9>"$root/scratch/F/.launch.lock"
flock 9
cap=$(awk -F '|' '$2 ~ /^[[:space:]]*F[[:space:]]*$/ { print int($3); exit }' "$root/ralph/ALLOC.md")
registry="$root/scratch/F/supervisors.tsv"
declare -A registered=()
boot=$(< /proc/sys/kernel/random/boot_id)
pidstat() {
    local raw
    IFS= read -r raw < "/proc/$1/stat" || return 1
    raw=${raw##*) }
    read -ra fields <<< "$raw"
    printf '%s %s\n' "${fields[0]}" "${fields[19]}"
}
active=0
touch "$registry"
while read -r pid stored_boot ticks job; do
    [[ $boot == "$stored_boot" ]] || continue
    identity=$(pidstat "$pid" 2>/dev/null || true)
    if [[ -z $identity ]]; then
        [[ -d /proc/$pid ]] || continue
    else
        read -r state live_ticks <<< "$identity"
        [[ $state != Z && $state != X && ( $ticks == '?' || $ticks == "$live_ticks" ) ]] || continue
    fi
    registered[$pid]=$job
done < "$registry"
active=${#registered[@]}
unknown=0
while read -r pid; do
    [[ ${registered[$pid]+present} ]] && continue
    identity=$(pidstat "$pid" 2>/dev/null || true)
    [[ -d /proc/$pid && $identity != [ZX]' '* ]] || continue
    active=$((active+1)); unknown=$((unknown+1))
done < <(pgrep -u "$EUID" -f '^timeout .* lane-F:r[0-9]+:[a-zA-Z0-9_]+ ' || true)
printf '%s %s active=%s unknown=%s cap=%s registered=%s\n' "$(date -Is)" "$round/$tag" "$active" "$unknown" "$cap" "${!registered[*]}" \
    >> "$root/scratch/F/concurrency.log"
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
' "lane-F:$round:$tag" "$tag" "$cpu" "$@" 9>&- > "$tag.stdout" 2>&1 &
supervisor=$!
identity=$(pidstat "$supervisor" 2>/dev/null || true)
ticks=${identity#* }
printf '%s\t%s\t%s\t%s\n' "$supervisor" "$boot" "${ticks:-?}" "$round/$tag" >> "$registry"
sleep 0.12
timer=$(ps -o pid= --ppid "$supervisor" | xargs || true)
worker=-
if [[ -n $timer ]]; then worker=$(ps -o pid= --ppid "$timer" | xargs || true); fi
printf '| %s / %s | `%s` (wall %ss, CPU %ss) | `scratch/F/%s/%s.{stdout,time}` | 1 | %s | %s |\n' \
    "$supervisor" "${worker:--}" "$command" "$wall" "$cpu" "$round" "$tag" "$start" "$end" >> "$lane_dir/STATE.md"
printf '%s supervisor=%s worker=%s\n' "$tag" "$supervisor" "${worker:--}"
