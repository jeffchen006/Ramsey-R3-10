# Codex r3 item 1: one shared dual (w_tau>=0, a_d free, u_sigma>=0) for a family of H.
# tau(T) = (|T|, sorted H-degrees of T, WL hash of X_T = H - N[T] with H-degree colours); sigma(S) = sorted H-degrees of S.
# (A) per H, per S: sum_tau C_tau(H,S) w_tau + sum_{y in S} a_{d(y)} + u_sigma(S) >= 0
# (B) per H: sum_tau (9-t) N_tau w_tau + sum_y (9-d(y)) a_{d(y)} + sum_S u_sigma(S) <= -1
# Feasible -> candidate uniform weights for this family; infeasible -> this type choice is rejected.
import sys, re, ast, collections, numpy as np, networkx as nx
from scipy.optimize import linprog
from scipy.sparse import csr_matrix
sys.path.insert(0,'./duo'); from fraclp import indep_sets
from adv6 import G
def bits(x): return [i for i in range(x.bit_length()) if x>>i&1]
def data(H,TS=(4,5,6,7,8)):
    n=30; adj=[sum(1<<j for j in H[i]) for i in range(n)]; deg=[H.degree(i) for i in range(n)]
    F=indep_sets(adj,n,8); full=(1<<n)-1
    C=collections.defaultdict(collections.Counter); N=collections.Counter()
    for t in TS:
        for T in indep_sets(adj,n,t):
            vs=bits(T); nb=T
            for i in vs: nb|=adj[i]
            X=H.subgraph(bits(full&~nb)).copy()
            nx.set_node_attributes(X,{i:str(deg[i]) for i in X},'d')
            tau=(t,tuple(sorted(deg[i] for i in vs)),nx.weisfeiler_lehman_graph_hash(X,node_attr='d',iterations=3) if len(X) else '')
            N[tau]+=1
            for j,S in enumerate(F):
                if S&T==0: C[j][tau]+=1
    Sd=[[deg[i] for i in bits(S)] for S in F]
    return C,N,Sd,deg
if __name__=='__main__':
    hard=[]
    for l in open(sys.argv[1]):
        m_=re.match(r'(\(.*?\)) (\(.*?\)) lev6,5,4 9.0 9.0 None',l.strip())
        if m_: hard.append((ast.literal_eval(m_.group(1)),ast.literal_eval(m_.group(2))))
    k=int(sys.argv[2]) if len(sys.argv)>2 else len(hard); hard=hard[:k]
    print('graphs',len(hard),flush=True)
    Ds=[]
    for D5,e in hard:
        H=G.copy(); H.remove_nodes_from(D5); H.remove_edge(*e); H=nx.convert_node_labels_to_integers(H)
        Ds.append(data(H)); print('built',D5,e,len(Ds[-1][1]),'types',flush=True)
    taus=sorted({t for d in Ds for t in d[1]}); ti={t:i for i,t in enumerate(taus)}
    degs=list(range(10)); sig=sorted({tuple(sorted(s)) for d in Ds for s in d[2]}); si={s:i for i,s in enumerate(sig)}
    nw,na,nu=len(taus),len(degs),len(sig); nv=nw+na+nu
    r=[];c=[];v=[];b=[];row=0
    for C,N,Sd,deg in Ds:
        for j,sd in enumerate(Sd):   # -(A) <= 0
            for tau,cnt in C[j].items(): r.append(row);c.append(ti[tau]);v.append(-cnt)
            for d in sd: r.append(row);c.append(nw+d);v.append(-1)
            r.append(row);c.append(nw+na+si[tuple(sorted(sd))]);v.append(-1); b.append(0); row+=1
        for tau,cnt in N.items(): r.append(row);c.append(ti[tau]);v.append((9-tau[0])*cnt)
        for d in deg: r.append(row);c.append(nw+d);v.append(9-d)
        for sd in Sd: r.append(row);c.append(nw+na+si[tuple(sorted(sd))]);v.append(1)
        b.append(-1); row+=1
    A=csr_matrix((v,(r,c)),shape=(row,nv))
    bounds=[(0,None)]*nw+[(None,None)]*na+[(0,None)]*nu
    res=linprog(np.zeros(nv),A_ub=A,b_ub=np.array(b,float),bounds=bounds,method='highs')
    print('types',nw,'sigma',nu,'rows',row,'status',res.status,res.message,flush=True)
