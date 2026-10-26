#!/bin/bash
# F10 certificates, part 2 (f8,f10,f12 certs done by ext27_cert.sh; f14 class idx 394409 done).
# f14: 5 remaining classes in parallel (idx mod 16 distinct: 394410->10, 394411->11, 394415->15, 394416->0, 394417->1).
# f16 (2 classes) was missing from ext27_cert.sh; added here. Then verify ALL certs.
cd ./symsat
PY=../tools/venv/bin/python; G=../data/graphs/mckay/r38_27.g6.gz; L=../runs/symsat
for i in 10 11 15 0 1; do $PY ext27.py $G 14 --cert certs/ext27 --start $i --step 16 > $L/ext27c2_f14_$i.log 2>&1 & done
$PY ext27.py $G 16 --cert certs/ext27 > $L/ext27c2_f16.log 2>&1 &
$PY ext27.py $G 24 --cert certs/ext27 > $L/ext27c2_f24.log 2>&1 &
wait
ls certs/ext27/*.json | xargs -P 12 -n 20 $PY ext27_verify.py > $L/ext27_verify.log 2>&1
echo "certs $(ls certs/ext27/*.json | wc -l) verified $(grep -c ' VERIFIED ' $L/ext27_verify.log) fail $(grep -c FAIL $L/ext27_verify.log)"
