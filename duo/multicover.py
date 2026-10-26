# For H in R(3,9;30,99): does H have 9 distinct independent 8-sets T_1..T_9 with each y in exactly 9-deg_H(y) of them?
# (necessary for H = G - N[v] in a 9-regular (3,10,40)-graph; T_x = N(x)-v)
import sys, numpy as np, networkx as nx
from scipy.optimize import milp, LinearConstraint, Bounds
def indep_sets(adj, n, k):
    out=[]
    def rec(start, cur, cand):
        if len(cur)==k: out.append(cur); return
        for i in range(start,n):
            if cand>>i &1:
                rec(i+1, cur+[i], cand & ~adj[i] & ~((1<<(i+1))-1))
    rec(0,[], (1<<n)-1); return out
res=[]
for line in open(sys.argv[1]):
    line=line.strip()
    if not line: continue
    H=nx.from_graph6_bytes(line.encode()); n=H.number_of_nodes()
    adj=[sum(1<<j for j in H[i]) for i in range(n)]
    S=indep_sets(adj,n,8)
    need=np.array([9-H.degree(i) for i in range(n)])
    M=np.zeros((n,len(S)))
    for j,s in enumerate(S): M[s,j]=1
    cons=[LinearConstraint(M,need,need), LinearConstraint(np.ones((1,len(S))),9,9)]
    r=milp(np.zeros(len(S)),constraints=cons,integrality=np.ones(len(S)),bounds=Bounds(0,1))
    res.append((len(S), r.status==0))
    print(len(S), r.status, flush=True)
print('feasible', sum(f for _,f in res), 'of', len(res))
