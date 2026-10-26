#!/bin/bash
cd ./sms
P=../runs/sms/Rc7b_cover
mkdir -p $P
/usr/bin/time -f "WALL %e s MAXRSS %M KB" sms-src/build/src/smsg -v 40 --dimacs cnf/Rc7b_cover.cnf --forbid-independent-set 10 --initial-partition 1 7 2 1 2 27 --proof-log $P/cover.plog --sym-break-clauses $P/cover.plog.sym.json > $P/smsg.log 2>&1
grep -E "^Result|WALL" $P/smsg.log
# extras for check_cnf: the cover clauses are allowed (they are the cover statement itself)
./rc7_check.sh cnf/Rc7b_cover.cnf $P/cover.plog ""
