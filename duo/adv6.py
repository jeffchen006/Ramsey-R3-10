# Survivors of adv_c35 (seven+eight-set LP value 9): add six-set rows, degree equalities, then MILP.
import sys, re, ast, numpy as np, networkx as nx
from multiprocessing import Pool
from scipy.optimize import linprog, milp, LinearConstraint, Bounds
from scipy.sparse import csr_matrix, vstack
sys.path.insert(0,'./duo'); from fraclp import indep_sets
G=nx.circulant_graph(35,[1,7,11,16])
def build(H,TS):
    n=H.number_of_nodes(); adj=[sum(1<<j for j in H[i]) for i in range(n)]
    F=indep_sets(adj,n,8); m=len(F)
    r=[];c=[];rhs=[]
    for t in TS:
        for T in indep_sets(adj,n,t):
            js=[j for j,S in enumerate(F) if S&T==0]; k=len(rhs)
            r+= [k]*len(js); c+=js; rhs.append(9-t)
    A=csr_matrix((np.ones(len(r)),(r,c)),shape=(len(rhs),m))
    D=csr_matrix(np.array([[1.0 if S>>y&1 else 0 for S in F] for y in range(n)]))
    need=np.array([9-H.degree(y) for y in range(n)],float)
    return A,np.array(rhs,float),D,need,m
def work(item):
    D5,e=item
    H=G.copy(); H.remove_nodes_from(D5); H.remove_edge(*e); H=nx.convert_node_labels_to_integers(H)
    A7,b7,Dm,need,m=build(H,(7,8))
    l=linprog(-np.ones(m),A_ub=A7,b_ub=b7,A_eq=Dm,b_eq=need,bounds=(0,1),method='highs')
    v78eq=None if l.status!=0 else round(-l.fun,6)
    A,b,_,_,_=build(H,(6,7,8))
    l=linprog(-np.ones(m),A_ub=vstack([A,Dm]),b_ub=np.concatenate([b,need]),bounds=(0,1),method='highs')
    v678=None if l.status!=0 else round(-l.fun,6)
    lp=linprog(-np.ones(m),A_ub=A,b_ub=b,A_eq=Dm,b_eq=need,bounds=(0,1),method='highs')
    v=None if lp.status!=0 else -lp.fun
    ip=None
    if v is not None and v>9-1e-6:
        A2,b2,_,_,_=build(H,(1,2,3,4,5,6,7,8))
        res=milp(-np.ones(m),constraints=[LinearConstraint(A2,-np.inf,b2),LinearConstraint(Dm,need,need)],
                 integrality=np.ones(m),bounds=Bounds(0,1))
        ip=None if res.status!=0 else round(-res.fun,4)
        if ip is not None and ip>9-1e-6:
            sel=[j for j in range(m) if res.x[j]>0.5]; print('INTEGRAL',D5,e,sel,flush=True)
    return D5,e,'v78eq',v78eq,'v678',v678,'v678eq',None if v is None else round(v,6),ip
if __name__=='__main__':
    items=[]
    for l in open('adv_c35.log'):
        m_=re.match(r'(\(.*?\)) (\(.*?\)) (\S+) (\S+)$',l.strip())
        if m_ and m_.group(4)!='None' and float(m_.group(4))>9-1e-6:
            items.append((ast.literal_eval(m_.group(1)),ast.literal_eval(m_.group(2))))
    print('survivors',len(items),flush=True)
    with Pool(4) as p:
        for out in p.imap_unordered(work,items): print(*out,flush=True)
    print('end',flush=True)
