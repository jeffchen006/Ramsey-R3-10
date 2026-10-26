#!/bin/bash
# cert/cube_check.sh - one-command certificate check of one SMS cube, for tools' cuberun hook.
# Usage: cube_check.sh CNF PLOG N S D EXTRAS [UNITS]
#   CNF    the cube's input CNF (base + cube units) given to smsg
#   PLOG   smsg --proof-log file; PLOG%.plog.sym.json must be the --sym-break-clauses file
#   N S    vertices, forbidden independent-set size;  D = |N(0)| (0: no partition)
#   EXTRAS CNF of allowed non-TRI/IS clauses of the base (cube constraints + encodings,
#          checked separately against lean/out/cube_X.opb and by VeriPB proof 2)
#   UNITS  optional: the cube's unit clauses (cuberun {units}); allowed in CNF as well
# Prints exactly one final line: "s VERIFIED cube" only if ALL of
#   cake_lpr "s VERIFIED UNSAT", Lean sbcheck "s VERIFIED <k> clauses", check_cnf "RESULT: OK"
# pass; else "s FAILED <which>". Verdicts are read from stdout, never exit codes.
set -u
CNF=$1; PLOG=$2; N=$3; S=$4; D=$5; EXTRAS=$6; UNITS=${7:-}
UX=()
if [ -n "$UNITS" ]; then   # add a DIMACS header (cuberun's {units} file has none)
  { echo "p cnf 10000000 $(grep -c ' 0' "$UNITS")"; grep -v '^[cp]' "$UNITS"; } > "${PLOG%.plog}.cert.units.cnf"
  UX=(--extra "${PLOG%.plog}.cert.units.cnf")
fi
R=.
OUT=${PLOG%.plog}.cert; SYM=${PLOG%.plog}.sym.json
fail=""
$R/sms/lratlog2lrat "$CNF" "$PLOG" "$OUT" > "$OUT.conv.log" 2>&1
grep -qx "s VERIFIED UNSAT" <($R/tools/bin/cake_lpr --CML_HEAP_SIZE=10000 --CML_STACK_SIZE=2000 \
  "$OUT.cnf" "$OUT.lrat" | tee "$OUT.cake.log") || fail="$fail cake_lpr"
K=$(python3 -c "import json,sys; print(len(json.load(open(sys.argv[1]))['sym_clauses']))" "$SYM")
python3 - "$SYM" "$N" "$S" "$D" > "$OUT.sb.wit" <<'EOF'
import json, sys
sym, n, s, d = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
var = lambda i, j: i * n - i * (i + 1) // 2 + (j - i)
print("c order positions=rowmajor better=min vars=rowmajor d=%d n=%d s=%d" % (d, n, s))
for lits, perm in json.load(open(sym))["sym_clauses"]:
    pi = [0] * n
    for v, w in enumerate(perm):
        pi[w] = v
    print("%s 0 | %s" % (" ".join(str(sg * var(min(i, j), max(i, j))) for sg, i, j in lits), " ".join(map(str, pi))))
EOF
if [ "$K" -gt 0 ]; then
  grep -qx "s VERIFIED $K clauses" <($R/lean/.lake/build/bin/sbcheck "$OUT.sb.wit" | tee "$OUT.sb.log") || fail="$fail sbcheck"
fi
python3 - "$OUT.sb.wit" "$OUT.symcl.cnf" <<'EOF'
import sys
cls = [l.split("|")[0].split() for l in open(sys.argv[1]) if not l.startswith("c")]
with open(sys.argv[2], "w") as f:
    f.write("p cnf 1000000 %d\n" % len(cls))
    f.writelines(" ".join(c) + "\n" for c in cls)
EOF
grep -qx "RESULT: OK (every clause is valid or listed as extra)" <(python3 $R/cert/check_cnf.py --n "$N" --s "$S" \
  --order rowmajor --extra "$EXTRAS" "${UX[@]}" --extra "$OUT.symcl.cnf" "$OUT.cnf" | tee "$OUT.cnfcheck.log") || fail="$fail check_cnf"
if [ -z "$fail" ]; then echo "s VERIFIED cube"; else echo "s FAILED$fail"; fi
