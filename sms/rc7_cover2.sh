#!/bin/bash
# Certified cover for the split R(7) cube set (agent sms): Rc7b + negated final cubes is UNSAT, VERIFIED.
cd ./sms
P=../runs/sms/Rc7b_cover2; mkdir -p $P
sort -u ../runs/sms/Rc7b_splitA/parents.txt ../runs/sms/Rc7b_splitB/parents.txt > ../runs/sms/Rc7b_parents_all.txt 2>/dev/null
python3 rc7_mkcover.py ../runs/sms/Rc7b_parents_all.txt cubes/Rc7b_subA.cubes cubes/Rc7b_subB.cubes || exit 2
( ulimit -v 16777216; /usr/bin/time -f "WALL %e s MAXRSS %M KB" sms-src/build/src/smsg -v 40 --dimacs cnf/Rc7b_cover2.cnf --forbid-independent-set 10 \
  --initial-partition 1 7 2 1 2 27 --proof-log $P/cover.plog --sym-break-clauses $P/cover.plog.sym.json ) > $P/smsg.log 2>&1
grep -E "^Result|WALL" $P/smsg.log
R=$(EXTRAS=cnf/Rc7b_cover2.cnf ./rc7_check.sh cnf/Rc7b_cover2.cnf $P/cover.plog "" | tail -1)
echo "$R" | tee $P/VERDICT.txt
[ "$R" = "s VERIFIED cube" ] && rm -f $P/cover.plog* $P/*.lrat 2>/dev/null
[ "$R" = "s VERIFIED cube" ]
