# satcore --extra units: vertex 0 = v, N(v) = 1..d, H = d+1..n-1 fixed to the given graph6 graph
import sys
def var(i, j):
    if i > j: i, j = j, i
    return j * (j - 1) // 2 + i + 1
s, d, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
n = ord(s[0]) - 63; bits = []
for ch in s[1:]:
    x = ord(ch) - 63; bits += [(x >> (5 - t)) & 1 for t in range(6)]
cl = []; k = 0
for j in range(1, n):
    for i in range(j):
        v = var(d + 1 + i, d + 1 + j); cl.append(v if bits[k] else -v); k += 1
open(out, 'w').write(f'p cnf {var(n+d, n+d+1)} {len(cl)}\n' + ''.join(f'{c} 0\n' for c in cl))
