"""Double-count directed exterior edges ending at a neighbor of an independent boundary set."""
from collections import Counter
from itertools import combinations
from time import process_time
import json, sys
import numpy as np
from scipy.optimize import linprog
from scipy.sparse import csr_matrix,hstack,vstack
from book_strata import DEST,OLD,TYPES,plants,independent_sets,standard
from book_controls import sites
from book_outside import instance


def features(graph,degree,order,masks,arm):
    population=order-len(graph);words=np.array(masks,np.int64);sizes=np.array([mask.bit_count() for mask in masks]);out_degree=degree-sizes;rows=[];rhs=[];names=[]
    def emit(key,coeff,bound):
        if np.max(coeff)*population<=bound:return
        rows.append(csr_matrix(coeff));rhs.append(bound);names.append(key)
    residual=np.array([[max(0,3-(hood&mask).bit_count()) if not(mask>>site&1) else 0 for mask in masks] for site,hood in enumerate(graph)],dtype=np.int16)
    for subset in independent_sets(graph):
        size=subset.bit_count()
        if not subset:continue
        if arm in ('shadows','both'):
            cap={0:0,1:2,2:5,3:8,4:13,5:17,6:22,7:27,8:35}.get(degree-size)
            if cap is not None and cap<population:emit(('avoid',subset),((words&subset)==0).astype(np.int16),cap)
        if arm not in ('edges','both') or not(size<=2 or size>=degree-2):continue
        hit=out_degree*((words&subset)!=0);points=list(sites(subset));closed=subset
        for point in points:closed|=graph[point]
        lower=np.array([max(0,size-(mask&closed).bit_count(),int(any(not(mask>>point&1) and not(mask&graph[point]) for point in points))) for mask in masks]);upper=np.minimum(out_degree,np.sum(residual[points],axis=0));emit(('lo',subset),lower-hit,0);emit(('hi',subset),hit-upper,0)
    if not rows:return csr_matrix((0,len(masks)),dtype=np.int64),np.array([],dtype=np.int64),[]
    return vstack(rows,format='csr'),np.array(rhs,dtype=np.int64),names


def model(graph,degree,order,weak,arm):
    rules,masks,base,original=instance(graph,degree,order,weak,True);extra,rhs,names=features(graph,degree,order,masks,arm);return masks,vstack((base,extra),format='csc'),np.concatenate((original,rhs)),[('base',idx) for idx in range(len(original))]+names


def check_cal():
    for key,truth,width in plants():
        full=(1<<width)-1;graph=[row&full for row in truth[:width]];masks,matrix,rhs,names=model(graph,6,22,{(1,2),(8,9)},'both');hist=Counter(row&full for row in truth[width:]);assert set(hist)<=set(masks) and np.all(matrix@np.array([hist[mask] for mask in masks])<=rhs)
    print('PASS: integer mask counts from 18 actual C22 boundaries satisfy both edge and independence families')


def solve(key,graph,weak,arm):
    start=process_time();masks,matrix,rhs,names=model(graph,9,40,weak,arm);obj=np.zeros(len(masks)+1);obj[-1]=1;sol=linprog(obj,A_ub=hstack((matrix,-np.ones((len(rhs),1))),format='csc'),b_ub=rhs,bounds=(0,None),method='highs',options={'threads':1,'time_limit':12});out=dict(id=key,arm=arm,masks=len(masks),nrows=len(rhs),status='cap' if sol.status else 'fractional')
    if not sol.status and sol.fun>1e-8:
        for scale in (1000,100000,10000000):
            dual=np.maximum(0,np.rint(-sol.ineqlin.marginals*scale)).astype(np.int64);margin=(40-len(graph))*int(min(matrix.T@dual))-int(dual@rhs)
            if margin>0:break
        assert margin>0;out.update(status='exact-separation',dual=[(names[idx],int(num)) for idx,num in enumerate(dual) if num],margin=margin)
    out['cpu']=process_time()-start;return out


def targets():
    for deck,lp in [('boundaries','dense'),('holdout','holdlp')]:
        records={(*row['pair'],row['cross'],row['rep']):row for row in map(json.loads,(DEST/(deck+'.jsonl')).read_text().splitlines())};
        for row in map(json.loads,(DEST/(lp+'.jsonl')).read_text().splitlines()):
            if row['status']=='fractional':yield row['id'],records[tuple(row['id'])]['rows'],{(1,2),(12,13)}


if __name__=='__main__':
    if sys.argv[1]=='cal':check_cal()
    else:
        for key,graph,weak in (targets() if sys.argv[1]=='dense' else (([r['id']],standard(r['type']),{(1,2)}) for r in map(json.loads,(OLD/'single-types.jsonl').read_text().splitlines()) if r['general'] and r['status']!='excluded')):
            for arm in ('edges','shadows','both'):print(json.dumps(solve(key,graph,weak,arm),separators=(',',':')),flush=True)
