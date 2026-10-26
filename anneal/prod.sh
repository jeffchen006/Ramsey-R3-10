#!/bin/bash
# n = 40 production: one worker per CPU; each worker loops runs of RUNTIME s with new seeds.
# usage: prod.sh CPU MODE   (MODE picks start/settings, see case below)
cd ./anneal
CPU=$1; MODE=$2; RUNTIME=${RUNTIME:-7200}
BIN=${BIN:-./ls_prod}
OUT=../runs/anneal/prod; mkdir -p $OUT
BASE="-n 40 -k 10 -maxdeg 9 -degcap 0 -w9 0 -focus 0.3 -T0 2 -T1 0.2 -vr 0.002 -time $RUNTIME"
r=0
while true; do
  seed=$((CPU * 100000 + r))
  case $MODE in
    rand9)  A="$BASE" ;;
    rand8)  A="$BASE -maxdeg 8" ;;
    vr005)  A="$BASE -vr 0.005" ;;
    f07)    A="$BASE -focus 0.7" ;;
    exoo)   A="$BASE -init file:../data/graphs/exoo/exoo39.g6" ;;
    a39)    A="$BASE -init file:../runs/anneal/g39/anneal39.g6" ;;
    k39)    A="$BASE -init file:../runs/anneal/g39/known39_seeds.g6" ;;
    grow)   A="$BASE -grow 38 -leveltime 3600" ;;
    alg)    A="$BASE -T0 1 -T1 0.2 -init file:../runs/anneal/seeds/alg40.g6" ;;
    inv)    f=$((2 * ((2 * r + CPU % 2) % 8))); A="$BASE -sym 2 -symf $f -sweep 300000" ;;  # Z2 with f fixed points (symsat open class; f = 0..14 over the two CPUs)
    k40)    A="$BASE -T0 1 -T1 0.2 -init file:../known39/out/nearmiss40_partial.g6" ;;
    b3)     A="$BASE -dlo 8" ;;
    b3s)    A="$BASE -dlo 8 -pswap 0.8" ;;
    b37)    A="$BASE -dlo 7" ;;
    gen39s) A="-n 39 -k 10 -maxdeg 9 -degcap 0 -w9 0 -focus 0.3 -saw 10000 -T0 0.3 -T1 0.3 -vr 0.002 -bench -time $RUNTIME" ;;
    gen39)  A="-n 39 -k 10 -maxdeg 9 -degcap 0 -w9 0 -focus 0.3 -T0 2 -T1 0.2 -vr 0.0015 -bench -time $RUNTIME" ;;
    *) echo "bad mode"; exit 2 ;;
  esac
  tag=${MODE}_c${CPU}_r$r
  [ "$MODE" = inv ] && tag=${tag}_f$f
  echo "$(date '+%F %T') start $tag seed=$seed" >> $OUT/worker_c$CPU.txt
  taskset -c $CPU nice -n 5 $BIN $A -seed $seed -out $OUT/$tag > /dev/null 2>&1
  rc=$?
  echo "$(date '+%F %T') end $tag rc=$rc $(grep END $OUT/$tag.log | cut -d' ' -f3-)" >> $OUT/worker_c$CPU.txt
  if [ $rc -eq 0 ]; then echo "$(date '+%F %T') FOUND in $tag" >> $OUT/worker_c$CPU.txt; fi
  r=$((r + 1))
done
