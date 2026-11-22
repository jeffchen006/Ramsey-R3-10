from collections import Counter
from functools import lru_cache
from itertools import combinations
import json
import sys
import time

from closure22 import ROOT,bits
from m14queue22 import BASE,data
from shadow import decode
from wing19 import index_long
from wing20 import Shore,site_types
from wing20_nextprice import Threshold,limits
from wing21_nextprice import compile_forced,flagged,pack


def literal_forced(poles,support,wing):
    vertices=list(range(poles+len(support)+len(wing)));ys=vertices[poles:poles+len(support)];sites=support+wing;neighbor=[0]*len(vertices)
    for left,right in combinations(vertices,2):
        if right<poles:value=False
        elif left<poles:value=bool(sites[right-poles]>>left&1)
        elif left>=poles+len(support):value=False
        else:value=not(sites[left-poles]&sites[right-poles])
        if value:neighbor[left]|=1<<right;neighbor[right]|=1<<left
    def oversized(fixed,available):
        need=poles+2-fixed
        if need<=0:return True
        while available.bit_count()>=need:
            low=available&-available;available^=low
            if oversized(fixed+1,available&~neighbor[low.bit_length()-1]):return True
        return False
    allvertices=(1<<len(vertices))-1
    assert not oversized(0,allvertices)
    return [(left-poles,right-poles) for left,right in combinations(ys,2) if neighbor[left]>>right&1 and oversized(2,allvertices&~((1<<left)|(1<<right)|neighbor[left]|neighbor[right]))]


def controls():
    count=0;occurrences=0
    for text in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=decode(text)
        if any(row.bit_count()!=6 for row in graph) or max((left&right).bit_count() for left,right in combinations(graph,2))>3:continue
        for first in range(22):
            for second in range(22):
                common=graph[first]&graph[second]
                if common.bit_count()!=1 or graph[first]>>second&1:continue
                middle=common.bit_length()-1;poles=list(bits(graph[middle]&~((1<<first)|(1<<second))));ys=sorted(set(range(22))-{first,second,middle}-set(bits(graph[first]|graph[second]|graph[middle])));wing=list(bits(graph[first]&~common))
                def support(site):return sum(1<<index for index,pole in enumerate(poles) if graph[site]>>pole&1)
                rows=list(map(support,ys));sites=list(map(support,wing));types=[mask for mask in range(1<<len(poles)) if mask.bit_count() in (1,2)];found=flagged(compile_forced(len(poles),rows,types),pack(sites));assert found==literal_forced(len(poles),rows,sites);assert all(graph[ys[left]]>>ys[right]&1 for left,right in found);count+=1;occurrences+=len(found)
    for wing,expected in [([5,6,9,10],[(0,1)]),([5,6,9],[]),([5,5,10,10],[(0,1)])]:assert literal_forced(4,[3,12],wing)==expected
    assert count==250 and occurrences==27;print('All 250 C22 directed missing physical edge tests agree for every signed pair; 27 forced present. Four-bridge, deletion and repeated-site controls pass.')


@lru_cache(None)
def marginal(margins):
    edges=list(combinations(range(7),2));types=site_types(edges,7);side=Shore(edges,margins,sum(margins)-8);return side,Threshold(side.physical,types),[pack([types[index] for index in sites]) for sites in side.physical]


@lru_cache(None)
def index_for(margins):return index_long(marginal(margins)[0].words)


def run(key):
    start=time.process_time();rows,ahits,_=data(key);bhits=ahits if key[0]=='D' else [2]*7 if key[0]=='S' else [2,1]+[2]*5
    edges=list(combinations(range(7),2));types=site_types(edges,7);ypairs=list(combinations(range(14),2));edge_ids={edge:index for index,edge in enumerate(ypairs)};j=[sum(pair&mask==pair for mask in rows) for pair in types[7:]]
    bounds=limits(7,rows,types,8);tests=compile_forced(7,rows,types);left,ltable,lmasks=marginal(tuple(ahits));right,rtable,rmasks=marginal(tuple(bhits));columns=[column[value] for column,value in zip(index_for(tuple(bhits)),j)]
    first=ltable.allowed(bounds);second=rtable.allowed(bounds)
    encode=lambda mask:sum(1<<edge_ids[pair] for pair in flagged(tests,mask))
    lefts={offset:encode(lmasks[offset]) for offset in bits(first)};rights=Counter()
    for offset in bits(second):rights[encode(rmasks[offset])]|=1<<offset
    @lru_cache(None)
    def valid(mask):
        if mask.bit_count()>14:return False
        adjacency=[0]*14
        for number in bits(mask):
            left,right=ypairs[number]
            if adjacency[left]&adjacency[right]:return False
            adjacency[left]|=1<<right;adjacency[right]|=1<<left
        return all(scope.bit_count()<=5-support.bit_count() for scope,support in zip(adjacency,rows))
    @lru_cache(None)
    def allowed(mask):return sum(bunch for other,bunch in rights.items() if valid(mask|other))
    before=after=0
    for offset,mask in lefts.items():
        available=second
        for digit,column in zip(left.words[offset],columns):available&=column[digit]
        before+=available.bit_count();after+=(available&allowed(mask)).bit_count()
    return dict(key=key,short=first.bit_count(),long=second.bit_count(),before=before,after=after,forced_unions=valid.cache_info().currsize,cpu=round(time.process_time()-start,5))


if __name__=='__main__':
    if sys.argv[1]=='cal':controls()
    else:
        for key in sys.argv[1:]:print(json.dumps(run(key)),flush=True)
