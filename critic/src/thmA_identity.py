"""critic: check sum_v e(H_v) = sum_v d(v)(n/2 - d(v)) (cases L4 / Theorem A identity) on 40-vertex
triangle-free graphs (greedy random + critic/deg4/k11.g6)."""
import random, sys
sys.path.insert(0, './critic/src')
from gen_tests import greedy_tf
def check(n, E):
    N = [set() for _ in range(n)]
    for a, b in E: N[a].add(b); N[b].add(a)
    e = len(E); lhs = 0
    for v in range(n):
        out = N[v] | {v}
        lhs += sum(1 for a, b in E if a not in out and b not in out)
    rhs = sum(len(N[v]) * (n - 2 * len(N[v])) for v in range(n))  # = 2 * sum d(n/2 - d)
    return 2 * lhs == rhs
rnd = random.Random(5); ok = all(check(40, greedy_tf(rnd, 40)) for _ in range(200))
s = open('./critic/deg4/k11.g6').read().strip()
d = [ord(c) - 63 for c in s[1:]]; bits = [(x >> (5 - i)) & 1 for x in d for i in range(6)]
E = []; k = 0
for j in range(1, 40):
    for i in range(j):
        if bits[k]: E.append((i, j))
        k += 1
print('identity holds on 200 random + k11:', ok and check(40, E))
