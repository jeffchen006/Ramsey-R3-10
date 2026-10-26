#!/bin/bash
# Watch seed files for new (3,10,39)-graphs. For each new graph not already in a known
# rewire component, compute its closure (k39 bfs, cap 5M) in runs/known39/comp_NNN.
# Usage: seed_driver.sh SEEDFILE...   (runs forever; state in runs/known39/seed_driver/)
R=.
K39=$R/known39/bin/k39
ST=$R/runs/known39/seed_driver
mkdir -p $ST
touch $ST/seen_canon.txt
while true; do
  for f in "$@"; do
    [ -f "$f" ] || continue
    key=$(echo "$f" | md5sum | cut -c1-8)
    done_n=$(cat $ST/lines_$key 2>/dev/null || echo 0)
    tot=$(wc -l < "$f")
    while [ "$done_n" -lt "$tot" ]; do
      done_n=$((done_n + 1))
      sed -n "${done_n}p" "$f" | awk '{print $NF}' > $ST/cur.g6
      if ! python3 $R/tools/check_graph.py --k 10 --n 39 $ST/cur.g6 > /dev/null 2>&1; then
        echo "$(date +%T) $f:$done_n not a (3,10,39)-graph, skipped"; echo $done_n > $ST/lines_$key; continue; fi
      c=$($K39 canon $ST/cur.g6)
      hit=""
      if grep -q -F -x "$c" $ST/seen_canon.txt; then hit="seed seen"; fi
      if [ -z "$hit" ]; then
        for a in $R/runs/known39/bfs_exoo/all.g6 $R/runs/known39/bfs_ann1/all.g6 $R/runs/known39/comp_*/all.g6; do
          [ -f "$a" ] && grep -q -F -x "$c" "$a" && { hit="$a"; break; }
        done
      fi
      echo "$c" >> $ST/seen_canon.txt
      if [ -n "$hit" ]; then echo "$(date +%T) $f:$done_n in $hit"; echo $done_n > $ST/lines_$key; continue; fi
      k=$(ls -d $R/runs/known39/comp_* 2>/dev/null | wc -l); d=$(printf "$R/runs/known39/comp_%03d" $k)
      mkdir -p $d; echo "$c" > $d/seed.g6; echo "$f:$done_n" > $d/source.txt
      echo "$(date +%T) $f:$done_n NEW component -> $d"
      OMP_NUM_THREADS=2 taskset -c 190-191 nice -n 10 $K39 bfs $d/seed.g6 $d 5000000 20 > $d/bfs.log 2>&1
      tail -1 $d/bfs.log
      [ -s $d/FOUND40.g6 ] && echo "!!! FOUND40 in $d"
      echo $done_n > $ST/lines_$key
    done
  done
  sleep 120
done
