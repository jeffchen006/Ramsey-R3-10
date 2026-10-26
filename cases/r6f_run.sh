#!/bin/bash
# Solve every batch CNF in DIR with smsg (no SMS, lazy independent 10-sets). usage: r6f_run.sh DIR CPU TIMEOUT
# Output: DIR/results.txt lines "cnf result(10=SAT,20=UNSAT,124=timeout) seconds"
DIR=$1; CPU=$2; TO=$3
S=./sms/sms-src/build/src/smsg
ulimit -v 16000000
for f in "$DIR"/b_*.cnf; do
  s=$(date +%s.%N)
  timeout $TO taskset -c $CPU $S -v 40 --dimacs "$f" --no-SMS --forbid-independent-set 10 > "${f%.cnf}.out" 2>&1
  r=$?
  e=$(date +%s.%N)
  echo "$(basename $f) $r $(echo "$e - $s" | bc)" >> "$DIR/results.txt"
done
echo DONE >> "$DIR/results.txt"
