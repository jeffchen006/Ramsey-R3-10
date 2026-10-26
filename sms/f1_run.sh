#!/bin/bash
# F1 for cert: no (3,8,m)-graph with <= E edges; deg <= 7; proof log. usage: f1_run.sh CPU m E
cd ./sms
CPU=$1; m=$2; E=$3; TAG=f1_8_${m}_le${E}
./run1.sh $TAG $CPU 86400 "-n $m -k 8 --dmax 7 --emax $E" "--forbid-independent-set 8 --proof-log proofs/$TAG.plog --sym-break-clauses proofs/$TAG.sym.json"
taskset -c $CPU nice -n 5 ./lratlog2lrat cnf/$TAG.cnf proofs/$TAG.plog proofs/$TAG >> ../runs/sms/$TAG.log 2>&1
echo "converted $(date -Is)" >> ../runs/sms/$TAG.log
