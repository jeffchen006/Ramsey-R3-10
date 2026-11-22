from collections import Counter
from functools import lru_cache
from itertools import combinations,combinations_with_replacement
import json
from math import factorial,prod
from pathlib import Path

import pynauty

ROOT=Path(__file__).resolve().parents[3]
SOURCE=ROOT/'scratch/D/m14r22'


def signature(degrees,first,second):
    return min(tuple(sorted((degree,(left>>site)&1,(right>>site)&1) for site,degree in enumerate(degrees))) for left,right in [(first,second),(second,first)])


def coefficient(shape):
    required=tuple(degree-left-right for degree,left,right in shape);size=len(shape)
    capacities=[2-shape[left][1]*shape[right][1]-shape[left][2]*shape[right][2] for left,right in combinations(range(size),2)]
    edges=list(combinations(range(size),2))
    @lru_cache(None)
    def count(index,rest):
        if index==len(edges):return int(not any(rest))
        left,right=edges[index]
        if any(rest[:left]):return 0
        result=0
        for exponent in range(min(rest[left],rest[right],capacities[index])+1):
            updated=list(rest);updated[left]-=exponent;updated[right]-=exponent;result+=count(index+1,tuple(updated))
        return result
    return count(0,required)


def check_hall(masks):
    later=[sum(1<<right for right in range(left+1,len(masks)) if masks[left]&masks[right]) for left in range(len(masks))]
    def visit(available,number,union):
        if number>union.bit_count():return False
        while available:
            low=available&-available;site=low.bit_length()-1;available-=low
            if not visit(available&later[site],number+1,union|masks[site]):return False
        return True
    return visit((1<<len(masks))-1,0,0)


def audit():
    totals=Counter();keys=set();weights=Counter();groups={'one':(6,4,4,4,4,4,4),'two':(5,5,4,4,4,4,4)}
    doubles=[sum(1<<site for site in pair) for pair in combinations(range(7),2)]
    triples=[sum(1<<site for site in triple) for triple in combinations(range(7),3)]
    for line in (SOURCE/'roster.jsonl').read_text().splitlines():
        record=json.loads(line);degrees=groups[record['kind']];first,second=record['triples'];masks=[first,second]+[mask for mask,multi in zip(doubles,record['pairs']) for _ in range(multi)]
        assert len(masks)==14 and first in triples and second in triples and first<=second
        assert tuple(sum(mask>>pole&1 for mask in masks) for pole in range(7))==degrees
        assert max(sum(mask&pair==pair for mask in masks) for pair in doubles)<=2
        adj={site:[] for site in range(21)}
        for offset,mask in enumerate(masks,7):
            for pole in range(7):
                if mask>>pole&1:adj[offset].append(pole);adj[pole].append(offset)
        special={site for site,degree in enumerate(degrees) if degree>4};colors=[special,set(range(7))-special,set(range(7,21))]
        graph=pynauty.Graph(21,adjacency_dict=adj,vertex_coloring=colors);key=(record['kind'],pynauty.certificate(graph));assert key not in keys;keys.add(key)
        group=pynauty.autgrp(graph);aut=int(group[1])*10**group[2];kernel=prod(factorial(count) for count in Counter(masks).values());assert aut==record['aut']*kernel
        order=factorial(len(special))*factorial(7-len(special));assert record['weight']*record['aut']==order
        passed=check_hall(masks);assert passed== (not record['hall']);witness=record['hall']
        if witness:
            assert not (Counter(witness)-Counter(masks)) and all(left&right for left,right in combinations(witness,2));union=0
            for mask in witness:union|=mask
            assert union.bit_count()<len(witness)
        totals[record['kind'],passed]+=1;weights[signature(degrees,first,second)]+=record['weight']
    multiplicities=Counter(signature(degrees,first,second) for degrees in groups.values() for first,second in combinations_with_replacement(triples,2))
    for shape,multi in multiplicities.items():assert weights[shape]==multi*coefficient(shape)
    print('Independent colored-nauty unique reps, stabilizers, literal clique-Hall tests, exhaustive labelled coefficient fibers:',len(keys),len(multiplicities),sum(weights.values()),dict(totals))


if __name__=='__main__':audit()
