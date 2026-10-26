"""critic: decode an r7 CNF model to the 40-vertex graph (g6) for checking."""
import sys
sys.path.insert(0, './critic/src')
from gen_tests import g6
x6, sol = sys.argv[1], sys.argv[2]
s = open(x6).read().strip(); n = ord(s[0]) - 63
bits = [((ord(c) - 63) >> (5 - i)) & 1 for c in s[1:] for i in range(6)]
E = []; k = 0
for j in range(1, n):
    for i in range(j):
        if bits[k]: E.append((i, j))
        k += 1
U, V, C, A, B = 27, 28, list(range(29, 36)), [36, 37], [38, 39]
S = C + A + B
E += [(U, c) for c in C + A] + [(V, c) for c in C + B] + [(a, b) for a in A for b in B]
true = {int(t) for l in open(sol) if l.startswith('v') for t in l.split()[1:] if int(t) > 0}
E += [(s_, y) for si, s_ in enumerate(S) for y in range(27) if si * 27 + y + 1 in true]
deg = [0] * 40
for a, b in E: deg[a] += 1; deg[b] += 1
print(g6(40, E)); print('degrees', sorted(set(deg)), file=sys.stderr)
