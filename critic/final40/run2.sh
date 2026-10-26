#!/bin/bash
# Review 31: positive controls, then independent sample re-glue (myglue.py, venv pysat)
cd .; P=critic/venv/bin/python
for d in 6 8 9; do cp critic/glue/ctl_$d.g6 critic/final40/ctl_$d.g6; $P critic/glue/myglue.py critic/final40/ctl_$d.g6 $d | sed "s/^/ctl d=$d: /"; done
$P critic/glue/myglue.py critic/final40/e96_sample.g6 8 > runs/critic/f40_e96.log 2>&1 &
$P critic/glue/myglue.py critic/final40/e87_sample.g6 9 > runs/critic/f40_e87.log 2>&1
wait
echo "e96: $(grep -c UNSAT runs/critic/f40_e96.log) UNSAT, $(grep -vc UNSAT runs/critic/f40_e96.log) other"
echo "e87: $(grep -c UNSAT runs/critic/f40_e87.log) UNSAT, $(grep -vc UNSAT runs/critic/f40_e87.log) other"
