"""Read 0/1 adjacency matrix; write graph6 of the graph (or its complement with -c)."""
import sys
sys.path.insert(0, './tools')
from check_graph import to_graph6
args = sys.argv[1:]
comp = '-c' in args
args = [a for a in args if a != '-c']
rows = [l.strip() for l in open(args[0]) if l.strip()]
n = len(rows)
adj = [0] * n
for u in range(n):
    for v in range(n):
        if u != v and (rows[u][v] == '1') != comp:
            adj[u] |= 1 << v
print(to_graph6(adj))
