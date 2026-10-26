#!/bin/bash
# For each completed small component (runs/known39/comp_*, bfs_ann1), run k39 r2 (two-vertex
# rewires) once; append new graphs (not in any small component) to known39/out/r2_seeds.g6,
# which seed_driver3.sh picks up. State: runs/known39/r2_driver/done.txt
R=.
K39=$R/known39/bin/k39
ST=$R/runs/known39/r2_driver
mkdir -p $ST; touch $ST/done.txt
# components already processed by hand (20:10): comp_000..comp_003, comp_005
while true; do
  for d in $R/runs/known39/bfs_ann1 $R/runs/known39/comp_*; do
    grep -q -x "$d" $ST/done.txt && continue
    tail -1 $d/bfs.log 2>/dev/null | grep -q "closure complete" || { [ "$d" = $R/runs/known39/bfs_ann1 ] || continue; }
    cat $R/runs/known39/bfs_ann1/all.g6 $R/runs/known39/comp_*/all.g6 > $ST/known.g6
    rm -f $ST/out.txt
    echo "$(date +%T) r2 on $d ($(wc -l < $d/all.g6) graphs)"
    OMP_NUM_THREADS=2 taskset -c 188-189 nice -n 10 $K39 r2 $d/all.g6 $ST/known.g6 $ST/out.txt 2> $ST/last.err
    grep -h "FOUND40" $ST/out.txt $ST/last.err && echo "!!! FOUND40 via r2 from $d"
    grep -v '^#' $ST/out.txt | awk '{print $NF}' >> $R/known39/out/r2_seeds.g6
    cp $ST/out.txt $d/r2_out.txt
    echo "$(date +%T) r2 done $d: $(grep -vc '^#' $ST/out.txt) new graphs"
    echo "$d" >> $ST/done.txt
  done
  sleep 300
done
