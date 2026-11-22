"""Physical second deficient P3 on a fixed first book; exact shared-site margins."""
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product
from pathlib import Path
from time import process_time
import json, sys, warnings
import numpy as np
from scipy.optimize import linprog, OptimizeWarning
from scipy.sparse import csc_matrix, hstack
from book_controls import book, flags, graph_masks, reorder, sites, bitset
from book_strata import standard, independent_sets
from kernel_cnf import ROOT
from wing_population import system

DEST = ROOT/'scratch/D/roles15'
SHAPES = ((8,), (5,3), (4,4))
warnings.filterwarnings('ignore',category=OptimizeWarning)


def shape(parts):
    rows=[]; cycles=[]; width=sum(parts)
    for length in parts:
        base=len(rows); cycle=[]
        for local in range(length):
            left=base+local; right=base+(local+1)%length
            rows.append(1<<left | 1<<right);cycle.extend((3+left,3+width+right))
        cycles.append(cycle)
    return tuple(rows), cycles


def group(cycles):
    for swaps in (0,1):
        for order in permutations(cycles):
            if any(len(before)!=len(after) for before,after in zip(cycles,order)):continue
            for actions in product(*(tuple(product(range(swaps,len(cycle),2),(-1,1))) for cycle in cycles)):
                perm=[0,2 if swaps else 1,1 if swaps else 2]+[0]*sum(map(len,cycles))
                for before,after,(offset,step) in zip(cycles,order,actions):
                    for idx,point in enumerate(before):perm[point]=after[(offset+step*idx)%len(after)]
                yield tuple(perm)


def normalize(path,size):
    ends=sorted(path[:2]);return _normal((*ends,path[2]),size)


def _normal(path,size):
    idx=size;out=[]
    for point in path:
        if point>=size:out.append(idx);idx+=1
        else:out.append(point)
    return tuple(out)


def clash(core,path):
    size=len(core);first,second,witness=path
    for lhs,rhs,edge in ((first,second,0),(first,witness,1),(second,witness,1)):
        if lhs<size and rhs<size and bool(core[lhs]>>rhs&1)!=bool(edge):return 'edge'
    if max(first,second)<size and core[first]&core[second]&~(1<<witness):return 'old-common'


def roster(parts):
    rows,cycles=shape(parts);core=standard(rows);size=len(core);perms=list(group(cycles));seen=set();result=[]
    assert len(set(perms))==len(perms) and all(reorder(core,perm)==core for perm in perms)
    for first,second in combinations(range(3,size+3),2):
        for witness in range(3,size+3):
            if witness in (first,second):continue
            path=normalize((first,second,witness),size)
            if path in seen:continue
            orbit={normalize(tuple(perm[site] if site<size else site for site in path),size) for perm in perms};seen.update(orbit);path=min(orbit)
            result.append(dict(path=path,orbit=len(orbit),reason=clash(core,path)))
    return sorted(result,key=lambda row:row['path'])


@lru_cache(None)
def domain(rows,order,otherlow):
    core,_,words,_=system(rows,order,'basic')
    words=[word for word in words if all((word&core[anchor]).bit_count()>=otherlow for anchor in (1,2))]
    return core,np.array(words,dtype=np.int64)


def build(rows,order,path,otherlow):
    core,words=domain(rows,order,otherlow);size=len(core);degree=1+len(rows);first,second,witness=path;ends={first,second};extra=sorted(set(path)-set(range(size)));assert extra==list(range(size,size+len(extra)));full=size+len(extra);pop=order-full
    def fixed(lhs,rhs):
        if lhs==rhs:return 0
        if lhs<size and rhs<size:return (core[lhs]>>rhs)&1
        if {lhs,rhs}==ends:return 0
        if {lhs,rhs} in ({first,witness},{second,witness}):return 1
        if min(lhs,rhs) in (1,2):return 0
    blocks=[];limits=[];base=0
    for anchor in extra:
        keep=np.ones(len(words),bool);outside=0
        for point in range(size):
            value=fixed(anchor,point)
            if value is not None:keep&=(words>>point&1)==value
        for point in extra:
            if fixed(anchor,point):outside|=1<<point
        blocks.append(words[keep]|outside);limits.append(1)
    blocks.append(np.concatenate([words|(contact<<size) for contact in range(1<<len(extra))]));limits.append(pop)
    if any(len(words)==0 for words in blocks):return None
    offsets=np.cumsum([0,*map(len,blocks)]);width=int(offsets[-1]);generic=len(extra);products=list(product(combinations(extra,2),range(size)));aux={key:width+idx for idx,key in enumerate(products)};width+=len(products)
    masks=np.concatenate(blocks);coeff=[];bounds=[]
    @lru_cache(None)
    def hit(block,bits):
        out=np.zeros(width,np.int16);offset=offsets[block];end=offsets[block+1];out[offset:end]=(masks[offset:end]&bits)==bits;return out
    def scalar(value):return (np.zeros(width,np.int16),int(value))
    def add(left,right):return (left[0]+right[0],left[1]+right[1])
    def times(term,scale):return (term[0]*scale,term[1]*scale)
    def leq(term,bound):coeff.append(term[0]);bounds.append(bound-term[1])
    def span(term,low,high):leq(term,high);leq(times(term,-1),-low)
    def edge(lhs,rhs):
        val=fixed(lhs,rhs)
        if val is not None:return scalar(val)
        point,anchor=sorted((lhs,rhs));return (hit(anchor-size,1<<point),0)
    def common(lhs,rhs,point):
        left=fixed(lhs,point);right=fixed(rhs,point)
        if left is not None:return times(edge(rhs,point),left)
        if right is not None:return times(edge(lhs,point),right)
        if point>=size:return hit(point-size,1<<lhs|1<<rhs),0
        out=np.zeros(width,np.int16);out[aux[(lhs,rhs),point]]=1;return out,0
    for (lhs,rhs),point in products:
        term=np.zeros(width,np.int16);term[aux[(lhs,rhs),point]]=1;left=edge(lhs,point);right=edge(rhs,point);leq(add((term,0),times(left,-1)),0);leq(add((term,0),times(right,-1)),0);leq(add(add(left,right),(-term,0)),1)
    for block,limit in enumerate(limits):span((hit(block,0),0),limit,limit)
    for lhs in range(full):
        terms=(hit(generic,1<<lhs),0)
        for point in range(full):terms=add(terms,edge(lhs,point))
        span(terms,degree,degree)
    for lhs,rhs in combinations(range(full),2):
        terms=(hit(generic,1<<lhs|1<<rhs),0)
        for point in range(full):terms=add(terms,common(lhs,rhs,point))
        weak=(lhs,rhs)==(1,2) or {lhs,rhs}==ends;low=1 if weak else otherlow;upper=1 if weak else 3;adj=edge(lhs,rhs)
        leq(add(terms,times(adj,upper)),upper);leq(times(add(terms,times(adj,low)),-1),-low)
    matrix=csc_matrix(np.stack(coeff).astype(np.int32));return matrix,np.array(bounds),offsets,limits,blocks,aux


def verify(data,dual):
    matrix,bound,offsets,limits,_,_=data;prices=matrix.T@dual;floor=sum(count*int(min(prices[left:right])) for count,left,right in zip(limits,offsets,offsets[1:]));return floor+int(np.minimum(prices[offsets[-1]:],0).sum())-int(dual@bound)


def price(rows,path,order=40,low=2):
    start=process_time();data=build(rows,order,path,low);out={'path':path}
    if data is None:out.update(status='empty')
    else:
        matrix,bounds,*_=data;obj=np.zeros(matrix.shape[1]+1);obj[-1]=1;result=linprog(obj,A_ub=hstack((matrix,-np.ones((len(bounds),1))),format='csc'),b_ub=bounds,bounds=(0,None),method='highs',options={'threads':1,'time_limit':14});out.update(status='cap' if result.status else 'fractional')
        if not result.status and result.fun>1e-7:
            for scale in (1000,100000,10000000):
                dual=np.maximum(0,np.rint(-result.ineqlin.marginals*scale)).astype(np.int64);margin=verify(data,dual)
                if margin>0:break
            assert margin>0;out.update(status='separated',margin=margin,dual={idx:int(dual[idx]) for idx in np.flatnonzero(dual).tolist()})
    return dict(**out,cpu=process_time()-start)


def plant(rows,order,path,graph):
    data=build(rows,order,path,1)
    if data is None:return False
    matrix,bound,offsets,limits,blocks,aux=data;size=3+2*len(rows);full=size+len(blocks)-1;values=np.zeros(matrix.shape[1],np.int64)
    for block,words in enumerate(blocks):
        lookup={int(word):idx for idx,word in enumerate(words)};points=[size+block] if block<len(blocks)-1 else range(full,order)
        for point in points:
            word=graph[point]&((1<<full)-1)
            if word not in lookup:return False
            values[offsets[block]+lookup[word]]+=1
    for ((lhs,rhs),point),idx in aux.items():values[idx]=(graph[lhs]&graph[rhs])>>point&1
    return bool(np.all(matrix@values<=bound))


def calibrate():
    counts=Counter();host_counts=Counter();wrong=0;wrong_outer=0
    for idx,text in enumerate((ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines()):
        graph=graph_masks(text)
        if {word.bit_count() for word in graph}!={6} or max((one&two).bit_count() for one,two in combinations(graph,2))>3:continue
        for ends in flags(graph):
            frame,(left,right)=book(graph,ends);core=list(frame)+list(left)+list(right);size=len(core);rows=tuple(bitset(col for col,site in enumerate(right) if graph[point]>>site&1) for point in left)
            for second in flags(graph):
                if second==ends:continue
                midpoint,=sites(graph[second[0]]&graph[second[1]]);path=(*second,midpoint);key=tuple(sorted(point in core for point in second))+(midpoint in core,);host_counts[idx]+=1
                if counts[key]>=5:continue
                outside=[point for point in path if point not in core];order=core+outside+sorted(set(range(22))-set(core+outside));path=tuple(order.index(point) for point in path);truth=reorder(graph,order);assert not clash(standard(rows),path) and plant(rows,22,path,truth);counts[key]+=1
                if not outside and not wrong:
                    bad=next(point for point in range(size) if point not in path and not(truth[point]>>path[0]&truth[point]>>path[1]&1));mut=(*path[:2],bad);assert clash(standard(rows),mut) or not plant(rows,22,mut,truth);wrong+=1
                if key==(True,True,False) and not wrong_outer:
                    wrongsite=next(slot for slot in range(size+1,22) if (truth[path[0]]&truth[path[1]]&1<<slot)==0);order=list(range(22));order[size],order[wrongsite]=order[wrongsite],order[size];assert not clash(standard(rows),path) and not plant(rows,22,path,reorder(truth,order));wrong_outer+=1
    print('PASS C22 planted actual second pair/witness and Q populations',counts,'complete ordered census',host_counts,'wrong internal/exterior witness rejected',wrong,wrong_outer);assert wrong and wrong_outer


if __name__=='__main__':
    if sys.argv[1]=='cal':calibrate()
    else:
        idx=int(sys.argv[2]);parts=SHAPES[idx];rows,cycles=shape(parts);records=roster(parts)
        if sys.argv[1]=='roster':
            for row in records:print(json.dumps(row))
        else:
            live=[r for r in records if not r['reason']];sample=sys.argv[1]=='pilot';live=([live[0],live[-1]] if sample else live[int(sys.argv[3])::int(sys.argv[4])]);
            for row in live:print(json.dumps(dict(shape=idx,**price(rows,tuple(row['path'])))),flush=True)
