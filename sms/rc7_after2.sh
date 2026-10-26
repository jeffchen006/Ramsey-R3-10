#!/bin/bash
# After Rc7b_subA, Rc7b_subB, Rc7b_cover2 (agent sms): summaries + timeouts of the sub-cube runs, mail to sms.
cd .
M=""
for X in A B; do
  D=runs/sms/Rc7b_sub$X; [ -d $D ] || { M="$M | sub$X: no run"; continue; }
  tools/bin/cuberun summary $D > $D/SUMMARY.txt 2>&1
  tools/bin/cuberun summary $D --timeouts sms/cubes/Rc7b_sub${X}_timeouts.cubes >> $D/SUMMARY.txt 2>&1
  NT=$(grep -c . sms/cubes/Rc7b_sub${X}_timeouts.cubes 2>/dev/null || echo 0)
  M="$M | sub$X: $(head -1 $D/SUMMARY.txt) timeouts=$NT alerts/found: $(ls $D/ALERT* $D/FOUND* 2>/dev/null | tr '\n' ' ')"
done
tools/bin/mbox send sms "R(7) sub-cube runs ended$M | cover2: $(cat runs/sms/Rc7b_cover2/VERDICT.txt 2>/dev/null)" --from rc7_after2
