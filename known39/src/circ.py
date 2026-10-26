"""All triangle-free circulants C_n(D) with max degree <= 9, as graph6 (one per D; not up to iso).
Usage: circ.py n"""
import sys
sys.path.insert(0, './tools')
from check_graph import to_graph6
n = int(sys.argv[1])
def sym(D): return {d % n for d in D} | {(-d) % n for d in D}
def tri_free(S):
    return not any((a + b) % n in S for a in S for b in S)
out = []
def rec(start, D):
    S = sym(D)
    if D:
        out.append(list(D))
    for d in range(start, n // 2 + 1):
        S2 = sym(D + [d])
        if len(S2) <= 9 and tri_free(S2): rec(d + 1, D + [d])
rec(1, [])
for D in out:
    S = sym(D)
    if len(S) < 6: continue
    adj = [sum(1 << ((i + s) % n) for s in S) for i in range(n)]
    print(to_graph6(adj), ' '.join(map(str, D)), file=sys.stdout)
