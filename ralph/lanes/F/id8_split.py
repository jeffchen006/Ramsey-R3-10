"""Split one local singleton chart after deduced hole equations, not global signings."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import sys
from time import perf_counter

from column_audit import normal,insert
from hole_branches import cut
from id8_marks import constraints,occupied,witness
from id8_local import target
from old_indicator import cardspace,cycle_basis
from orbit_extend import vertices


def setup(holes,width):
    base=target();keys={pair:form<<1 for pair,form in cardspace(base).items()};chart0=list(map(int,Path('roles.chart').read_text().split()));pins=constraints(keys,holes,chart0)
    for idx in range(18):base[idx][idx]=int(idx not in holes)
    keys={pair:normal(pins,form) for pair,form in keys.items()};rows=[];required=[];candidates=[]
    for full,sites in occupied(base,holes):
        code=(sum(1<<site for site in full)<<18)+sum(1<<site for site in sites);flat=cycle_basis(keys,sites,64)
        if len(full)==1:required.append(code)
        if 1 not in flat:rows.append((code,flat))
    for sites in combinations(range(18),10):
        flat=cycle_basis(keys,sites,9)
        if flat is None or 1 in flat:continue
        mask=sum(1<<site for site in sites);rows.append((mask,flat))
        if len(flat)==width:candidates.append((mask,flat))
    rows.sort(key=lambda item:len(item[1])); assert candidates
    best=-1
    for mask,flat in candidates[::max(1,len(candidates)//16)]:
        room={}
        for form in flat:insert(room,form&~1)
        score=0
        for code,other in rows:
            if len(other)>3:break
            reduced={}
            for form in other:insert(reduced,normal(room,form&~1))
            score+= (8,2,0,0)[len(reduced)]
        if score>best:best=score; selected=mask,[form&~1 for form in flat]
    return base,required,rows,selected


def main(holes,width,mode):
    base,required,rows,(mask,chart)=setup(holes,width);total=1<<len(chart);step=max(1,total//8) if mode=='pilot' else 1; start=perf_counter(); hist=Counter();selected=set(required)
    print('chart sites',tuple(vertices(mask)),'conditional rank',len(chart),'bank',len(rows),flush=True)
    for point in range(0,total,step):
        units={}
        for index,form in enumerate(chart):insert(units,form^(point>>index&1))
        steps,extra,state=cut(rows,units);hist[state]+=1; selected.update(steps+extra)
        if mode=='pilot' or state=='open':print('role',point,state,len(steps),len(extra),flush=True)
    print('sample',sum(hist.values()),'hist',hist,'projected time',round((perf_counter()-start)*step,3),'support union',len(selected),flush=True)
    if step==1 and 'open' not in hist:witness(base,Path('split'+'-'.join(map(str,holes))),selected)


if __name__=='__main__':main(tuple(map(int,sys.argv[1].split(','))),int(sys.argv[2]),sys.argv[3])
