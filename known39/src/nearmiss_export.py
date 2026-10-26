"""Export near misses: results.txt + all.g6 -> lines 'unmet idx g6_39 g6_40(G+w)' for unmet <= T.
Usage: nearmiss_export.py DIR T"""
import sys
sys.path.insert(0, './tools')
from check_graph import parse_graph6, to_graph6
d, T = sys.argv[1], int(sys.argv[2])
want = {}
for line in open(d + '/results.txt'):
    if line[0] == '#': continue
    f = line.split()
    if f[7] == '0' and int(f[8]) <= T: want[int(f[0])] = (int(f[8]), int(f[10], 16))
for i, line in enumerate(open(d + '/all.g6')):
    if i in want:
        g6 = line.strip(); adj = parse_graph6(g6); n = len(adj); unmet, S = want[i]
        a = adj + [S]
        for v in range(n):
            if S >> v & 1: a[v] |= 1 << n
        print(unmet, i, g6, to_graph6(a))
    if want and i > max(want): break
