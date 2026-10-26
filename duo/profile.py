import sys, gzip, numpy as np, networkx as nx
from collections import Counter
for line in open(sys.argv[1]):
    line=line.strip()
    if not line: continue
    G=nx.from_graph6_bytes(line.encode()); A=nx.to_numpy_array(G); n=len(A)
    A2=A@A; cod=Counter(int(A2[i,j]) for i in range(n) for j in range(i+1,n) if A[i,j]==0)
    ev=np.sort(np.linalg.eigvalsh(A))
    print(n, G.number_of_edges(), dict(sorted(cod.items())), 'lmin %.3f l2 %.3f'%(ev[0],ev[-2]))
