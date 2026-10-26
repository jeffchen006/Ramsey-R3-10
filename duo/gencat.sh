#!/bin/bash
# usage: gencat.sh PART  (PART in 0..3, mod 4). Kernel catalogues for case R (n=40,d=9): M=4,5,6 -> -D3/4/5, e 7:16/18/20, nu>=7.
cd ./duo; O=../runs/duo/kern2/cat; p=$1
for spec in "4 3 16" "5 4 18" "6 5 20"; do set -- $spec
  /usr/bin/time -f "M$1 part $p WALL %e s" ../tools/bin/genbg -q -D$2 8 8 7:$3 $p/4 | ./kfilt 8 7 > $O/M$1_p$p.txt
done
echo done part $p
