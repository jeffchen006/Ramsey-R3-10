#!/bin/bash
# par.sh CPUS INFILE OUTFILE LOGPREFIX glue-args...
# Split INFILE round-robin over the CPUs in list CPUS (e.g. 156-167 or 160,161), run glue on each
# part pinned to one CPU, dedupe each part with shortg, then merge + dedupe into OUTFILE.
CPUS=$1; IN=$2; OUT=$3; LOG=$4; shift 4
B=$(cd $(dirname $0)/..; pwd)/bin; SG=$(cd $(dirname $0)/../..; pwd)/tools/bin/shortg
list=$(python3 -c "
s='$CPUS'; out=[]
for p in s.split(','):
    if '-' in p: a,b=map(int,p.split('-')); out+=range(a,b+1)
    else: out.append(int(p))
print(' '.join(map(str,out)))")
n=$(echo $list | wc -w)
tmp=$(mktemp -d ${OUT}.parts.XXXX)
i=0
for c in $list; do
  awk -v n=$n -v i=$i 'NR % n == i' $IN > $tmp/in.$i
  ( taskset -c $c nice -n 5 $B/glue "$@" < $tmp/in.$i 2> $LOG.$i.err | taskset -c $c $SG -q > $tmp/out.$i 2>/dev/null ) &
  i=$((i+1))
done
wait
cat $tmp/out.* | $SG -q > $OUT 2>/dev/null
cat $LOG.*.err > $LOG.err
rm -rf $tmp
echo "par.sh done: $(wc -l < $OUT) graphs in $OUT"
