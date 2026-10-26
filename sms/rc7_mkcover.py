#!/usr/bin/env python3
"""cnf/Rc7b_cover2.cnf = Rc7b + negations of (L300 cubes minus all TIMEOUT parents) + negations of all sub-cubes.
usage: rc7_mkcover.py PARENTS.txt SUB1.cubes [SUB2.cubes ...]   (agent sms; run in sms/)"""
import sys
norm = lambda ls: " ".join(ls)
par = {norm(l.split()) for l in open(sys.argv[1]) if l.strip()}
sub = [l.split()[1:-1] for f in sys.argv[2:] for l in open(f) if l.startswith("a ")]
old = [l.split()[1:-1] for l in open("cubes/Rc7b_L300.cubes") if l.startswith("a ")]
rest = [c for c in old if norm(c) not in par]
assert len(rest) == len(old) - len(par), (len(rest), len(old), len(par))
neg = [[str(-int(x)) for x in c] for c in rest + sub]
head, body = open("cnf/Rc7b.cnf").read().split("\n", 1)
h = head.split()
with open("cnf/Rc7b_cover2.cnf", "w") as f:
    f.write(f"p cnf {h[2]} {int(h[3]) + len(neg)}\n"); f.write(body)
    for c in neg: f.write(" ".join(c) + " 0\n")
print(f"cover2: {len(rest)} old cubes + {len(sub)} sub-cubes ({len(par)} parents)")
