"""A 19-site induced full book, both endpoint stars fixed, shared exterior masks."""
from collections import Counter
from itertools import combinations,product
from time import process_time
import json, sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import hstack,coo_matrix
from book_strata import DEST,standard,independent_sets
from book_controls import sites,bitset
from kernel_cnf import decode


def wings(text):
    width=(ord(text[0])-63)//2;edges=decode(text);return [bitset(col-width for u,col in edges if u==row) for row in range(width)]


def system(rows,order,mode):
    graph=standard(rows);width=len(rows);degree=width+1;outside=order-len(graph);labels=[('total',0,outside,outside)];rules={};maxsets=[mask for mask in independent_sets(graph) if mask.bit_count()==degree];sets=[]
    for site,word in enumerate(graph):
        if site not in (1,2):rules[1<<site]=len(labels);labels.append(('deg',1<<site,degree-word.bit_count(),degree-word.bit_count()))
    for a,b in combinations(range(len(graph)),2):
        if graph[a]>>b&1 or a in (1,2) or b in (1,2):continue
        used=(graph[a]&graph[b]).bit_count();rules[1<<a|1<<b]=len(labels);labels.append(('pair',1<<a|1<<b,1-used,3-used))
    if mode=='ramsey':
        for word in independent_sets(graph):
            cap={0:0,1:2,2:5,3:8,4:13,5:17}.get(degree-word.bit_count(),99)
            if 0<cap<outside:sets.append(word);labels.append(('avoid',word,0,cap))
    active=[word for word in range(1,1<<width) if word.bit_count()<=3];indices=[];columns=[];masks=[];full=(1<<len(graph))-1;closures={word:bitset(col for col in range(width) if any(rows[site]>>col&1 for site in sites(word))) for word in active};sat=[mask for mask,idx in rules.items() if labels[idx][0]=='pair' and not labels[idx][3]]
    for left,right in product(active,repeat=2):
        if closures[left]&right:continue
        for centre in (0,1):
            if max(left.bit_count(),right.bit_count())+centre>3:continue
            mask=centre|(left<<3)|(right<<(3+width));
            if any(not(mask&word) for word in maxsets) or any(mask&term==term for term in sat) or any((hood&mask).bit_count()>3 for hood in graph):continue
            points=list(sites(mask));col=len(masks);masks.append(mask);hits=[0,*[rules[1<<site] for site in points],*[rules[1<<a|1<<b] for a,b in combinations(points,2)]];hits.extend(len(labels)-len(sets)+idx for idx,term in enumerate(sets) if not(mask&term));indices.extend(hits);columns.extend([col]*len(hits))
    matrix=coo_matrix((np.ones(len(indices),dtype=np.int64),(indices,columns)),shape=(len(labels),len(masks))).tocsc();return graph,labels,masks,matrix


def cal():
    hits=0
    for record in map(json.loads,(DEST/'wing-cal.jsonl').read_text().splitlines()):
        for mode in ('basic','ramsey'):
            _,labels,masks,matrix=system(record['rows'],22,mode);plant=Counter((m<<3)|1 for m in record['y']);plant.update(m<<3 for m in record['z']);assert set(plant)<=set(masks);out=matrix@np.array([plant[m] for m in masks]);assert all(low<=value<=cap for (_,_,low,cap),value in zip(labels,out,strict=True));hits+=1
    print('PASS full-wing calibrated integer exterior counts',hits)


def separate(idx,line,mode):
    start=process_time();rows=wings(line);graph,labels,masks,matrix=system(rows,40,mode);pop=40-len(graph);bound=np.array([num for _,_,low,cap in labels for num in (cap,-low)],dtype=np.int64);from scipy.sparse import vstack
    interlace=np.column_stack((np.arange(len(labels)),np.arange(len(labels))+len(labels))).ravel();A=vstack((matrix,-matrix),format='csc')[interlace,:];obj=np.zeros(len(masks)+1);obj[-1]=1;out=dict(id=idx,rows=rows,edges=sum(r.bit_count() for r in rows),mode=mode,columns=len(masks),constraints=len(labels),status='cap')
    if not masks:out.update(status='empty');return out
    sol=linprog(obj,A_ub=hstack((A,-np.ones((len(bound),1))),format='csc'),b_ub=bound,bounds=(0,None),method='highs',options={'threads':1,'time_limit':12})
    if not sol.status:
        if sol.fun<1e-8:out['status']='fractional'
        else:
            for scale in (1000,100000,10000000):
                dual=np.maximum(0,np.rint(-sol.ineqlin.marginals*scale)).astype(np.int64);floor=int(min(A.T@dual));margin=pop*floor-int(dual@bound)
                if margin>0:break
            assert margin>0;out.update(status='separated',dual=[[*labels[pos//2],pos%2,int(value)] for pos,value in enumerate(dual) if value],margin=margin)
    out['cpu']=process_time()-start;return out


if __name__=='__main__':
    if sys.argv[1]=='cal':cal()
    else:
        low,high=map(int,sys.argv[2:4]);shard,mod=map(int,sys.argv[4:6]);kept=0
        with (DEST/'wing8.g6').open() as db,(DEST/'wing8.scan').open() as scan:
            for idx,(line,meta) in enumerate(zip(db,scan,strict=True)):
                row=meta.split()
                if row[2]!='live' or not low<=int(row[1])<=high:continue
                kept+=1
                if (kept-1)%mod==shard:print(json.dumps(separate(idx,line.strip(),sys.argv[1]),separators=(',',':')),flush=True)
