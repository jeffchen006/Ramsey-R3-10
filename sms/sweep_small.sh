#!/bin/bash
# small-case sweep on CPU 60 (sequential); results appended to runs/sms/sweep_small.txt
cd ./sms
OUT=../runs/sms/sweep_small.txt
for n in 10 11 12 13 14; do ./bench.sh $n 5 lazy 60 >> $OUT; ./bench.sh $n 5 eager 60 >> $OUT; done
for n in 13 14 15 16 17 18; do ./bench.sh $n 6 lazy 60 >> $OUT; ./bench.sh $n 6 eager 60 >> $OUT; done
for n in 22 23; do ./bench.sh $n 7 lazy 60 >> $OUT; ./bench.sh $n 7 eager 60 >> $OUT; done
./bench.sh 21 7 lazy 60 >> $OUT
echo DONE >> $OUT
