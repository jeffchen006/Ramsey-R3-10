"""Bound petal packing in the two actual matchings by their degree-two conflict components."""
from functools import lru_cache
from itertools import combinations
import json
from pathlib import Path
import sys
from book_controls import bitset,book,sites


@lru_cache(None)
def components(left,right):
    types=[]
    for length in range(1,left+right+1):
        for first in range(1+(length%2)):
            groups=[(idx+first)%2 for idx in range(length)];counts=(groups.count(0),groups.count(1))
            if counts[0]>left or counts[1]>right:continue
            variants=[False,True] if length==6 else [False]
            for cycle in variants:
                frontier=set()
                for mask in range(1<<length):
                    if mask&(mask>>1) or cycle and mask&1 and mask>>(length-1)&1:continue
                    ranks=tuple(sum((mask>>idx)&1 for idx,side in enumerate(groups) if side==block) for block in range(2));frontier.add(ranks)
                maximal=tuple(sorted((a,b) for a,b in frontier if (a+1,b) not in frontier and (a,b+1) not in frontier))
                types.append((*counts,length-1+cycle,cycle,maximal))
    return tuple(types)


@lru_cache(None)
def bounds(left,right,edges,cycles):
    types=components(left,right);records=[]
    def walk(start,need_left,need_right,budget,hexes,chosen,frontier):
        if need_left+need_right==0:
            records.append((chosen,frontier));return
        for pos in range(start,len(types)):
            lhs,rhs,cost,cycle,options=types[pos]
            if lhs>need_left or rhs>need_right or cost>budget or cycle>hexes:continue
            ways={(a+x,b+y) for a,b in frontier for x,y in options}
            front=tuple(sorted((a,b) for a,b in ways if not any((x>a or y>b) and x>=a and y>=b for x,y in ways)))
            walk(pos,need_left-lhs,need_right-rhs,budget-cost,hexes-cycle,(*chosen,pos),front)
    walk(0,left,right,edges,cycles,(),((0,0),))
    return records


def profile(frame):
    fixed,*rows=frame;degree=rows[0].bit_count();books=[book(rows,ends)for ends in ((0,1),(2,3))];paths=[bitset(path)for path,_ in books];wings=[[bitset(group) for group in groups] for _,groups in books];pools=[left|right for left,right in wings];marked=paths[0]|paths[1];shared=pools[0]&pools[1]&~marked;cross=[(a,b) for a in (0,1) for b in (2,3) if rows[a]>>b&1];hexes=sum(all((wings[0][idx]&wings[1][idx^flip]&~marked).bit_count()>=3 for idx in range(2)) for flip in range(2));sizes=[degree-1-(pool&paths[1-side]).bit_count() for side,pool in enumerate(pools)]
    budget=shared.bit_count()-2*(len(cross)==2)
    return sizes,budget,hexes


def compute(frame):
    sizes,budget,hexes=profile(frame);records=bounds(*sizes,budget,hexes);ranks={}
    for quota in range(min(sizes)+1):
        bound=min(max((b for a,b in front if a>=quota),default=-1) for _,front in records);ranks[quota]=bound
    return dict(sizes=sizes,overlap=budget,hexes=hexes,ranks=ranks,checked=len(records))


if __name__=='__main__':
    for key,frame,truth in map(json.loads,Path(sys.argv[1]).read_text().splitlines()):
        row=compute(frame);row['id']=key;print(json.dumps(row,separators=(',',':')),flush=True)
