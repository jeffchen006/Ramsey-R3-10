#!/bin/bash
# cert/f1_split_watch.sh - certify sms F1 split runs f1_8_<m>_le<E>_D<D> when converted.
# Results: runs/cert/f1/split_certs.txt (one line per tag). Runs up to ~30 h, CPUs 68-69.
R=.; OUT=$R/runs/cert/f1/split_certs.txt; touch $OUT
for i in $(seq 1 900); do
  for log in $R/runs/sms/f1_8_*_le*_D*.log; do
    [ -e "$log" ] || continue
    tag=$(basename $log .log)
    grep -q " $tag:" $OUT && continue
    grep -q converted $log || continue
    m=$(echo $tag | sed 's/f1_8_\([0-9]*\)_le.*/\1/'); E=$(echo $tag | sed 's/.*_le\([0-9]*\)_D.*/\1/'); D=${tag##*_D}
    taskset -c 68-69 nice -n 5 $R/cert/venv/bin/python $R/cert/sms_card_cert.py $m 8 0 $D 0 $E \
      $R/sms/proofs/$tag.cnf $R/sms/proofs/$tag.lrat $R/sms/proofs/$tag.sym.json $R/cert/demo/sms_$tag \
      --fix-nbhd $D > $R/runs/cert/f1/cert_$tag.log 2>&1
    echo "$(date +%F_%T) $tag: $(tail -1 $R/runs/cert/f1/cert_$tag.log)" >> $OUT
  done
  sleep 120
done
