#!/bin/bash
# F10 certificates: re-run ext27 in cert mode for all f, then check every cert independently.
cd ./symsat
PY=../tools/venv/bin/python; G=../data/graphs/mckay/r38_27.g6.gz; L=../runs/symsat
for i in 0 1 2; do $PY ext27.py $G 8 --cert certs/ext27 --start $i --step 3 > $L/ext27c_f8_$i.log 2>&1 & done
(for f in 10 12 14 24; do $PY ext27.py $G $f --cert certs/ext27; done) > $L/ext27c_rest.log 2>&1 &
wait
ls certs/ext27/*.json | xargs -P 4 -n 20 $PY ext27_verify.py > $L/ext27_verify.log 2>&1
echo "certs $(ls certs/ext27/*.json | wc -l) verified $(grep -c ' VERIFIED ' $L/ext27_verify.log) fail $(grep -c FAIL $L/ext27_verify.log)"
