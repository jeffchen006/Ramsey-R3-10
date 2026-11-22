"""One price point for a shared exterior population on an entire double bouquet."""
from collections import Counter
from itertools import combinations,product
from pathlib import Path
from time import process_time
import json,sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix,hstack
from book_controls import sites,bitset,reorder,book
from book_join import allowed


def instance(rows,degree,order,weak,general=False):
    width=len(rows);outside=order-width;rules=[(0,outside,outside)];conflict=rows[:]
    for point,star in enumerate(rows):rules.append((1<<point,degree-star.bit_count(),degree-star.bit_count()))
    for left,right in combinations(range(width),2):
        if rows[left]>>right&1:continue
        used=(rows[left]&rows[right]).bit_count();low,cap=(1,1) if (left,right)in weak else (1 if general else 2,3);rules.append((1<<left|1<<right,low-used,cap-used))
        if used>=cap:conflict[left]|=1<<right;conflict[right]|=1<<left
    index={key:pos for pos,(key,_,_) in enumerate(rules)};masks=[];indices=[];columns=[];values=[]
    def enumerate_masks(mask,available):
        member=list(sites(mask));rank=len(masks);masks.append(mask);sub=[0,*[1<<site for site in member],*[1<<first|1<<second for first,second in combinations(member,2)]]
        for word in sub:
            pos=index[word];indices.extend((2*pos,2*pos+1));columns.extend((rank,rank));values.extend((1,-1))
        while available and len(member)<degree:
            site=available&-available;available^=site;point=site.bit_length()-1;new=mask|site
            if any((star&new).bit_count()>3 for star in rows):continue
            enumerate_masks(new,available&~conflict[point])
    enumerate_masks(0,(1<<width)-1);matrix=coo_matrix((values,(indices,columns)),shape=(2*len(rules),len(masks)),dtype=np.int64).tocsc();bound=np.array([value for _,low,cap in rules for value in (cap,-low)],dtype=np.int64)
    return rules,masks,matrix,bound


def example():
    graph=[0]*22
    def edge(left,right):graph[left]|=1<<right;graph[right]|=1<<left
    for offset in (0,11):
        edge(offset,offset+1);edge(offset,offset+2)
        for pos in range(4):
            edge(offset+1,offset+3+pos);edge(offset+2,offset+7+pos);edge(offset+3+pos,offset+7+pos);edge(offset+3+pos,offset+7+(pos+1)%4)
    edge(0,11)
    for left,right in product([3,9],[14,20]):edge(left,right)
    for a,b in product(range(4),repeat=2):
        left=(0,1,3+a,7+a,2);right=(11,12,14+b,18+b,13);mask=sum(((graph[site]>>other)&1)<<(5*i+j) for i,site in enumerate(left)for j,other in enumerate(right));assert mask in allowed('two')
    return graph


def run(folder):
    started=process_time();plants=list(map(json.loads,(folder/'cal.in').read_text().splitlines()));books=list(map(json.loads,(folder/'cal-pack2.jsonl').read_text().splitlines()))
    for (key,_,truth),plant in zip(plants,books,strict=True):
        assert key==plant['id'];core=[]
        for pair,petals in zip(((0,1),(2,3)),plant['bouquet']):core.extend(book(truth,pair)[0]);core.extend(site for petal in petals for site in petal)
        graph=reorder(truth,core+sorted(set(range(22))-set(core)));frozen=(1<<len(core))-1;weak={pair for pair in combinations(range(len(core)),2) if (graph[pair[0]]&graph[pair[1]]).bit_count()==1};_,masks,A,rhs=instance([row&frozen for row in graph[:len(core)]],6,22,weak);weights=Counter(row&frozen for row in graph[len(core):]);assert set(weights)<=set(masks) and np.all(A@np.array([weights[key] for key in masks])<=rhs)
    print('PASS planted integer exterior vectors, all 18 labelled C22 double bouquets',flush=True);graph=example();rules,masks,A,rhs=instance(graph,9,40,{(1,2),(12,13)});print('example passes 16/16 K=2 interface orbits; outside18 masks',len(masks),'rows',A.shape[0],'nonzeros',A.nnz,flush=True)
    cost=np.zeros(len(masks)+1);cost[-1]=1;opt=linprog(cost,A_ub=hstack((A,-np.ones((len(rhs),1))),format='csc'),b_ub=rhs,bounds=(0,None),method='highs',options={'time_limit':16,'threads':1});data=dict(graph=graph,status=int(opt.status),cpu=process_time()-started,masks=len(masks))
    if opt.status==0:
        data['objective']=float(opt.fun)
        if opt.fun>1e-8:
            for scale in [1000,100000,10000000]:
                dual=np.maximum(0,np.rint(-scale*opt.ineqlin.marginals)).astype(np.int64);floor=int(np.min(A.T@dual));margin=int(18*floor-dual@rhs)
                if margin>0:break
            assert margin>0;data.update(dual={pos:int(weight)for pos,weight in enumerate(dual)if weight},floor=floor,margin=margin)
    print(json.dumps(data),flush=True)


if __name__=='__main__':run(Path(sys.argv[1]))
