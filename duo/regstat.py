import sys, gzip, networkx as nx
from collections import Counter
fn=sys.argv[1]
op=gzip.open if fn.endswith('.gz') else open
cnt=Counter()
with op(fn,'rt') as f:
    for line in f:
        line=line.strip()
        if not line: continue
        G=nx.from_graph6_bytes(line.encode())
        ds=sorted(set(d for _,d in G.degree()))
        cnt[(G.number_of_nodes(),G.number_of_edges(),tuple(ds))]+=1
for k,v in sorted(cnt.items()): print(k,v)
