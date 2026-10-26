#!/bin/bash
# For cert: UNSAT "no (3,k,m)-graph with <= e(3,k,m)-1 edges" ([GR] Table 3 values), deg <= k-1, no MTF.
# SMS lazy IS + proof log. usage: emin_series.sh CPU TIMEOUT k:m:e ...
cd ./sms
CPU=$1; TO=$2; shift 2
for t in "$@"; do
  IFS=: read k m e <<< "$t"
  TAG=emin_${k}_${m}_${e}
  ./run1.sh $TAG $CPU $TO "-n $m -k $k --dmax $((k-1)) --emax $((e-1))" "--forbid-independent-set $k --proof-log proofs/$TAG.plog --sym-break-clauses proofs/$TAG.sym.json"
  ls -la proofs/$TAG.plog >> ../runs/sms/$TAG.log
done
