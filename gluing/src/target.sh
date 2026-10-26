#!/bin/bash
# target.sh K N DMINLO VALDIR [glue args] : all (3,K+1;N)-graphs (v = min degree vertex) from R(3,K;N-d-1)
K=$1; N=$2; LO=$3; VAL=$4; shift 4; B=$(dirname $0)/../bin
for d in $(seq $LO $K); do m=$((N-d-1)); f=$VAL/r3_${K}_${m}.g6; [ -s $f ] && $B/glue -k $K -d $d "$@" < $f; done
