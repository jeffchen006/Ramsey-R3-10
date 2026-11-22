"""Rebind the actual ID 15 and all small footprints, independent of the C++ footprint producer."""
from collections import Counter
from itertools import combinations
from pathlib import Path

from column_audit import orbit,parse_request,put,replay
from column_quadratic import fix_space,verifyflat
from cyclic_check import read_base
from odd_check import verify
from orbit_extend import vertices


def bind():
    source=Path('target.q').read_text().strip();assert source==Path('../r13/max.q').read_text().splitlines()[15];base=read_base(source);size=len(base);assert size==18
    for left in range(size):
        for right in range(size):assert base[left][right]==(min((left-right)%size,(right-left)%size) in (0,5,7,8,9))
    position=Path('../r13/holes.map').read_text().splitlines().index('15 1');punctured=Path('../r13/holes.q').read_text().splitlines()[position];card=read_base(punctured)
    assert all(card[left][right]==(0 if left==right==0 else base[left][right]) for left in range(size) for right in range(size))
    ident,*words=Path('../r13/holes.odd').read_text().splitlines()[position].split();assert int(ident)==position and verify(punctured,10,words)>=1
    full=(1<<size)-1;neighbors=[sum(1<<right for right in range(size) if left!=right and base[left][right]) for left in range(size)]
    arcs=sorted(orbit(511));assert len(arcs)==18 and verify(source,9,[f'U1:0,{arc}' for arc in arcs])==18
    def component(mask):
        if not mask:return 0
        reached=mask&-mask
        while True:
            expanded=reached
            for site in vertices(reached):expanded|=neighbors[site]&mask
            if expanded==reached:return expanded
            reached=expanded
    blockers={}
    for arc in arcs:
        unseen=arc;parts=[]
        while unseen:
            part=component(unseen);parts.append(part);unseen^=part
        blockers[arc]={mask for mask in (sum(1<<site for site in selected) for count in range(10) for selected in combinations(vertices(arc),count)) if all(component(mask&part)==mask&part for part in parts)}
    kept=[];hist=Counter()
    for mask in range(1<<size):
        count=mask.bit_count()
        if count>7:continue
        if any(mask&arc in blockers[arc] for arc in arcs):hist['arc']+=1;continue
        weak=[site for site in vertices(full^mask) if (neighbors[site]&mask).bit_count()<=1]
        if any(all(not base[left][right] for left,right in combinations(bonus,2)) for bonus in combinations(weak,9-count)):hist['mate']+=1;continue
        kept.append(mask)
    assert len(kept)==693 and Counter(map(int.bit_count,kept))=={6:99,7:594}
    requests=[parse_request(line) for line in Path('single.request').read_text().splitlines()];names={}
    for name,edges,feet,tops in requests:
        assert name==str(feet[0]) and len(feet)==1 and not edges and tops==[0] and min(orbit(feet[0]))==feet[0];names[name]=orbit(feet[0])
    assert len(names)==len(requests)==25 and sum(map(len,names.values()))==len(kept) and set.union(*names.values())==set(kept)
    replay('target.q',10,'single.request','single.trace');statuses={name:status for name,_,status,_ in (row.split() for row in Path('single.trace').read_text().splitlines() if ' end ' in row)};assert names.keys()==statuses.keys() and [name for name,status in statuses.items() if status!='I']==['37449']
    assert Path('qsingle.request').read_text().strip()=='37449 1 0 37449 0';replay('target.q',10,'qsingle.request','qsingle.trace');unit=[int(row.split()[-1]) for row in Path('qsingle.trace').read_text().splitlines() if ' step ' in row];keys,space=fix_space(base,[37449],[0],unit)
    forms=[row.split() for row in Path('qsingle.flat').read_text().splitlines()];name,*indices=Path('qsingle.xor').read_text().split();assert name=='37449' and len(indices)==len(set(indices))==54
    combined=set();selected=Counter()
    for raw in indices:
        tag,*tokens=forms[int(raw)];assert tag==name;poles,sites,first,second=map(int,tokens);verifyflat((keys,space),10,[37449],[0],0,(poles,sites,first,second));selected[poles]+=1
        for left in vertices(first^1):
            for right in vertices(second^1):
                key=tuple(sorted({left,right}-{0}));combined.symmetric_difference_update({key})
    assert combined=={()};print('single hole bound',words,'18 universally balanced arcs; direct component-wise footprint rejection',hist,'pass',Counter(map(int.bit_count,kept)))
    print('D18 reps',Counter(len(group) for group in names.values()),'linear eliminates 690; last three',sorted(names[name]),'by',len(unit),'linear exclusions + 54 quadratics XOR 1; selected old-only / one-pole:',selected)


if __name__=='__main__':bind()
