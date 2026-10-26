# Adversarial test of Codex's fractional-gluing target: H = C35(1,7,11,16) - D - e,
# D independent 5-set (orbit reps under Aut = {x -> a x + b}), e an edge of C35 - D, alpha(H) <= 8.
import sys, itertools, networkx as nx
from multiprocessing import Pool
sys.path.insert(0,'./duo'); from fraclp import solve
n=35; Sset={1,7,11,16,34,28,24,19}
G=nx.circulant_graph(35,[1,7,11,16])
mults=[a for a in range(1,35) if all(((a*s)%35) in Sset for s in Sset) and __import__('math').gcd(a,35)==1]
assert len(mults)*35==210, mults
adj=[sum(1<<j for j in G[i]) for i in range(n)]
def canon(D):
    return min(tuple(sorted((a*x+b)%35 for x in D)) for a in mults for b in range(35))
reps=set()
for D in itertools.combinations(range(n),5):
    if all(not G.has_edge(x,y) for x,y in itertools.combinations(D,2)): reps.add(canon(D))
reps=sorted(reps)
def alpha_le8(H):
    from networkx.algorithms.clique import find_cliques
    return max(len(c) for c in find_cliques(nx.complement(H)))<=8
def work(D):
    out=[]
    base=G.copy(); base.remove_nodes_from(D)
    for e in list(base.edges()):
        H=base.copy(); H.remove_edge(*e)
        if not alpha_le8(H): continue
        H=nx.convert_node_labels_to_integers(H)
        v8=solve(H,(8,))[0]
        v78=solve(H,(7,8))[0] if v8>9-1e-7 else None
        out.append((D,e,round(v8,5),None if v78 is None else round(v78,5)))
    return out
if __name__=='__main__':
    print('reps',len(reps),flush=True)
    with Pool(3) as p:
        for res in p.imap_unordered(work,reps):
            for r in res: print(*r,flush=True)
    print('end',flush=True)
