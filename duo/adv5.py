# LP only: survivors of adv_c35 (7+8 rows value 9). Levels: (6,7,8)+eq, then add 5, then add 4 rows (stop when infeasible).
import sys, re, ast, numpy as np, networkx as nx
from multiprocessing import Pool
from scipy.optimize import linprog
sys.path.insert(0,'./duo'); from adv6 import build, G
def work(item):
    D5,e=item
    H=G.copy(); H.remove_nodes_from(D5); H.remove_edge(*e); H=nx.convert_node_labels_to_integers(H)
    out=[]
    for TS in ((6,7,8),(5,6,7,8),(4,5,6,7,8)):
        A,b,Dm,need,m=build(H,TS)
        l=linprog(-np.ones(m),A_ub=A,b_ub=b,A_eq=Dm,b_eq=need,bounds=(0,1),method='highs')
        out.append(None if l.status!=0 else round(-l.fun,6))
        if out[-1] is None: break
    return D5,e,'lev6,5,4',*out
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
