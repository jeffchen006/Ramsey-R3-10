#!/bin/bash
# After the M4/aut0 sample run ends, run the corrected (3,9,35) 8-regular kernel classification (M<=4, aut, -a), 6 h wall on 136-139.
cd ./duo
while pgrep -f "kern2/s40_M4_a0 " >/dev/null; do sleep 60; done
ulimit -v 4000000
timeout 6h taskset -c 136-139 nice -n 5 ../tools/venv/bin/python kernel_run2.py 35 8 9 4 ../runs/duo/kern/k35_M4.g6 ../runs/duo/kern2/c35_a1 3600 4 1
echo "c35 end rc=$? $(date -Is)"
