"""Two pentagons with unknown shared exterior occupancy and reciprocal edge counts."""
from itertools import combinations
from pathlib import Path
import json
import sys
import numpy as np
from scipy.sparse import coo_matrix,hstack
from scipy.optimize import linprog
from kernel_cnf import ROOT,decode


def core_graph(rows):
    columns=[sum(1<<idx for idx,row in enumerate(rows) if row>>site&1) for site in range(5)]
    cycle=[(1<<((idx-1)%5))|(1<<((idx+1)%5)) for idx in range(5)]
    return [cycle[idx]|rows[idx]<<5 for idx in range(5)]+[cycle[idx]<<5|columns[idx] for idx in range(5)]


def model(rows,order,degree,plant=None,square=False):
    core=core_graph(rows);width=len(core);frozen=(1<<width)-1;weak={(1,4),(6,9)};cap=order-width
    if plant:weak={pair for pair in combinations(range(width),2) if (plant[pair[0]]&plant[pair[1]]).bit_count()==1}
    saturated={pair for pair in weak if core[pair[0]]&core[pair[1]]}
    masks=[mask for mask in range(1<<width) if not any(mask>>site&1 and mask&core[site] for site in range(width)) and all(not(mask>>first&mask>>second&1) for first,second in saturated)]
    uses=list(range(len(masks)));pairs=[(left,right) for left in uses for right in uses[left:] if not masks[left]&masks[right]];columns=len(masks)+len(pairs);ir=[];ic=[];values=[];rhs=[];connections=[[] for mask in masks]
    for var,(left,right) in enumerate(pairs,len(masks)):
        connections[left].append((var,right));
        if left!=right:connections[right].append((var,left))
    def put(terms,bound,sign=1):
        rhs.append(sign*bound)
        for var,coeff in terms:ir.append(len(rhs)-1);ic.append(var);values.append(sign*coeff)
    def bounded(terms,low,high):put(terms,low,-1);put(terms,high)
    bounded([(site,1) for site in uses],cap,cap)
    for vertex in range(width):
        need=degree-core[vertex].bit_count();bounded([(idx,1)for idx,mask in enumerate(masks) if mask>>vertex&1],need,need)
    for first,second in combinations(range(width),2):
        if core[first]>>second&1:continue
        unique=(first,second) in weak;shared=(core[first]&core[second]).bit_count();bounded([(idx,1)for idx,mask in enumerate(masks) if mask>>first&mask>>second&1],(1 if unique else 2)-shared,(1 if unique else 3)-shared)
    for idx,mask in enumerate(masks):
        bounded([(idx,mask.bit_count()-degree),*((var,1) for var,other in connections[idx])],0,0)
        for vertex in range(width):
            if mask>>vertex&1:continue
            covered=(mask&core[vertex]).bit_count();terms=[(var,1)for var,other in connections[idx] if masks[other]>>vertex&1]
            corrections=sum((row&frozen)==mask and (row&plant[vertex]).bit_count()==1 for row in plant[width:]) if plant else 0
            put([(idx,2-covered),*((var,-1)for var,_ in terms)],corrections);put([(idx,covered-3),*terms],0)
    if square:
        for first,last in combinations(range(width),2):
            if not core[first]>>last&1:continue
            left=core[first]&~(1<<last);right=core[last]&~(1<<first)
            internal=sum((core[site]&right).bit_count() for site in range(width) if left>>site&1)
            if plant:
                quota=sum((plant[site]&plant[last]&~(1<<first)).bit_count() for site in range(order) if site!=last and plant[first]>>site&1)
            else:quota=14 if first in (1,4) and last in (6,9) else 12
            coefficients=[]
            for idx,mask in enumerate(masks):
                value=((mask&right).bit_count() if mask>>first&1 else 0)+((mask&left).bit_count() if mask>>last&1 else 0)
                if value:coefficients.append((idx,value))
            for var,(a,b) in enumerate(pairs,len(masks)):
                if (masks[a]>>first&masks[b]>>last&1) or (masks[a]>>last&masks[b]>>first&1):coefficients.append((var,1))
            bounded(coefficients,quota-internal,quota-internal)
    matrix=coo_matrix((values,(ir,ic)),shape=(len(rhs),columns),dtype=np.int64).tocsr();bound=np.asarray(rhs,dtype=np.int64);upper=np.asarray([cap]*len(uses)+[cap*degree]*len(pairs),dtype=np.int64)
    if plant:
        lookup={mask:idx for idx,mask in enumerate(masks)};blocks=[lookup[mask&frozen] for mask in plant[width:]];truth=np.zeros(columns,dtype=np.int64)
        for idx in blocks:truth[idx]+=1
        index={pair:var for var,pair in enumerate(pairs,len(masks))}
        for first,second in combinations(range(width,order),2):
            if plant[first]>>second&1:
                left,right=sorted((blocks[first-width],blocks[second-width]));truth[index[left,right]]+=1+(left==right)
        assert (matrix@truth<=bound).all() and (truth<=upper).all();return {'status':'planted','masks':len(masks),'columns':columns}
    relaxed=hstack([matrix,-np.ones((len(rhs),1))],format='csc');objective=np.zeros(columns+1);objective[-1]=1
    result=linprog(objective,A_ub=relaxed,b_ub=bound,bounds=(0,None),method='highs',options={'threads':1,'time_limit':12});info={'masks':len(masks),'columns':columns,'constraints':len(rhs)}
    if result.status!=0:return dict(status='uncertain',**info)
    if result.fun<=1e-7:return dict(status='fractional',**info)
    for scale in (1000,100000,10000000):
        dual=np.maximum(0,np.rint(-scale*result.ineqlin.marginals)).astype(np.int64);weights=matrix.T@dual;margin=int(np.minimum(weights,0)@upper-dual@bound)
        if margin>0:return dict(status='exact-separation',dual={idx:int(value)for idx,value in enumerate(dual)if value},margin=margin,**info)
    return dict(status='inexact',**info)


def control(square=False):
    tested=0
    for code in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        edges=decode(code);graph=[{last if first==point else first for first,last in edges if point in (first,last)} for point in range(22)]
        if {len(row) for row in graph}!={6} or any(len(left&right)>3 for left,right in combinations(graph,2)):continue
        cycles=[]
        for first,second in combinations(range(22),2):
            common=graph[first]&graph[second]
            if len(common)==1:
                centre=next(iter(common));cycles.extend((centre,first,left,right,second) for left in graph[first]-common for right in graph[left]&graph[second]-common)
        for idx in range(0,len(cycles),11):
            left=cycles[idx];right=next(other for other in cycles if not set(left)&set(other));pins=(*left,*right);sites=[*pins,*sorted(set(range(22))-set(pins))];plant=[sum(1<<spot for spot,last in enumerate(sites) if last in graph[first]) for first in sites];rows=[(row>>5)&31 for row in plant[:5]];assert model(rows,22,6,plant,square)['status']=='planted';tested+=1
    print('PASS planted integral occupancy and reciprocal weights on',tested,'paired-C5 controls; known extra deficiencies supplied',flush=True)


if __name__=='__main__':
    folder=Path(sys.argv[1]);square='--square' in sys.argv[3:];control(square);stride=int(sys.argv[2]);lines=(folder/'interfaces.tsv').read_text().splitlines()
    for idx,text in enumerate(lines):
        if idx%stride:continue
        rows=list(map(int,text.split()[:5]));
        if square and sum((rows[idx]&18).bit_count() for idx in (1,4))!=2:continue
        print(json.dumps(dict(index=idx,**model(rows,40,9,square=square))),flush=True)
