#!/bin/bash
# F1 split by max degree D (cert): vertex 0 has max degree D, N(0)={1..D}, all deg <= D, edges <= E.
# usage: f1_split.sh CPU m E TIMEOUT D...
cd ./sms
CPU=$1; m=$2; E=$3; TO=$4; shift 4
for D in "$@"; do
  TAG=f1_8_${m}_le${E}_D${D}
  if [ $D -eq 0 ]; then PART="1 $((m-1))"; else PART="1 $D $((m-1-D))"; fi
  ./run1.sh $TAG $CPU $TO "-n $m -k 8 --dmax $D --emax $E --fix-nbhd $D" "--forbid-independent-set 8 --initial-partition $PART --proof-log proofs/$TAG.plog --sym-break-clauses proofs/$TAG.sym.json"
  taskset -c $CPU nice -n 5 ./lratlog2lrat cnf/$TAG.cnf proofs/$TAG.plog proofs/$TAG >> ../runs/sms/$TAG.log 2>&1
  echo "converted $(date -Is)" >> ../runs/sms/$TAG.log
  grep -q "status=20" ../runs/sms/$TAG.log && echo "$TAG sms/cnf/$TAG.cnf sms/proofs/$TAG.cnf sms/proofs/$TAG.lrat sms/proofs/$TAG.sym.json partition: $PART" >> ../runs/sms/f1_split_done.txt
done
