#!/bin/bash
# After Rc7b_cert: summary, timeouts list, mail to sms + lead (no LLM needed).
cd .
D=runs/sms/Rc7b_cert
tools/bin/cuberun summary $D > $D/SUMMARY.txt 2>&1
tools/bin/cuberun summary $D --timeouts sms/cubes/Rc7b_timeouts.cubes >> $D/SUMMARY.txt 2>&1
NT=$(grep -c . sms/cubes/Rc7b_timeouts.cubes 2>/dev/null || echo 0)
S=$(head -4 $D/SUMMARY.txt | tr '\n' ' ')
A=$(ls $D/ALERT* $D/FOUND* 2>/dev/null | tr '\n' ' ')
tools/bin/mbox send sms "Rc7b_cert ended: $S timeouts=$NT alerts/found: ${A:-none}. Next: re-cube timeouts (sms/cubes/Rc7b_timeouts.cubes) at C=360." --from rc7_after
tools/bin/mbox send lead "sms R(7) run ended: $S timeouts=$NT alerts/found: ${A:-none}. If timeouts > 0, sms re-cubes them next (not yet proven)." --from sms_rc7_after
