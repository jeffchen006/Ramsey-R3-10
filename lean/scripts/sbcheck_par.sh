#!/bin/bash
# Parallel sbcheck: sbcheck_par.sh FILE CPULIST   (the caller's own CPUs, e.g. 68-71)
# FILE must have exactly one "c order ..." header line, before all clauses.
# Worker i streams the file and checks every n-th clause (comment/header lines go to all
# workers; line numbers in FAIL messages are per worker); runs the verified checker on each, and prints "s VERIFIED <total> clauses" only if every chunk verifies.
set -u
f=$1; cpus=$2
bin=$(dirname $0)/../.lake/build/bin/sbcheck
list=$(python3 -c "
import sys
out=[]
for part in '$cpus'.split(','):
    a,_,b=part.partition('-'); out+=list(range(int(a),int(b or a)+1))
print(' '.join(map(str,out)))")
n=$(echo $list | wc -w)
[ "$(grep -c '^c order' $f)" = "1" ] || { echo "s FAILED: need exactly one header"; exit 1; }
hdr=$(grep -m1 '^c order' $f)
first=$(grep -n -m1 -v '^c' $f | cut -d: -f1); hline=$(grep -n -m1 '^c order' $f | cut -d: -f1)
[ "$hline" -lt "$first" ] || { echo "s FAILED: header after a clause"; exit 1; }
tmp=$(mktemp -d)
i=0
for c in $list; do
  ( awk -v i=$i -v n=$n '/^c/ {print; next} {k++; if (k % n == i) print}' "$f" | \
      taskset -c $c nice -n 5 $bin - > $tmp/w$i.out 2>&1 ) &
  i=$((i+1))
done
wait
tot=0; ok=1
for o in $tmp/w*.out; do
  grep FAIL $o | head -5
  k=$(grep -o 's VERIFIED [0-9]*' $o | awk '{print $3}')
  if [ -n "$k" ]; then tot=$((tot+k)); elif grep -q 's FAILED' $o; then ok=0; elif [ -s $o ]; then ok=0; fi
done
rm -r $tmp
if [ $ok = 1 ] && [ $tot -gt 0 ]; then echo "s VERIFIED $tot clauses"; else echo "s FAILED"; exit 1; fi
