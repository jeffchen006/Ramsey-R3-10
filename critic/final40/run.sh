#!/bin/bash
# Review 31: validity of all final40 inputs + independent sample re-glue (myglue.py)
cd .
python3 tools/check_graph.py --k 9 --n 31 gluing/cls/S8_in96.g6 | tail -2
python3 tools/check_graph.py --k 9 --n 30 gluing/cls/N_in87.g6 | tail -2
python3 critic/glue/myglue.py critic/final40/e96_sample.g6 8 > runs/critic/f40_e96.log 2>&1 &
python3 critic/glue/myglue.py critic/final40/e87_sample.g6 9 > runs/critic/f40_e87.log 2>&1
wait
echo "e96: $(grep -c UNSAT runs/critic/f40_e96.log) UNSAT, $(grep -vc UNSAT runs/critic/f40_e96.log) other"
echo "e87: $(grep -c UNSAT runs/critic/f40_e87.log) UNSAT, $(grep -vc UNSAT runs/critic/f40_e87.log) other"
