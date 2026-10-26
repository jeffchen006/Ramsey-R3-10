#!/usr/bin/env python3
"""Check that every clause in EXT is an independent-k-set clause (identity map).
usage: check_ext.py K EXT [SETS]  (SETS: vertex set per clause, must match)"""
import sys, itertools
k = int(sys.argv[1]); bad = 0; cnt = 0
def dec(v):
    j = 1
    while j*(j+1)//2 < v: j += 1
    return v - 1 - j*(j-1)//2, j
for line in open(sys.argv[2]):
    if line.startswith(('c', 'p')) or not line.strip(): continue
    lits = [int(x) for x in line.split()][:-1]; cnt += 1
    S = set()
    for l in lits:
        if l <= 0: bad += 1; break
        S |= set(dec(l))
    want = sorted(a*0 + (j*(j-1)//2 + a + 1) for a, j in itertools.combinations(sorted(S), 2))
    if len(S) != k or sorted(lits) != want: bad += 1
if len(sys.argv) > 3:
    cl = [sorted(int(x) for x in l.split()[:-1]) for l in open(sys.argv[2]) if l.strip() and not l.startswith(('c', 'p'))]
    st = [sorted(int(x) for x in l.split()) for l in open(sys.argv[3])]
    ev = lambda i, j: j*(j-1)//2 + i + 1
    mism = sum(1 for c, S in zip(cl, st) if c != sorted(ev(a, b) for a, b in itertools.combinations(S, 2)))
    print("sets=%d clauses=%d set mismatches=%d" % (len(st), len(cl), mism)); bad += mism + (len(st) != len(cl))
print("ext clauses=%d bad=%d" % (cnt, bad)); sys.exit(1 if bad else 0)
