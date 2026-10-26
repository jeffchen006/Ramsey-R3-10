#!/bin/bash
# (k-1)-regular (3,k,n) with MTF and fixed N(0): analogue of the 9-regular n=40 case.
# usage: reg_series.sh CPU TIMEOUT k:n ...
cd ./sms
CPU=$1; TO=$2; shift 2
for kn in "$@"; do
  k=${kn%%:*}; n=${kn##*:}; d=$((k-1))
  ./run1.sh reg_${k}_${n}_fix $CPU $TO "-n $n -k $k --dmin $d --dmax $d --mtf --fix-nbhd $d" "--forbid-independent-set $k --initial-partition 1 $d $((n-1-d))"
done
