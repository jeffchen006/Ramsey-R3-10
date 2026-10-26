#!/bin/sh
# Kill otabu jobs for classes closed exactly by symsat (Z5 f5/f10, Z7 f5, Z13 f1) while the lift queue runs.
while kill -0 218535 2>/dev/null; do
  for pid in $(pgrep -x otabu); do
    if tr '\0' ' ' < /proc/$pid/cmdline 2>/dev/null | grep -Eq 'n40_(Z5_f5|Z5_f10|Z7_f5|Z13_f1)\.txt'; then kill $pid; echo "skipped $pid $(date)"; fi
  done
  sleep 20
done
