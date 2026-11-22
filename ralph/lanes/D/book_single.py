"""Whole eleven-site books: screen all 41 types against the same 29 outside vertices."""
from collections import Counter
from itertools import combinations
from pathlib import Path
from time import process_time
import json,sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import hstack
from book_outside import instance
from book_contacts import standard
from book_controls import sites,bitset,reorder


def screen(rows,general):
    graph=standard(rows);rules,masks,A,b=instance(graph,9,40,{(1,2)},general);cost=np.zeros(len(masks)+1);cost[-1]=1;sol=linprog(cost,A_ub=hstack((A,-np.ones((len(b),1))),format='csc'),b_ub=b,bounds=(0,None),method='highs',options={'threads':1,'time_limit':4});data=dict(type=rows,general=general,masks=len(masks),status='cap');assert sol.status==0
    if sol.fun>1e-8:
        for scale in (1000,100000,10000000):
            weights=np.maximum(0,np.rint(-sol.ineqlin.marginals*scale)).astype(np.int64);worst=int(min(A.T@weights));margin=29*worst-int(b@weights)
            if margin>0:break
        assert margin>0;data.update(status='excluded',dual={idx:int(num) for idx,num in enumerate(weights) if num},margin=margin)
    else:
        for scale in (1,2,6,12,60,120,840,2520,27720,360360,12252240):
            x=np.rint(scale*sol.x[:-1]).astype(np.int64)
            if np.all(x>=0) and np.all(A@x<=b*scale):data.update(status='rational',scale=scale,point={mask:int(val) for mask,val in zip(masks,x) if val});break
        else:data.update(status='fractional')
    return data


def replay(record):
    rows=record['type'];graph=standard(rows);neighbors=[set(sites(word)) for word in graph];pairs=list(combinations(range(11),2));weak=(1,2);labels=[(set(),29,29)]+[({site},9-len(hood),9-len(hood)) for site,hood in enumerate(neighbors)];allowed=[]
    for a,b in pairs:
        if b in neighbors[a]:continue
        known=len(neighbors[a]&neighbors[b]);low,high=(1,1) if (a,b)==weak else ((1 if record['general'] else 2),3);labels.append(({a,b},low-known,high-known))
    for subset in range(1<<11):
        mask=set(sites(subset))
        if len(mask)>9 or any(len(row&mask)>3 for row in neighbors) or any(b in neighbors[a] for a,b in combinations(sorted(mask),2)):continue
        if any(hi==0 and len(term)==2 and term<=mask for term,_,hi in labels):continue
        allowed.append(mask)
    assert len(allowed)==record['masks']
    if record['status']=='excluded':
        multipliers=[(labels[int(idx)//2],int(val),int(idx)%2) for idx,val in record['dual'].items()];rhs=sum(val*(-low if sign else high) for (_,low,high),val,sign in multipliers);floor=min(sum(val*(-1 if sign else 1) for (term,_,_),val,sign in multipliers if term<=mask) for mask in allowed);assert 29*floor-rhs==record['margin']>0
    if record['status']=='rational':
        masses=[(set(sites(int(mask))),int(value)) for mask,value in record['point'].items()];assert all(mask in allowed and val>=0 for mask,val in masses)
        for term,low,high in labels:assert low*record['scale']<=sum(val for mask,val in masses if term<=mask)<=high*record['scale']


def run(folder):
    start=process_time();summary=Counter();plants=list(map(json.loads,(folder/'cal.in').read_text().splitlines()));books=list(map(json.loads,(folder/'cal-pack2.jsonl').read_text().splitlines()));checked=0
    for (_,_,truth),record in zip(plants,books,strict=True):
        for (a,b),petals in zip(((0,1),(2,3)),record['bouquet']):
            h,=sites(truth[a]&truth[b]);indices=[h,a,b,*[edge[0] for edge in petals],*[edge[1] for edge in petals]];g=reorder(truth,indices+sorted(set(range(22))-set(indices)));width=len(indices);frozen=(1<<width)-1;low={pair for pair in combinations(range(width),2) if (g[pair[0]]&g[pair[1]]).bit_count()==1};_,masks,A,bound=instance([row&frozen for row in g[:width]],6,22,low);w=Counter(row&frozen for row in g[width:]);assert set(w)<=set(masks) and np.all(A@np.array([w[mask]for mask in masks])<=bound);checked+=1
    print('positive planted 7-site books',checked)
    with (folder/'single-types.jsonl').open('w') as out:
        for idx,line in enumerate((folder/'booktypes4.tsv').read_text().splitlines()):
            *rows,_=map(int,line.split())
            for general in [True,False]:
                rec=screen(rows,general);replay(rec);rec['id']=idx;print(json.dumps(rec,separators=(',',':')),file=out);summary[general,rec['status']]+=1
    print('all individual types; integer replay',summary,'cpu',process_time()-start)


if __name__=='__main__':run(Path(sys.argv[1]))
