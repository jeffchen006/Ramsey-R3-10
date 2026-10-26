#!/bin/bash
# Usage: memcap.sh MAX_GB cmd args...   Kill the command tree when its total RSS exceeds MAX_GB.
max_kb=$(( $1 * 1024 * 1024 )); shift
"$@" &
pid=$!
while kill -0 $pid 2>/dev/null; do
  tot=0
  for p in $pid $(pgrep -P $pid) $(for c in $(pgrep -P $pid); do pgrep -P $c; done); do
    r=$(awk '/VmRSS/{print $2}' /proc/$p/status 2>/dev/null); tot=$(( tot + ${r:-0} ))
  done
  if [ $tot -gt $max_kb ]; then
    echo "memcap: RSS ${tot} KB > ${max_kb} KB, killing" >&2
    pkill -TERM -P $pid; kill -TERM $pid; sleep 1; pkill -KILL -P $pid; kill -KILL $pid 2>/dev/null
    wait $pid; exit 137
  fi
  sleep 1
done
wait $pid
