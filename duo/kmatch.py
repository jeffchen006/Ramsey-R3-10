# Filter genbg output (bipartite n1+n2, graph6) by maximum matching >= m. Usage: kmatch.py n1 m < in > out
import sys, networkx as nx
n1, m = int(sys.argv[1]), int(sys.argv[2])
for l in sys.stdin:
    G = nx.from_graph6_bytes(l.strip().encode())
    if len(nx.max_weight_matching(G, maxcardinality=True)) >= m: sys.stdout.write(l)
