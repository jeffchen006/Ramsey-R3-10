#!/bin/bash
# Like cubesolve.sh but for a list of cube line numbers. usage: CPU N CNF CUBEFILE OUT TIMEOUT "smsg args" LISTFILE
cd ./sms
CPU=$1; N=$2; CNF=$3; CF=$4; OUT=$5; TO=$6; SM=$7; LIST=$8
for i in $(cat $LIST); do
  s=$(date +%s.%N)
  r=$(timeout $TO taskset -c $CPU nice -n 5 sms-src/build/src/smsg -v $N --dimacs $CNF $SM --cube-file $CF --cube-line $i 2>&1 | grep -E "^Result|Time for cube|Timeout reached|^\[\(" | cut -c1-60 | tr '\n' ' ')
  e=$(date +%s.%N)
  echo "$i $(echo "$e - $s" | bc) $r" >> $OUT
done
echo DONE >> $OUT
