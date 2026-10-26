#!/bin/bash
# exits (= wakes anneal) only on: n=40 graph found, a worker loop died, or n=40 best K < 5
cd .
while true; do
  [ -s runs/anneal/ALERT_FOUND40 ] && { echo "EVENT found40"; cat runs/anneal/ALERT_FOUND40; exit 0; }
  n=$(pgrep -f "prod.sh [0-9]+ " | wc -l)
  [ "$n" -lt 16 ] && { echo "EVENT workers=$n"; exit 0; }
  pgrep -f watch.sh > /dev/null || { echo "EVENT watcher died"; exit 0; }
  low=$(grep -l '^# ls n=40' runs/anneal/prod/*.log 2>/dev/null | xargs grep -hoE 'best K=[0-4] ' 2>/dev/null | head -1)
  [ -n "$low" ] && { echo "EVENT low K: $low"; python3 anneal/summ.py | tail -1; exit 0; }
  sleep 120
done
