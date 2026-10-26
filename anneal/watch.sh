#!/bin/bash
# every 60 s: check every graph in runs/anneal/**/*.found.g6.
# n = 40 and check_graph --k 10 passes -> copy to graphs/found/ and write runs/anneal/ALERT_FOUND40.
# n = 39 and passes -> append to runs/anneal/g39/anneal39.g6 (dedup by string).
cd .
SEEN=runs/anneal/watch_seen.txt; touch $SEEN
while true; do
  for f in $(find runs/anneal -name '*.found.g6' 2>/dev/null); do
    while read -r g; do
      [ -z "$g" ] && continue
      grep -qxF "$g" $SEEN && continue
      echo "$g" >> $SEEN
      tmp=$(mktemp -p runs/anneal); echo "$g" > $tmp
      c=${g:0:1}
      if [ "$c" = "g" ]; then  # n = 40
        if python3 tools/check_graph.py --k 10 --n 40 $tmp > $tmp.out 2>&1; then
          name=graphs/found/anneal_$(date +%Y%m%d_%H%M%S).g6
          cp $tmp $name
          echo "$(date '+%F %T') $name from $f: $(cat $tmp.out | head -1)" >> runs/anneal/ALERT_FOUND40
        else
          echo "$(date '+%F %T') n40 candidate FAILED check from $f" >> runs/anneal/watch.log
        fi
      elif [ "$c" = "f" ]; then  # n = 39
        if python3 tools/check_graph.py --k 10 --n 39 $tmp > /dev/null 2>&1; then
          grep -qxF "$g" runs/anneal/g39/anneal39.g6 || echo "$g" >> runs/anneal/g39/anneal39.g6
        fi
      fi
      rm -f $tmp $tmp.out
    done < "$f"
  done
  # new n=40 best below 5 independent 10-sets -> ALERT file (once; a jobctl event)
  if [ ! -e runs/anneal/ALERT_LOWK ]; then
    low=$(grep -l '^# ls n=40' runs/anneal/prod/*.log 2>/dev/null | xargs grep -HoE 'best K=[0-4] ' 2>/dev/null | head -1)
    [ -n "$low" ] && echo "$(date '+%F %T') $low" > runs/anneal/ALERT_LOWK
  fi
  sleep 60
done
