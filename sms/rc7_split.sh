#!/bin/bash
# After rc7_after (agent sms): split every TIMEOUT cube of Rc7b_cert into sub-cubes (lookahead at cutoff C),
# write $OUT (parent lits + new lits; a parent with no sub-cubes is kept whole). The cover CNF is made later
# by rc7_mkcover.py. Env: T (parents), W (work dir), OUT (sub-cubes), C (cutoff), P (parallel jobs).
# Memory: ulimit -v 3 GB per smsg (38 in parallel <= 114 GB < sms cap 128 GB).
cd ./sms
C=${C:-360}
OUT=${OUT:-cubes/Rc7b_sub.cubes}
T=${T:-cubes/Rc7b_timeouts.cubes}
W=${W:-../runs/sms/Rc7b_split}; mkdir -p $W
[ -s $T ] || { echo "no timeouts"; exit 0; }
grep -E '^(a )?-?[0-9]' $T | sed 's/^a //; s/ 0$//' > $W/parents.txt
N=$(wc -l < $W/parents.txt); echo "$(date) splitting $N parents at C=$C"
cube1() {  # i lits
  i=$1; shift; P=$W/p$i
  { head -1 cnf/Rc7b.cnf | awk -v k=$# '{print $1,$2,$3,$4+k}'; tail -n +2 cnf/Rc7b.cnf; for l in "$@"; do echo "$l 0"; done; } > $P.cnf
  ( ulimit -v 3145728; timeout 3h nice -n 5 sms-src/build/src/smsg -v 40 --dimacs $P.cnf --forbid-independent-set 10 \
      --initial-partition 1 7 2 1 2 27 --prerun 20 --assignment-cutoff $C --cutoff-edge-vars-only --lookahead-only-edge-vars --cube-only-decisions ) > $P.log 2>&1
  echo "rc=$?" >> $P.log; rm -f $P.cnf
}
export -f cube1; export W C
nl -ba $W/parents.txt | xargs -P ${P:-38} -L 1 bash -c 'cube1 "$@"' _
python3 - $W $OUT <<'PY'
import sys, os, re
W = sys.argv[1]
par = [l.split() for l in open(f"{W}/parents.txt")]
norm = lambda ls: " ".join(ls)
tos = {norm(p) for p in par}
sub, kept, bad = [], 0, []
for i, p in enumerate(par, 1):
    txt = open(f"{W}/p{i}.log").read()
    if "[(" in txt or re.search(r"^s SAT", txt, re.M): bad.append(f"GRAPH in p{i}")
    rc = re.findall(r"^rc=(\d+)", txt, re.M)[-1]
    cs = [l.split()[1:] for l in txt.splitlines() if l.startswith("Decisions:")]
    if rc != "0" or not cs:
        sub.append(p); kept += 1   # keep the parent whole (cubing failed, timed out or refuted it)
    else:
        sub += [p + [x for x in c if x not in p] for c in cs]
with open(sys.argv[2], "w") as f:
    for c in sub: f.write("a " + " ".join(c) + " 0\n")
print(f"parents {len(par)}, kept whole {kept}, sub-cubes {len(sub)}, {bad or 'no graphs'}")
if bad: open(f"{W}/FOUND_graph_in_cubing.txt", "w").write("\n".join(bad))
PY
