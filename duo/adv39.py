# Codex r3 item 2: H = G - N[v], G a (3,10;39) graph, v of degree 8 with all neighbours of degree 9 (|H|=30, e=99).
# Fractional gluing LP with degree equalities; levels (8),(7,8),(6..8),(5..8),(4..8); stop at first infeasible.
import sys, numpy as np, networkx as nx
from multiprocessing import Pool
from scipy.optimize import linprog
sys.path.insert(0,'./duo'); from adv6 import build
def items():
    seen=set(); out=[]
    for f in ('known39/out/sample1000_39.g6','known39/out/r2_seeds.g6'):
        for ln,l in enumerate(open('./'+f),1):
            l=l.strip()
            if not l: continue
            G=nx.from_graph6_bytes(l.encode())
            for v in G:
                if G.degree(v)==8 and all(G.degree(x)==9 for x in G[v]):
                    H=G.copy(); H.remove_nodes_from(list(G[v])+[v]); H=nx.convert_node_labels_to_integers(H)
                    if H.number_of_edges()!=99: continue
                    h=nx.weisfeiler_lehman_graph_hash(H,iterations=4)
                    if h in seen: continue
                    seen.add(h); out.append((f,ln,v,nx.to_graph6_bytes(H,header=False).strip().decode()))
    return out
def work(it):
    f,ln,v,g=it; H=nx.from_graph6_bytes(g.encode()); res=[]
    for TS in ((8,),(7,8),(6,7,8),(5,6,7,8),(4,5,6,7,8)):
        A,b,Dm,need,m=build(H,TS)
        l=linprog(-np.ones(m),A_ub=A,b_ub=b,A_eq=Dm,b_eq=need,bounds=(0,1),method='highs')
        res.append(None if l.status!=0 else round(-l.fun,6))
        if res[-1] is None: break
    return f.split('/')[-1],ln,v,'levels8..4',*res,'SURVIVOR' if res[-1] is not None else '',g
if __name__=='__main__':
    its=items(); print('instances',len(its),flush=True)
    with Pool(4) as p:
        for o in p.imap_unordered(work,its): print(*o,flush=True)
    print('end',flush=True)
