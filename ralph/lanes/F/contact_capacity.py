"""Physical calibration and two labelled, unrestricted contacts on a fixed card."""

from argparse import ArgumentParser
from collections import Counter
from itertools import combinations, product
from math import comb
from pathlib import Path

from orbit_extend import independent, independent_sets, parse_graph6, to_graph6


def extend(card, left, right, joined):
    count = len(card)
    return [value | ((left >> site & 1) << count) | ((right >> site & 1) << (count+1))
            for site,value in enumerate(card)] + [left | joined << (count+1), right | joined << count]


def subsets(bits, graph, size):
    return sum(1 for _ in independent_sets(graph,bits,size))


def small():
    total=Counter()
    for count, forbidden in ((3,3),(4,3),(4,4)):
        for mask in range(1<<comb(count,2)):
            card=[0]*count
            for index,(left,right) in enumerate(combinations(range(count),2)):
                if mask>>index & 1:
                    card[left] |= 1<<right;card[right] |= 1<<left
            if any(not independent(value,card) or value.bit_count()>=forbidden for value in card):continue
            full=(1<<count)-1
            counts=[[subsets(full^contacts,card,k) for contacts in range(full+1)] for k in (forbidden,forbidden-1,forbidden-2)]
            for first,second,joined in product(range(full+1),range(full+1),range(2)):
                graph=extend(card,first,second,joined)
                if any(not independent(value,graph) or value.bit_count()>=forbidden for value in graph):continue
                capacities=[min(2-joined,forbidden-1-value.bit_count()) for value in card]
                deficit=missed=0
                for value in card:
                    if value.bit_count()!=forbidden-1:continue
                    deficit+=max(0,2-sum(capacity for vertex,capacity in enumerate(capacities) if value>>vertex & 1))
                    missed+=(not value&first)+(not value&second)
                estimated=counts[0][0]+counts[1][first]+counts[1][second]+(1-joined)*counts[2][first|second]
                physical=sum(not any(graph[left]>>right&1 for left,right in combinations(subset,2)) for subset in combinations(range(count+2),forbidden))
                assert estimated==physical and deficit<=missed and (not missed or physical>0)
                total[count,joined,int(physical==0),int(deficit>0)]+=1
    print('small physical strict/deficit table',sorted(total.items()))
    assert sum(num for (_,_,strict,_),num in total.items() if strict)>0 and sum(num for (_,_,_,bad),num in total.items() if bad)>0


def one(path):
    card=parse_graph6(path.read_text().strip());assert len(card)==38
    active=[index for index,value in enumerate(card) if value.bit_count()==8]
    assert all(value.bit_count() in (8,9) for value in card) and len(active)<=8
    universe=(1<<38)-1; full=(1<<len(active))-1
    physical=[sum(1<<vertex for index,vertex in enumerate(active) if flag>>index&1) for flag in range(full+1)]
    allowed=[independent(mask,card) for mask in physical]
    assert subsets(universe,card,10)==0
    misses={}
    for size in (8,9):
        histogram=[0]*(full+1)
        for subset in independent_sets(card,universe,size):
            key=sum(1<<index for index,vertex in enumerate(active) if subset>>vertex&1)
            histogram[key]+=1
        for index in range(len(active)):
            for flag in range(full+1):
                if flag>>index&1:histogram[flag]+=histogram[flag^(1<<index)]
        misses[size]=[histogram[full^flag] for flag in range(full+1)]
    old_edges=sum(value.bit_count() for value in card)//2; best={}; counts=Counter()
    flip=lambda mask: ((mask&0x5555555555)<<1)|((mask&0xaaaaaaaaaa)>>1)
    for first,second in combinations(range(1,full+1),2):
        if first&second or not (allowed[first] and allowed[second]):continue
        for joined in (0,1):
            degree1,degree2=first.bit_count()+joined,second.bit_count()+joined
            edges=old_edges+degree1+degree2-joined
            if not (4<=min(degree1,degree2)<=max(degree1,degree2)<=9 and 161<=edges<=180):continue
            score=misses[9][first]+misses[9][second]+(1-joined)*misses[8][first|second]
            sym=flip(physical[first])==physical[second]
            for role in (('any',joined),('sym' if sym else 'nonsym',joined)):
                counts[role]+=1
                if role not in best or score<best[role][0]:
                    best[role]=(score,first,second,edges)
    for role,(score,first,second,edges) in sorted(best.items()):
        graph=extend(card,physical[first],physical[second],role[1]);assert all(independent(value,graph) for value in graph) and subsets((1<<40)-1,graph,10)==score
        print(path,role[0],role[1],counts[role],score,edges,to_graph6(graph),flush=True)
    return best


if __name__=='__main__':
    parser=ArgumentParser();parser.add_argument('mode',choices=('small','score'));parser.add_argument('files',type=Path,nargs='*');args=parser.parse_args()
    if args.mode=='small':small()
    else:
        for where in args.files:one(where)
