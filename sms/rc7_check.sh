#!/bin/bash
# Certified check of one R(7) cube (agent sms): cert/cube_check.sh (LRAT + Lean sbcheck with coarse
# blocks d=9 + check_cnf) AND every SYM witness keeps the finer blocks {0},{1..7},{8,9},{10},{11,12},{13..39}.
# usage: rc7_check.sh CUBECNF PLOG UNITS ; prints "s VERIFIED cube" only if both pass.
R=.
[ -f "$2.sym.json" ] && cp "$2.sym.json" "${2%.plog}.sym.json"
C=$($R/cert/cube_check.sh "$1" "$2" 40 10 9 ${EXTRAS:-$R/sms/cnf/Rc7b.cnf} "$3" | tail -1)
P=$(python3 - "${2%.plog}.sym.json" <<'PY'
import json, sys
blocks = [0] + [1]*7 + [2]*2 + [3] + [4]*2 + [5]*27
bad = sum(1 for _, perm in json.load(open(sys.argv[1]))["sym_clauses"]
          if any(blocks[perm[v]] != blocks[v] for v in range(40)))
print("PARTITION OK" if bad == 0 else "PARTITION BAD %d" % bad)
PY
)
# Lean sbcheck with the finer blocks, on the witness file cube_check.sh wrote
W="${2%.plog}.cert.sb.wit"; L="LEAN-BLOCKS SKIP"
if [ -f "$W" ]; then
  K=$(grep -vc '^c' "$W")
  sed '1s/.*/c order positions=rowmajor better=min vars=rowmajor d=0 n=40 s=10 blocks=1:7,2,1,2,27/' "$W" > "$W.blocks"
  if [ "$K" -eq 0 ] || grep -qx "s VERIFIED $K clauses" <($R/lean/.lake/build/bin/sbcheck "$W.blocks"); then L="LEAN-BLOCKS OK"; else L="LEAN-BLOCKS BAD"; fi
fi
if [ "$C" = "s VERIFIED cube" ] && [ "$P" = "PARTITION OK" ] && [ "$L" = "LEAN-BLOCKS OK" ]; then echo "s VERIFIED cube"; else echo "s FAILED [$C] [$P] [$L]"; fi
