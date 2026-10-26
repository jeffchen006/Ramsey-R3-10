#!/bin/bash
# usage: bench.sh N K MODE(lazy|eager) CPU [extra smsg args...]
# Enumerates all (3,K,N)-graphs with SMS (cutoff 0 => exact up to isomorphism).
set -u
N=$1; K=$2; MODE=$3; CPU=$4; shift 4
D=.
SMSG=$D/sms/sms-src/build/src/smsg
TAG=r3_${K}_${N}_${MODE}
CNF=$D/sms/cnf/$TAG.cnf
LOG=$D/runs/sms/$TAG.log
if [ $MODE = eager ]; then python3 $D/sms/gen_ramsey.py -n $N -k $K --eager-is -o $CNF; OPT="";
else python3 $D/sms/gen_ramsey.py -n $N -k $K -o $CNF; OPT="--forbid-independent-set $K"; fi
/usr/bin/time -f "WALL %e s MAXRSS %M KB" taskset -c $CPU nice -n 5 $SMSG -v $N --all-graphs --cutoff 0 --dimacs $CNF $OPT "$@" > $LOG 2>&1
python3 $D/sms/edges2g6.py $N < $LOG > $D/runs/sms/$TAG.g6
CNT=$(wc -l < $D/runs/sms/$TAG.g6)
$D/tools/bin/shortg -q $D/runs/sms/$TAG.g6 $D/runs/sms/$TAG.short.g6 2>/dev/null; UNIQ=$(wc -l < $D/runs/sms/$TAG.short.g6)
CHK=$(python3 $D/tools/check_graph.py --k $K $D/runs/sms/$TAG.g6 > /dev/null 2>&1 && echo ok || echo FAIL)
[ "$CNT" = 0 ] && CHK=none
echo "$TAG count=$CNT uniq=$UNIQ check=$CHK $(grep -E '^Total time' $LOG) $(grep WALL $LOG)"
