#!/usr/bin/env bash
# List (and with --kill, stop) every process whose working directory is in this workspace's scratch/.
# These are the lanes' detached solver jobs. They outlive the hmz flow, so stop them after the run.
set -u
ROOT=$(cd "$(dirname "$0")/.." && pwd)
pids=()
for d in /proc/[0-9]*; do
  [ "$(stat -c %u "$d" 2>/dev/null)" = "$(id -u)" ] || continue
  cwd=$(readlink "$d/cwd" 2>/dev/null) || continue
  case "$cwd" in "$ROOT"/scratch/*) pids+=("${d#/proc/}");; esac
done
[ ${#pids[@]} -eq 0 ] && { echo "no jobs in $ROOT/scratch"; exit 0; }
for p in "${pids[@]}"; do printf '%s  %s\n' "$p" "$(tr '\0' ' ' < /proc/$p/cmdline | cut -c1-140)"; done
if [ "${1:-}" = "--kill" ]; then
  kill -TERM "${pids[@]}" 2>/dev/null; echo "sent SIGTERM to ${#pids[@]} processes"
else
  echo "(${#pids[@]} processes; run with --kill to stop them)"
fi
