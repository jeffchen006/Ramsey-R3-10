"""Enumerate the tiny switching space of an OLD card; no four-pole completion."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import sys

from cyclic_check import read_base
from four_slot import put
from orbit_extend import independent,independent_sets,to_graph6
from relift_audit import explicit_lift


def old_models(text):
    base=read_base(text);size=len(base)
    singles=[(left,right) for right in range(size) for left in range(right) if base[left][right]==1]
    bits={edge:1<<idx for idx,edge in enumerate(singles)}
    roots=list(range(size));relations=[]
    def root(site):
        while site!=roots[site]:site=roots[site]
        return site
    for left,right in singles:
        if root(left)!=root(right):roots[root(left)]=root(right);relations.append(bits[left,right])
    for triple in combinations(range(size),3):
        edges=list(combinations(triple,2))
        if all(pair in bits for pair in edges):relations.append(sum(bits[pair] for pair in edges))
    pivots={}
    for row in relations:
        while row and row.bit_length()-1 in pivots:row^=pivots[row.bit_length()-1]
        if row:pivots[row.bit_length()-1]=row
    free=[idx for idx in range(len(bits)) if idx not in pivots];assert len(free)<=5
    for assignment in range(1<<len(free)):
        point=sum(1<<idx for pos,idx in enumerate(free) if assignment>>pos&1)
        for idx,row in sorted(pivots.items()):point|=((point&row).bit_count()%2)<<idx
        assert all(not ((point&row).bit_count()%2) for row in relations)
        graph=explicit_lift(base,iter(1-(point>>idx&1) for idx in range(len(bits))))
        assert all(independent(row,graph) for row in graph)
        yield point,graph


def run(name,target,maxcol,limit):
    text=Path(name+'.q').read_text().strip();out=[];stricts=[]
    for number,(point,graph) in enumerate(old_models(text)):
        if number>=limit:break
        allmask=(1<<len(graph))-1;bad=next(independent_sets(graph,allmask,target),None)
        if bad:
            out.append(f'{number} {point} I{target} {bad}');continue
        stricts.append(to_graph6(graph));constraints=list(independent_sets(graph,allmask,target-1));counts=Counter();solutions=[]
        for size in range(1,maxcol+1):
            for mask in independent_sets(graph,allmask,size):
                if all(mask&other for other in constraints):counts[size]+=1;solutions.append(mask)
        out.append(f'{number} {point} strict {len(constraints)} clean {sorted(counts.items())}');put(f'{name}.old{number}.cols',solutions)
    put(name+'.models',out);put(name+'.strict.g6',stricts);print('\n'.join(out))


if __name__=='__main__':run(sys.argv[1],*map(int,sys.argv[2:]))
