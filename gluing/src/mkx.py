"""Write satcore --extra clauses for the |X| = 27 hybrid case.
Vertices: u = 0, w = 1, Y = 2..12 (= N(u) | N(w)), X = 13..39 fixed to the given (3,8;27)-graph.
usage: python3 mkx.py X.g6line OUT.cnf
"""
import sys

def var(i, j):
    if i > j: i, j = j, i
    return j * (j - 1) // 2 + i + 1

def g6dec(s):
    n = ord(s[0]) - 63; bits = []
    for ch in s[1:]:
        x = ord(ch) - 63; bits += [(x >> (5 - t)) & 1 for t in range(6)]
    E = set(); k = 0
    for j in range(1, n):
        for i in range(j):
            if bits[k]: E.add((i, j))
            k += 1
    return n, E

s, out = sys.argv[1], sys.argv[2]
nX, E = g6dec(s)
assert nX == 27
X0 = 13
cl = [[-var(0, 1)]]
for x in range(nX):
    cl.append([-var(0, X0 + x)]); cl.append([-var(1, X0 + x)])
for j in range(1, nX):
    for i in range(j):
        v = var(X0 + i, X0 + j)
        cl.append([v] if (i, j) in E else [-v])
for y in range(2, 13):
    cl.append([var(0, y), var(1, y)])
with open(out, 'w') as f:
    f.write(f'p cnf {var(38, 39)} {len(cl)}\n')
    for c in cl:
        f.write(' '.join(map(str, c)) + ' 0\n')
