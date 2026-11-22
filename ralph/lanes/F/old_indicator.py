"""Low-degree Boolean identities for an unsigned old card. No signing branches."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import sys

from column_audit import insert,normal,put
from cyclic_check import read_base
from orbit_extend import independent_sets,vertices
from relift_audit import encode,explicit_lift


def multiply(factors):
    result={0}
    for form in factors:
        following=result.copy()
        for position in vertices(form):
            bit=1<<position
            for term in result:
                product=term|bit
                if product in following:following.remove(product)
                else:following.add(product)
        result=following
    return result


def cardspace(base):
    size=len(base);keys={(left,right):0 for left,right in combinations(range(size),2) if base[left][right]};keys={pair:1<<idx for idx,pair in enumerate(keys)};relations={};parents=list(range(size))
    def root(site):
        while site!=parents[site]:site=parents[site]
        return site
    for (left,right),form in keys.items():
        if root(left)!=root(right):parents[root(left)]=root(right);insert(relations,form)
    for triple in combinations(range(size),3):
        sides=list(combinations(triple,2))
        if all(edge in keys for edge in sides):insert(relations,sum(keys[edge] for edge in sides))
    return {pair:normal(relations,form) for pair,form in keys.items()}


def cycle_basis(keys,sites,degree):
    parents={site:(site,0) for site in sites};basis={}
    def find(site):
        parity=0
        while True:
            other,edge=parents[site];parity^=edge
            if site==other:return site,parity
            site=other
    for pair in combinations(sites,2):
        if pair not in keys:continue
        left,right=pair;first,offset=find(left);second,other=find(right);row=offset^other^keys[pair]
        if first!=second:parents[first]=second,row
        else:
            insert(basis,row)
            if len(basis)>degree:return None
    return tuple(basis.values())


def seek(source,order,degree,stride,prefix):
    base=read_base(Path(source).read_text().strip());keys=cardspace(base);monomials={0:0};basis={};receipts=[];hist=Counter();visited=0;dedup=set()
    for index,selected in enumerate(combinations(range(len(base)),order)):
        if index%stride:continue
        visited+=1;flat=cycle_basis(keys,selected,degree)
        if flat is None:continue
        hist[len(flat)]+=1;poly=multiply(flat);row=0
        for term in sorted(poly):row|=1<<monomials.setdefault(term,len(monomials))
        if row in dedup:continue
        dedup.add(row);mask=sum(1<<site for site in selected);relation=1<<len(receipts)
        while row>1:
            pivot=row.bit_length()-1
            if pivot not in basis:basis[pivot]=row,relation;receipts.append(mask);break
            prior,preimage=basis[pivot];row^=prior;relation^=preimage
        if row==1:
            receipts.append(mask);answer=[receipts[position] for position in vertices(relation)];put(prefix+'.witness',answer);print('conflict',len(answer));break
    else:put(prefix+'.witness',[]);print('no identity in test')
    print(prefix,'visited',visited,'cycle rank',dict(hist),'equations',len(dedup),'span',len(basis),'monomials',len(monomials))


def independent_check(source,order,prefix):
    base=read_base(Path(source).read_text().strip());size=len(base);keys={(left,right):0 for right in range(size) for left in range(right) if base[left][right]};keys={edge:1<<idx for idx,edge in enumerate(keys)};triangle={}
    for triple in combinations(range(size),3):
        edges=list(combinations(triple,2))
        if all(edge in keys for edge in edges):insert(triangle,sum(keys[edge] for edge in edges))
    result=set();counts=Counter();masks=list(map(int,Path(prefix+'.witness').read_text().split()));assert masks
    for mask in masks:
        sites=list(vertices(mask));assert len(sites)==order and max(sites)<size;full={};flat={}
        for left,right in combinations(sites,2):
            if (left,right) in keys:insert(full,(1<<(64+left))^(1<<(64+right))^keys[left,right])
        for pivot,row in full.items():
            if pivot<1<<64:insert(flat,normal(triangle,row))
        factors=[(0,)+tuple(1<<idx for idx in vertices(value)) for value in flat.values()];counts[len(factors)]+=1
        from itertools import product
        for choices in product(*factors):
            term=0
            for variable in choices:term|=variable
            result.symmetric_difference_update({term})
    assert result=={0};print('ungauged original-edge XOR to 1:',prefix,len(masks),'supports',dict(counts))


def biclique(size):
    base=[[int(left==right or (left<2)!=(right<2)) for right in range(size)] for left in range(size)]
    keys=cardspace(base);flat=cycle_basis(keys,tuple(range(size)),size-3);assert len(flat)==size-3
    byedge=[pair for right in range(size) for pair in ((left,right) for left in range(right)) if pair in keys];positive=0
    for flags in range(1<<len(byedge)):
        signs={(left,right):int(flags>>index&1) for index,(left,right) in enumerate(byedge)};sw=[None]*size;sw[0]=0
        for site in range(2,size):sw[site]=signs[0,site]
        sw[1]=signs[1,2]^sw[2];point=sum((signs[left,right]^sw[left]^sw[right])<<idx for idx,(left,right) in enumerate(keys))
        graph=explicit_lift(base,iter(1-signs[pair] for pair in byedge));strict=next(independent_sets(graph,(1<<(2*size))-1,size),None) is None
        assert strict==any((form&point).bit_count()%2 for form in flat);positive+=strict
    assert positive==(1<<len(keys))-(1<<(size-1));print('K2,%s calibration: %s/%s strict, rank %s agrees pointwise'%(size-2,positive,1<<len(byedge),size-3))


def small():
    biclique(6);biclique(7)
    path=[[int(abs(left-right)<=1) for right in range(6)] for left in range(6)];put('oldpath.q',[encode(path)]);seek('oldpath.q',5,3,1,'oldpath');independent_check('oldpath.q',5,'oldpath')


if __name__=='__main__':
    if sys.argv[1]=='small':small()
    elif sys.argv[1]=='check':independent_check(sys.argv[2],int(sys.argv[3]),sys.argv[4])
    else:seek(sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),int(sys.argv[5]),sys.argv[6])
