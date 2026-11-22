"""One named full hole; affine nonedge signs use bit zero as the constant."""
from collections import Counter
from itertools import combinations, product
from pathlib import Path
import sys

from column_audit import insert, normal, put
from cyclic_check import read_base
from old_indicator import cycle_basis
from orbit_extend import independent_sets, vertices
from relift_audit import explicit_lift


def target():
    source = Path('../r13/max.q').read_text().splitlines()[21]
    assert source == Path('../r14/old21.q').read_text().strip()
    base = read_base(source)
    assert len(base) == 18 and all(base[left][right] == (min((left-right)%18, (right-left)%18) in {0,5,6,8,9}) for left in range(18) for right in range(18))
    base[0][0] = 0
    return base


def edgespace(base):
    edges = {pair: 1 << (index+1) for index, pair in enumerate(pair for pair in combinations(range(len(base)),2) if base[pair[0]][pair[1]])}
    triangles = {}
    for triple in combinations(range(len(base)),3):
        sides = tuple(combinations(triple,2))
        if all(pair in edges for pair in sides):
            insert(triangles, sum(edges[pair] for pair in sides))
    return {pair:normal(triangles, bit) for pair,bit in edges.items()}


def support_list(base, hole, order):
    if base[hole][hole]:return []
    available = [site for site in range(len(base)) if site != hole and not base[hole][site]]
    return list(combinations(available, order-2))


def literal(base,hole,order,signs):
    physical = explicit_lift(base, iter(signs)); prefix = 3 << (2*hole)
    found = set()
    for selected in independent_sets(physical,(1<<(2*len(base)))-1,order):
        if selected & prefix != prefix:continue
        sizes = [(selected>>(2*site)&3).bit_count() for site in range(len(base))]
        if sizes.count(2)==1:found.add(tuple(idx for idx,num in enumerate(sizes) if num==1))
    return found,physical


def control():
    for sign in (0,1):
        base = [[1,0,1],[0,1,0],[1,0,1]]
        for removed in (None,0,1):
            if removed is not None:base[removed][removed]=0
            found,physical=literal(base,1,4,[sign]); eligible=support_list(base,1,4)
            assert found == set(eligible) == ({(0,2)} if removed==1 else set())
            if removed is None:assert not list(independent_sets(physical,63,4))
            if removed==1:
                tens=list(independent_sets(physical,63,4));assert len(tens)==2
                for selected in tens:
                    wrong=selected^3
                    assert wrong not in tens and wrong.bit_count()==4
            if removed is not None:base[removed][removed]=1
    print('C4 + K2, C4 + 2K1: both crossing matchings, 0 -> 2 literal I4s; wrong hole and wrong singleton endpoint rejected')
    base=[[int(left==right or (left<4 and right<4 and (left-right)%4 in (1,3))) for right in range(5)] for left in range(5)];base[4][4]=0
    keys=edgespace(base);sites,=support_list(base,4,6);forms=cycle_basis(keys,sites,10);assert len(forms)==1
    valid=0
    for signs in product(range(2),repeat=4):
        raw=[(left,right) for right in range(5) for left in range(right) if base[left][right]]
        point=sum(keys[pair]*(1-sign) for pair,sign in zip(raw,signs));found,_=literal(base,4,6,signs)
        assert bool(found)==all((form&point).bit_count()%2==0 for form in forms);valid+=bool(found)
    assert valid==8;print('C4 quotient plus isolated hole: exact affine I6 indicator matches 8/16 literal signings')


def project(forms, units):
    reduced={}
    for form in forms:insert(reduced,normal(units,form))
    return None if 1 in reduced else tuple(reduced.values())


def price():
    base=target();keys=edgespace(base);subsets=support_list(base,0,10);assert len(subsets)==45
    rows=[(sum(1<<site for site in sites),cycle_basis(keys,sites,64)) for sites in subsets];assert all(forms is not None for _,forms in rows)
    print('original 45 ranks',dict(sorted(Counter(len(forms) for _,forms in rows).items())))
    units={};path=[]
    while True:
        for mask,forms in rows:
            reduced=project(forms,units)
            if reduced is None or len(reduced)>1:continue
            path.append(mask)
            if not reduced:
                put('hole.trace',path);print('unavoidable full hole; steps',len(path));return
            insert(units,reduced[0]^1);break
        else:break
    put('hole.trace',path)
    print('units',len(units),'residual ranks',dict(Counter(-1 if (flat:=project(forms,units)) is None else len(flat) for _,forms in rows)))
    put('hole.rows',[' '.join(map(str,(mask,*forms))) for mask,forms in rows])


if __name__=='__main__':{'control':control,'price':price}[sys.argv[1]]()
