#!/bin/bash
# After rc7_after (agent sms): split the R(7) TIMEOUT cubes not already split in rc7_splitA.
cd ./sms
grep -vxF -f cubes/Rc7b_timeoutsA.cubes cubes/Rc7b_timeouts.cubes > cubes/Rc7b_timeoutsB.cubes
mkdir -p ../runs/sms/Rc7b_splitB; : > ../runs/sms/Rc7b_splitB/parents.txt; : > cubes/Rc7b_subB.cubes
echo "timeouts total $(grep -c . cubes/Rc7b_timeouts.cubes), new for B $(grep -c . cubes/Rc7b_timeoutsB.cubes)"
T=cubes/Rc7b_timeoutsB.cubes W=../runs/sms/Rc7b_splitB OUT=cubes/Rc7b_subB.cubes P=38 ./rc7_split.sh
