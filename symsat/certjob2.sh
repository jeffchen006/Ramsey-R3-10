#!/bin/bash
# certjob.sh p f n K TL : satcore run in certificate mode, then independent check; one line to runs/symsat/certs.log
p=$1; f=$2; n=$3; K=$4; TL=$5; shift 5; EXTRA="$*"
PY=./tools/venv/bin/python
cd ./symsat
P=certs/n$n/p${p}_f${f}
A=$(echo "$EXTRA" | grep -o -- "--amax [0-9]*" | awk '{print $2}')
[ -n "$A" ] && P=${P}_a$A
r=$($PY cyclic.py $p $f --n $n --K $K --engine satcore --cert $P --tl $TL --work ../runs/symsat/work $EXTRA 2>/dev/null)
res=$(echo "$r" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['result'], d['time_s'])")
if [[ $res == UNSAT* ]]; then
  v=$(python3 verify_sc.py check $P.spec.json $P.map $P $n $K $p $f 2>&1 | tail -3 | tr '\n' ' ')
  if [[ $v == *"RESULT: VERIFIED"* ]]; then st=VERIFIED; xz -T1 -f $P.drat; else st=FAILED; fi
else st=NONE; v=""; fi
echo "$p $f $st amax=${A:-none} n=$n K=$K extra=[$EXTRA] search=[$res] check=[$v]" >> ../runs/symsat/certs.log
