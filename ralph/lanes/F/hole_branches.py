"""Deductions in the eleven necessary *local* parity roles. No global sign branches."""
from collections import Counter
from itertools import combinations,product
from pathlib import Path
import sys

from column_audit import insert,normal,put
from hole_joint import polynomial
from hole_local import localforms
from hole_price import target
from old_indicator import cardspace,cycle_basis
from orbit_extend import vertices


def bank(base,order,maxrank):
    keys={pair:bit<<1 for pair,bit in cardspace(base).items()};rows=[]
    for sites in combinations(range(len(base)),order):
        forms=cycle_basis(keys,sites,maxrank)
        if forms is not None:rows.append((sum(1<<site for site in sites),forms))
    return keys,sorted(rows,key=lambda pair:len(pair[1]))


def establish(keys,chart,point):
    units={};byedge=list(keys.values())
    for idx,raw in enumerate(chart):
        form=point>>idx&1
        for pos in vertices(raw>>1):form^=byedge[pos]
        insert(units,form)
    assert len(units)==len(chart) and 1 not in units
    return units


def cut(rows,units):
    steps=[];pending=rows
    while True:
        following=[];change=False
        cache={}
        for mask,flat in pending:
            reduced={}
            for form in flat:
                if form not in cache:cache[form]=normal(units,form)
                insert(reduced,cache[form])
                if 1 in reduced:break
            if 1 in reduced:continue
            if not reduced:return steps+[mask],[],'rank0'
            if len(reduced)==1:
                steps.append(mask);insert(units,next(iter(reduced.values()))^1);cache.clear();change=True
            else:following.append((mask,tuple(reduced.values())))
        pending=following
        if not change:break
    monomials={0:0};basis={};records=[]
    for mask,flat in pending:
        if len(flat)>3:continue
        row=sum(1<<monomials.setdefault(term,len(monomials)) for term in sorted(polynomial(flat)));ref=1<<len(records)
        while row>1 and (pivot:=row.bit_length()-1) in basis:
            other,history=basis[pivot];row^=other;ref^=history
        if row:
            records.append(mask)
            if row==1:return steps,[records[idx] for idx in vertices(ref)],'xor'
            basis[row.bit_length()-1]=row,ref
    return steps,[],'open'


def small():
    from relift_audit import explicit_lift
    from orbit_extend import independent_sets
    for order in (5,6):
        base=[[int(left==right or (left<4 and right<4 and (left-right)%4 in (1,3))) for right in range(6)] for left in range(6)];base[4][4]=0
        chart,points=localforms(base,4,order);keys,rows=bank(base,order,16)
        for point in points:
            steps,proof,state=cut(rows,establish(keys,chart,point))
            passing=0
            for signs in product(range(2),repeat=4):
                edges=[(left,right) for right in range(6) for left in range(right) if base[left][right]];raw=sum((1-signs[edges.index(pair)])<<(idx+1) for idx,pair in enumerate(keys))
                if any(((raw&form).bit_count()%2)!=(point>>idx&1) for idx,form in enumerate(chart)):continue
                graph=explicit_lift(base,iter(signs));passing+=not list(independent_sets(graph,(1<<12)-1,order))
            assert not passing or state=='open'
        print('six sites small order',order,'local point count',len(points))
    # Independent four-cycle parity obstruction vs an actual no-transversal role.
    base=[[int(left==right or (left-right)%4 in (1,3)) for right in range(4)] for left in range(4)]
    keys,rows=bank(base,4,16);raw=sum(1<<(idx+1) for idx in range(4));
    for point in (0,1):
        steps,_,state=cut(rows,establish(keys,[raw],point));assert state==('open' if point else 'rank0')
    print('pinned C4 on four sites: even parity rank-zero, odd parity retained')


def run(rank,limit,restored=False):
    base=target();chart,points=localforms(base,0,10);assert list(map(int,Path('local.pass').read_text().split()))==points and len(points)==11
    keys,rows=bank(base,10,rank);print('bank by original cycle-rank',dict(Counter(len(flat) for _,flat in rows)))
    if restored:points=sorted(set(range(1<<len(chart)))-set(points))
    for number in range(min(limit,len(points))):
        steps,proof,state=cut(rows,establish(keys,chart,points[number]));print(number,points[number],state,len(steps),len(proof),flush=True)
        name=f'restored{rank}.{points[number]}' if restored else f'branch{rank}.{number}'
        put(name+'.proof',[f'{state} {points[number]}',' '.join(map(str,steps)),' '.join(map(str,proof))])


if __name__=='__main__':
    if sys.argv[1]=='small':small()
    elif sys.argv[1]=='restored':run(*map(int,sys.argv[2:]),restored=True)
    else:run(*map(int,sys.argv[1:]))
