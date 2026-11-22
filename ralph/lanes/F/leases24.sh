#!/bin/bash
set -euo pipefail
lane=$(cd "$(dirname "$0")" && pwd);root=$(cd "$lane/../../.." && pwd);store=$root/scratch/F/r24;py=$root/opt/venv/bin/python;prior=$1;slot=$2
export TMPDIR=$PWD PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
while [[ -e /proc/$prior ]];do sleep 2;done
echo "$(date -Is) lease released prior=$prior slot=$slot"
case $slot in
  1) (cd "$store/shape/attain"; "$py" -B -c "import sys;sys.path.insert(0,'$lane');from pattern_repair24 import work,get;from source24 import cycle;record=work('attain37',get(955182831),10,True,[(500,cycle(5))],1000000);print(record);assert record['states']['model']==1" >witness.stdout); (cd "$store/transfer/balance"; "$py" -B "$lane/transfer24.py" target 0 4 balance >balance.jsonl; "$py" -B "$lane/transfer24.py" target 4 15 all >full.jsonl);;
  2) :;;
  3) while [[ -e /proc/546263 ]];do sleep 2;done; (cd "$store/shape/repair/work1"; "$py" -B "$lane/pattern_repair24.py" plan last >plan.stdout; cp ../last.tsv manifest.tsv; "$py" -B "$lane/pattern_repair24.py" wave manifest.tsv 1000000 >worker.jsonl);;
esac
cd "$store/global/work$slot"; echo "$(date -Is) taking fresh global work$slot";exec "$py" -B "$lane/global24.py" prod manifest.tsv >worker.log
