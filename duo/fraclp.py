# Fractional regular-gluing LP (Codex round 2, idea 1). For H in R(3,9;30,99):
# max sum z_S over independent 8-sets S, 0<=z<=1, sum_{S∋y} z_S <= 9-deg(y) (or ==, with --eq),
# for independent T of size t in TS: sum_{S∩T=∅} z_S <= 9-t.
import sys, numpy as np, networkx as nx
from scipy.optimize import linprog
from scipy.sparse import lil_matrix, csr_matrix
def indep_sets(adj,n,k):
    out=[]
    def rec(start,mask,cnt,cand):
        if cnt==k: out.append(mask); return
        for i in range(start,n):
            if cand>>i&1: rec(i+1,mask|1<<i,cnt+1,cand&~adj[i]&~((1<<(i+1))-1))
    rec(0,0,0,(1<<n)-1); return out
def solve(H,TS=(8,),eq=False):
    n=H.number_of_nodes(); adj=[sum(1<<j for j in H[i]) for i in range(n)]
    F=indep_sets(adj,n,8); m=len(F)
    rows=[];rhs=[]
    for t in TS:
        for T in indep_sets(adj,n,t):
            rows.append([j for j,S in enumerate(F) if S&T==0]); rhs.append(9-t)
    A=lil_matrix((len(rows),m))
    for r,cols in enumerate(rows):
        for j in cols: A[r,j]=1
    D=np.zeros((n,m))
    for j,S in enumerate(F):
        for y in range(n):
            if S>>y&1: D[y,j]=1
    need=np.array([9-H.degree(y) for y in range(n)])
    kw=dict(A_eq=D,b_eq=need) if eq else {}
    Aub=A.tocsr(); bub=np.array(rhs,float)
    if not eq:
        from scipy.sparse import vstack
        Aub=vstack([Aub,csr_matrix(D)]); bub=np.concatenate([bub,need])
    r=linprog(-np.ones(m),A_ub=Aub,b_ub=bub,bounds=(0,1),method='highs',**kw)
    return (-r.fun if r.status==0 else None), m, len(rows)
if __name__=='__main__':
    TS=tuple(int(x) for x in sys.argv[2].split(','))
    lines=[l.strip() for l in open(sys.argv[1]) if l.strip()]
    lo=int(sys.argv[3]) if len(sys.argv)>3 else 0; hi=int(sys.argv[4]) if len(sys.argv)>4 else len(lines)
    for i in range(lo,hi):
        H=nx.from_graph6_bytes(lines[i].encode())
        print(i, H.number_of_nodes(), H.number_of_edges(), *solve(H,TS), flush=True)
