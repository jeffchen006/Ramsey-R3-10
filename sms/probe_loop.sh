#!/bin/bash
# Run Knuth probes forever with seeds S0, S0+100, ... usage: probe_loop.sh CPU S0 BASE OUT C0 STEP T "smsg args"
# Memory: each smsg runs under ulimit -v $PROBE_MEM_KB (default 4 GB, knuth_probe.py). Stops on a FAILED event.
cd ./sms
CPU=$1; S=$2; BASE=$3; OUT=$4; C0=$5; ST=$6; T=$7; SA=$8
while true; do
  python3 knuth_probe.py $CPU $S $BASE 40 $OUT $C0 $ST $T "$SA"; rm -rf $OUT.work; S=$((S+100))
  tail -1 $OUT | grep -q FAILED && { echo "stop: $(tail -1 $OUT)"; exit 3; }
done
