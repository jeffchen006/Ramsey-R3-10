#!/bin/bash
# usage: verify_proof.sh CPU TAG N K [partition...]  -> appends a line to runs/sms/proof_checks.txt
# Checks: lrat-check on (input+external clauses, LRAT) ; check_ext.py on external clauses.
cd ./sms
CPU=$1; TAG=$2; N=$3; K=$4; shift 4
PART=""; [ $# -gt 0 ] && PART="--partition $*"
CONV=$(python3 lratlog2lrat.py cnf/$TAG.cnf proofs/$TAG.plog proofs/$TAG)
T0=$(date +%s.%N)
LR=$(taskset -c $CPU nice -n 5 ../tools/bin/lrat-check proofs/$TAG.cnf proofs/$TAG.lrat 2>&1 | grep -E "^c (NOT )?VERIFIED$" | head -1)
T1=$(date +%s.%N)
EX=$(taskset -c $CPU python3 check_ext.py --n $N --k $K proofs/$TAG.ext proofs/$TAG.sym.json $PART | head -1)
SZ=$(stat -c %s proofs/$TAG.lrat)
echo "$TAG | $CONV | lrat-check: ${LR:-NO RESULT} ($(echo "$T1-$T0" | bc) s, lrat $SZ B) | $EX" >> ../runs/sms/proof_checks.txt
