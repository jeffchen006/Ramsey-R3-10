#!/bin/bash
# Run all kernel catalogue jobs of cases/out/kern_nr/plan.sh, 4 at a time (cases CPUs 144-147).
cd .
ulimit -v 4000000
xargs -P 4 -I{} sh -c '{}' < cases/out/kern_nr/plan.sh
python3 cases/kern_nr_plan.py counts > cases/out/kern_nr/summary.txt
echo DONE
