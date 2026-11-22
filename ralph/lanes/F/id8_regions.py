"""Local (conditioned) parity table for singletons from a set of sites."""
from itertools import combinations, product
from pathlib import Path
from collections import Counter
import sys

from column_audit import insert,normal
from hole_price import edgespace
from hole_branches import establish
from id8_local import target,coordinates
from old_indicator import cycle_basis
from orbit_extend import vertices


def region(keys,sites,order,units):
    free={pair:normal(units,form) for pair,form in keys.items()}
    space={}
    for form in cycle_basis(free,sites,64):insert(space,form&~1)
    chart=sorted(space.values(),key=int.bit_length,reverse=True)
    if len(chart)>12:return len(chart),None,None
    rows=[]
    for support in combinations(sites,order):
        forms=cycle_basis(free,support,64)
        if 1 in forms:continue
        coords=[(coordinates(form&~1,chart),form&1) for form in forms]
        rows.append((sum(1<<site for site in support),coords))
    return len(chart),chart,sorted(rows,key=lambda item:len(item[1]))


def union(dim,rows,stride=1):
    total=1<<dim;allroles=(1<<total)-1;live=allroles
    if stride>1:live=sum(1<<point for point in range(0,total,stride))
    cache={0:0};bits=[(allroles//((1<<(1<<axis))+1))<<(1<<axis) for axis in range(dim)]
    cuts=[]
    for mask,coords in rows:
        event=live
        for word,constant in coords:
            if word not in cache:
                part=0
                for index in vertices(word):part^=bits[index]
                cache[word]=part
            event &= cache[word] if constant else ~cache[word]
            if not event:break
        if event:cuts.append(mask);live^=event
        if not live:break
    return live,cuts


def control():
    from hole_price import literal
    from orbit_extend import independent_sets
    from relift_audit import explicit_lift
    for size in (4,5):
        base=[[int(left==right or abs(left-right) in (1,size-1)) for right in range(size)] for left in range(size)]
        keys=edgespace(base); dim,chart,rows=region(keys,tuple(range(size)),size,{})
        live,cuts=union(dim,rows); assert dim==1
        for signs in product((0,1),repeat=size):
            graph=explicit_lift(base,iter(signs));point=sum(1-sign for sign in signs)%2
            assert bool(live>>point&1)==(not list(independent_sets(graph,(1<<(2*size))-1,size)))
        assert cuts==[(1<<size)-1]
    print('C4/C5 tables checked on all 16/32 physical lifts including odd-cycle nonedge convention')


def main(count,mode):
    base=target(); keys=edgespace(base); chart0=list(map(int,Path('roles.chart').read_text().split())); units={}
    for form in chart0:insert(units,form^1)
    core=[site for site in range(18) if not base[0][site]]
    rest=sorted(set(range(18))-set(core)); assert len(core)==11
    freqs=Counter()
    for idx,added in enumerate(combinations(rest,count)):
        if mode=='pilot' and idx%5:continue
        sites=sorted(core+list(added));dim,chart,rows=region(keys,sites,10,units)
        if rows is None:freqs[dim,'over']+=1;continue
        stride=max(1,(1<<dim)//32) if mode=='pilot' else 1
        live,cuts=union(dim,rows,stride);freqs[dim,bool(live)]+=1
        print(added,'dim',dim,'sample',len(range(0,1<<dim,stride)),'pass',live.bit_count(),'cuts',len(cuts),flush=True)
        if not live and stride==1:
            Path('region.zero').write_text(' '.join(map(str,cuts))+'\n');break
    print('summary',freqs)


if __name__=='__main__':
    if sys.argv[1]=='control':control()
    else:main(int(sys.argv[1]),sys.argv[2])
