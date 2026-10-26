#!/bin/bash
# UNSAT scaling: (3,k,R(3,k)) for k=5..8 in 4 encodings. CPU $1, variant set $2 (a|b)
cd ./sms
CPU=$1; SET=$2
declare -A R=( [4]=9 [5]=14 [6]=18 [7]=23 [8]=28 [9]=36 )
for k in 5 6 7 8; do
  n=${R[$k]}; dmin=$(( n - ${R[$((k-1))]} )); dmax=$((k-1))
  if [ $SET = a ]; then
    ./run1.sh u3_${k}_${n}_plain $CPU 14400 "-n $n -k $k" "--forbid-independent-set $k"
    ./run1.sh u3_${k}_${n}_deg $CPU 14400 "-n $n -k $k --dmin $dmin --dmax $dmax" "--forbid-independent-set $k"
  else
    ./run1.sh u3_${k}_${n}_mtf $CPU 14400 "-n $n -k $k --mtf" "--forbid-independent-set $k"
    ./run1.sh u3_${k}_${n}_degmtf $CPU 14400 "-n $n -k $k --mtf --dmin $dmin --dmax $dmax" "--forbid-independent-set $k"
  fi
done
