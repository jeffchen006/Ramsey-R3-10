"""Exact independence-mask relaxation on each physical wing pair; join by disjoint pools."""
import argparse
from itertools import combinations
from pathlib import Path
from time import process_time
import json
import numpy as np

from book_controls import bitset,book,sites
from book_seedpack import upper
from book_packing import subsets


def seeds(may):
    full=(1<<len(may))-1;result=[]
    def visit(seed,available,free):
        result.append((seed,free))
        while available:
            site=available&-available;available^=site;point=site.bit_length()-1
            visit(seed|site,available&~may[point],free&~(site|may[point]))
    visit(0,full,full);return result


def local(frame,side,roster,pool):
    fixed,*rows=frame;degree=rows[0].bit_count();points=list(sites(pool));size=1<<len(points);states=np.arange(size,dtype=np.int32);counts=np.fromiter((word.bit_count() for word in range(size)),dtype=np.int8,count=size)
    def pack(word):return bitset(idx for idx,point in enumerate(points) if word>>point&1)
    cuts={}
    for seed,free in roster:
        mask=pack(free);bound=degree-seed.bit_count()
        if mask.bit_count()>bound and (mask not in cuts or bound<cuts[mask]):cuts[mask]=bound
    live=np.ones(size,dtype=bool)
    for mask,bound in cuts.items():live &= counts[states&mask]<=bound
    for left,right in combinations(points,2):
        if rows[left]>>right&1:
            pair=pack(1<<left|1<<right);live &= states&pair!=pair
    maxis=np.where(live,counts,-1)
    for bit in range(len(points)):
        stride=1<<bit;view=maxis.reshape(-1,2*stride);np.maximum(view[:,:stride],view[:,stride:],out=view[:,stride:]);
    return lambda word:word.bit_count()-int(maxis[pack(word)])


def quotas(frame):
    fixed,*rows=frame;books=[book(rows,ends) for ends in ((0,1),(2,3))];core=bitset([point for path,_ in books for point in path]);pools=[bitset((*left,*right))&~core for _,(left,right) in books];roster=seeds(upper(frame));bounds=[local(frame,idx,roster,pools[idx]) for idx in range(2)];common=pools[0]&pools[1];found={}
    for keep in subsets(common):
        first=pools[0]&~(common^keep);second=pools[1]&~keep;found[bounds[0](first),bounds[1](second)]=[first,second]
    return [{'ranks':[x,y],'pools':found[x,y]} for x,y in sorted(found) if not any((a>x or b>y) and a>=x and b>=y for a,b in found)]


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('input',type=Path);args=parser.parse_args()
    for key,frame,truth in map(json.loads,args.input.read_text().splitlines()):
        start=process_time();front=quotas(frame);print(json.dumps(dict(id=key,front=front,cpu=process_time()-start),separators=(',',':')),flush=True)
