"""Named-hole projection: only characters seen by the 45 supports."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import sys

from column_audit import insert, normal, put
from hole_price import support_list, target
from old_indicator import cycle_basis
from orbit_extend import vertices


def localforms(base,hole,order):
    edges={pair:1<<(idx+1) for idx,pair in enumerate(pair for pair in combinations(range(len(base)),2) if base[pair[0]][pair[1]])}
    triangle={}
    for triple in combinations(range(len(base)),3):
        sides=tuple(combinations(triple,2))
        if all(pair in edges for pair in sides):insert(triangle,sum(edges[pair] for pair in sides))
    keys={pair:normal(triangle,bit) for pair,bit in edges.items()}
    forms=[cycle_basis(keys,sites,64) for sites in support_list(base,hole,order)];basis={}
    for flat in forms:
        for form in flat:insert(basis,form)
    pivots=sorted(basis,reverse=True);chart=[basis[pivot] for pivot in pivots];assert len(chart)<=10
    def coords(form):
        word=0
        for idx,pivot in enumerate(pivots):
            if form&pivot:form^=basis[pivot];word|=1<<idx
        assert not form
        return word
    projected=[[coords(form) for form in flat] for flat in forms]
    survivors=[point for point in range(1<<len(chart)) if all(any((point&form).bit_count()%2 for form in flat) for flat in projected)]
    return chart,survivors


def control():
    base=[[int(left==right or (left<4 and right<4 and (left-right)%4 in (1,3))) for right in range(5)] for left in range(5)];base[4][4]=0
    chart,survivors=localforms(base,4,6);assert len(chart)==1 and survivors==[1]
    from hole_price import literal
    from itertools import product
    passes=0
    for signs in product(range(2),repeat=4):
        found,_=literal(base,4,6,signs);assert bool(found)==(sum(signs)%2 not in survivors);passes+=not found
    assert passes==8;print('one projected parity role survives; physical count 8/16')


def inspect():
    base=target();chart,survivors=localforms(base,0,10);assert survivors
    print('local parity dimension',len(chart),'roles',1<<len(chart),'pass 45',len(survivors))
    put('local.chart',chart);put('local.pass',survivors)
    sites=tuple(vertices(245790));assert sites in support_list(base,0,10)
    mask=sum(1<<site for site in (2,14,4,16,3,15));doubled=1
    edges=[pair for pair in combinations(sites,2) if base[pair[0]][pair[1]]];assert len(edges)==8
    pairs={tuple(sorted(pair)) for pair in zip((2,14,4,16,3,15),(14,4,16,3,15,2))};assert pairs<=set(edges)
    assert set(edges)-pairs=={(1,14),(4,17)}
    counts=Counter();example=None
    for row in Path('../r13/col21.rows').read_text().splitlines():
        full,single,size,stage=map(int,row.split());assert stage==3
        if full&~doubled:continue
        cuts=(single&mask)==mask;counts[full,cuts]+=1
        if cuts and example is None:example=row
    print('exactly one hole, necessary F13 single-column footprint roster',sorted(counts.items()),'first rejected',example);assert example


if __name__=='__main__':{'control':control,'inspect':inspect}[sys.argv[1]]()
