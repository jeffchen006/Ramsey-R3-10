#!/bin/bash
# usage: run1.sh TAG CPU TIMEOUT_S "gen_ramsey args" "smsg args"
# Generates cnf/TAG.cnf, runs smsg, log in runs/sms/TAG.log, graph6 in runs/sms/TAG.g6
set -u
TAG=$1; CPU=$2; TO=$3; GEN=$4; SM=$5
D=.
N=$(echo " $GEN " | grep -oE " -n [0-9]+ " | grep -oE "[0-9]+")
python3 $D/sms/gen_ramsey.py $GEN -o $D/sms/cnf/$TAG.cnf
echo "CMD smsg -v $N --dimacs cnf/$TAG.cnf $SM ; gen: $GEN ; start $(date -Is)" > $D/runs/sms/$TAG.log
/usr/bin/time -f "WALL %e s MAXRSS %M KB" timeout $TO taskset -c $CPU nice -n 5 $D/sms/sms-src/build/src/smsg -v $N --dimacs $D/sms/cnf/$TAG.cnf $SM >> $D/runs/sms/$TAG.log 2>&1
echo "end $(date -Is)" >> $D/runs/sms/$TAG.log
python3 $D/sms/edges2g6.py $N < $D/runs/sms/$TAG.log > $D/runs/sms/$TAG.g6
