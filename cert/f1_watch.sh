#!/bin/bash
# cert/f1_watch.sh - certify sms F1 runs as soon as sms has converted them.
# F1: no (3,8,m)-graph with <= E edges, (m,E) = (23,46) (24,52) (25,58) (26,64) (27,70).
# Result lines go to runs/cert/f1/sms_certs.txt. Runs on CPUs 68-69 (nice), exits when all done.
R=.; OUT=$R/runs/cert/f1/sms_certs.txt
todo="23:46 24:52 25:58 26:64 27:70"
for i in $(seq 1 800); do
  left=""
  for x in $todo; do
    m=${x%:*}; E=${x#*:}; tag=f1_8_${m}_le${E}
    if grep -q converted $R/runs/sms/$tag.log 2>/dev/null; then
      res=$(taskset -c 68-69 nice -n 5 $R/cert/venv/bin/python $R/cert/sms_card_cert.py $m 8 0 7 0 $E \
        $R/sms/proofs/$tag.cnf $R/sms/proofs/$tag.lrat $R/sms/proofs/$tag.sym.json $R/cert/demo/sms_$tag --sb lean \
        > $R/runs/cert/f1/cert_$tag.log 2>&1; tail -1 $R/runs/cert/f1/cert_$tag.log)
      echo "$(date +%F_%T) $tag: $res" >> $OUT
    else
      left="$left $x"
    fi
  done
  todo=$left
  [ -z "$todo" ] && break
  sleep 120
done
echo "$(date +%F_%T) watcher done; remaining: $todo" >> $OUT
