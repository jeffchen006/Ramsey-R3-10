#!/bin/bash
# collect algebra's n=40 symmetric seeds (runs/algebra/L_n40_*.best) with K <= KMAX and no triangles
# into runs/anneal/seeds/alg40.g6 (K computed by ls itself)
cd .
KMAX=${1:-24}
out=runs/anneal/seeds/alg40.g6; tmp=$out.tmp; : > $tmp
for f in runs/algebra/L_n40_*.best; do
  g=$(head -1 $f); [ -z "$g" ] && continue
  echo "$g" > runs/anneal/seeds/one.g6
  r=$(anneal/ls -n 40 -k 10 -w9 0 -addvr 0 -init file:runs/anneal/seeds/one.g6 -time 0 | grep '^start')
  K=$(echo $r | sed 's/.*K=\([0-9]*\) K1.*/\1/'); T=$(echo $r | sed 's/.* T=\([0-9]*\) .*/\1/')
  [ "$T" = "0" ] && [ "$K" -le $KMAX ] && echo "$g" >> $tmp && echo "$K $f"
done
sort -u $tmp > $out; rm -f $tmp runs/anneal/seeds/one.g6
wc -l $out
