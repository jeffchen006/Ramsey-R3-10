"""Validate multiplicity and averaging against physical smaller signings."""

from itertools import combinations,product
from math import comb

from card_replay import ceildiv, lines, minimum_occupied, read_base, restrictions
from orbit_extend import independent_sets
from relift_audit import explicit_lift
from odd_check import verify


def run():
    text,=lines('small.q');base=read_base(text);target=3;size=len(base)
    cores=lines('small.core.q');floors=list(map(int,lines('small.core.exact')))
    occupied=minimum_occupied(base,target)
    totals={};examples=0;pairs=tuple(combinations(range(size),2))
    for signs in product(range(2),repeat=5):
        graph=explicit_lift(base,iter(signs));sets=list(independent_sets(graph,1023,target))
        masks=[sum(1<<vertex for vertex in range(size) if support&(3<<(2*vertex))) for support in sets]
        assert min(mask.bit_count() for mask in masks)>=occupied
        assert all(any(((mask >> index)&1) != ((mask >> ((index+1)%size))&1) for index in range(size)) for mask in masks)
        assert len(sets)>=ceildiv(size*sum(floors),comb(size-occupied,2))
        for shift in range(size):
            restricted=sum(not(mask>>shift)&1 for mask in masks)
            assert restricted>=ceildiv(2*sum(floors),size-1-occupied)
        for left,right in pairs:
            holes=(1<<left)|(1<<right)
            physical=1023^((3<<(2*left)) | (3<<(2*right)))
            physical_count=sum(1 for _ in independent_sets(graph,physical,target))
            assert physical_count==sum(not(mask&holes) for mask in masks)
            distance=min(right-left,size-right+left)
            assert physical_count>=floors[distance-1]
            totals[distance]=min(physical_count,totals.get(distance,10**9))
        for mask in masks:
            count=sum(not(mask & ((1<<left)|(1<<right))) for left,right in pairs)
            assert count==comb(size-mask.bit_count(),2)
        examples+=len(masks)
    assert list(totals[distance] for distance in (1,2))==floors
    print('all 32 signings;',examples,'physical independent sets rechecked; min occupied',occupied,'exact two-hole floors',floors)
    assert read_base(cores[0])!=restrictions(base,{0,2})
    text=lines('card.core.q')[216];_,*tokens=lines('card.core.odd')[216].split();assert verify(text,10,tokens)==8
    first,*rest=tokens;header,*terms=first.split(':')
    for mutation in (['C999:'+':'.join(terms)]+rest,['C1:0,0']+rest,[header+':'+':'.join(terms+[terms[0]])]+rest):
        try:verify(text,10,mutation)
        except AssertionError:continue
        raise AssertionError('mutant accepted')
    print('wrong-hole matrix unequal, inflated capacity / weight-zero support / duplicate-support mutations rejected')


if __name__=='__main__':
    assert __debug__
    run()
