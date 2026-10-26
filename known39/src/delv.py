"""Print graph6 of G - v for each v (or for v in argv[2:])."""
import sys
sys.path.insert(0, './tools')
from check_graph import parse_graph6, to_graph6
for line in open(sys.argv[1]):
    if not line.strip(): continue
    adj = parse_graph6(line.strip()); n = len(adj)
    vs = [int(x) for x in sys.argv[2:]] or range(n)
    for v in vs:
        keep = [u for u in range(n) if u != v]
        idx = {u: i for i, u in enumerate(keep)}
        b = [0] * (n - 1)
        for u in keep:
            for w in keep:
                if adj[u] >> w & 1: b[idx[u]] |= 1 << idx[w]
        print(to_graph6(b))
