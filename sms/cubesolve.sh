#!/bin/bash
# Solve each cube in its own smsg process. usage: cubesolve.sh CPU N CNF CUBEFILE OUT TIMEOUT "smsg args" [first last]
cd ./sms
CPU=$1; N=$2; CNF=$3; CF=$4; OUT=$5; TO=$6; SM=$7
NC=$(wc -l < $CF); FIRST=${8:-1}; LAST=${9:-$NC}
for i in $(seq $FIRST $LAST); do
  s=$(date +%s.%N)
  r=$(timeout $TO taskset -c $CPU nice -n 5 sms-src/build/src/smsg -v $N --dimacs $CNF $SM --cube-file $CF --cube-line $i 2>&1 | grep -E "^Result|Time for cube|Timeout reached" | tr '\n' ' ')
  e=$(date +%s.%N)
  echo "$i $(echo "$e - $s" | bc) $r" >> $OUT
done
echo DONE >> $OUT
