"""critic: ALL triangle-free circulants C_n(D) with |D| <= 9 (D symmetric), graph6 + D on stderr."""
import sys, itertools
sys.path.insert(0, './critic/src')
from gen_tests import g6, circ
n = int(sys.argv[1]); half = list(range(1, n // 2 + 1)); c = 0
for k in range(1, 6):
    for S in itertools.combinations(half, k):
        D = set(S) | {n - s for s in S}
        if len(D) > 9 or any((a + b) % n in D for a in D for b in D): continue
        print(g6(n, circ(n, S))); print(n, S, file=sys.stderr); c += 1
print('count', c, file=sys.stderr)
