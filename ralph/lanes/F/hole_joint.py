"""Bounded constant-coefficient indicators with one named old hole."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import sys

from column_audit import insert, normal, put
from hole_price import project, support_list, target
from old_indicator import cardspace, cycle_basis
from orbit_extend import vertices


def polynomial(forms):
    terms={0}
    for form in forms:
        following=set() if form&1 else terms.copy()
        for position in vertices(form>>1):
            for term in terms:following.symmetric_difference_update({term | 1<<position})
        terms=following
    return terms


def price(stride):
    base=target(); keys={pair:bit<<1 for pair,bit in cardspace(base).items()}
    required=list(map(int,Path('hole.trace').read_text().split()));assert len(required)==1
    sites=tuple(vertices(required[0])); assert sites in support_list(base,0,10)
    unit,=cycle_basis(keys,sites,10);units={};insert(units,unit^1)
    keys={pair:normal(units,form) for pair,form in keys.items()}
    inputs=[(1,sites) for sites in support_list(base,0,10)]+[(0,sites) for idx,sites in enumerate(combinations(range(18),10)) if idx%stride==0]
    monoms={0:0};basis={};refs={};records=[];stats=Counter();visited=Counter();unique=set()
    for hole,sites in inputs:
        visited[hole]+=1;forms=cycle_basis(keys,sites,5)
        if forms is None or 1 in forms or len(forms)>4:continue
        assert 1 not in forms
        terms=polynomial(forms)
        if not terms:continue
        row=sum(1<<monoms.setdefault(term,len(monoms)) for term in sorted(terms));stats[hole,len(forms)]+=1
        if row in unique:continue
        unique.add(row);ref=1<<len(records)
        while row>1 and (pivot:=row.bit_length()-1) in basis:row^=basis[pivot];ref^=refs[pivot]
        if row:
            records.append((hole,sum(1<<site for site in sites)))
            if row==1:
                chosen=[records[idx] for idx in vertices(ref)];put(f'joint{stride}.witness',[f'{hole} {mask}' for hole,mask in chosen]);print('constant one',len(chosen));break
            pivot=row.bit_length()-1;basis[pivot]=row;refs[pivot]=ref
    else:put(f'joint{stride}.witness',[]);print('no constant one')
    print('visited(hole,old)',visited[1],visited[0],'nonempty by role/rank',sorted(stats.items()),'distinct',len(unique),'span',len(basis),'monomials',len(monoms))


if __name__=='__main__':price(int(sys.argv[1]))
