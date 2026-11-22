"""Boolean polynomial multiples at bounded degree, retaining only physical support IDs."""
from itertools import combinations
from collections import Counter
from pathlib import Path
import sys,time
from column_audit import normal,insert
from hole_branches import cut
from hole_joint import polynomial
from id8_split import setup
from id8_marks import witness
from orbit_extend import vertices


def span(rows,degree):
    allvars=0
    for _,terms in rows:
        for term in terms:allvars|=term
    axes=tuple(1<<idx for idx in vertices(allvars));basis={};monoms={0:0};history=[]
    for mask,terms in sorted(rows,key=lambda row:max(t.bit_count() for t in row[1])):
        order=max(term.bit_count() for term in terms)
        for width in range(degree-order+1):
            for seq in combinations(axes,width):
                factor=sum(seq);row=0
                for term in terms:row^=1<<monoms.setdefault(term|factor,len(monoms))
                identifier=len(history);depend=1<<identifier
                while row>1 and row.bit_length() in basis:
                    other,track=basis[row.bit_length()];row^=other;depend^=track
                if row:
                    history.append(mask)
                    if row==1:return sorted({history[idx] for idx in vertices(depend)})
                    basis[row.bit_length()]=row,depend
    return []


def more(rows,units,degree):
    cache={};seen=set();polys=[]
    for mask,flat in rows:
        basis={}
        for form in flat:
            if form not in cache:cache[form]=normal(units,form)
            insert(basis,cache[form]);
            if 1 in basis or len(basis)>degree:break
        if 1 in basis or len(basis)>degree:continue
        terms=frozenset(polynomial(basis.values()))
        if terms and terms not in seen:seen.add(terms);polys.append((mask,terms))
    return span(polys,degree)


def control():
    rows=[(7,{0,1}), (9,{2}), (11,{1,3})];assert not span(rows,1) and set(span(rows,2))=={7,9,11}
    assert not span(rows[:-1],3); print('three Boolean equations: constant-only insufficient; degree-two multiples prove conflict; dropping obligation restores feasibility')


def run(holes,degree,mode):
    base,required,rows,(mask,chart)=setup(holes,6); selected=set(required);hist=Counter();points=[5,9,13,37,53,63] if mode=='pilot' else range(64); clock=time.perf_counter()
    for point in points:
        units={}
        for idx,form in enumerate(chart):insert(units,form^(point>>idx&1))
        steps,extra,state=cut(rows,units);selected.update(steps+extra)
        if state=='open':
            extra=more(rows,units,degree);selected.update(extra);state='multiples' if extra else 'open'
        if mode=='pilot' or state=='open':print('point',point,state,len(extra),flush=True)
        hist[state]+=1
    print(holes,'hist',hist,'projected seconds',round((time.perf_counter()-clock)*64/len(points),3),'union',len(selected),flush=True)
    if mode!='pilot' and not hist['open']:witness(base,Path('multi'+'-'.join(map(str,holes))),selected)


if __name__=='__main__':
    if sys.argv[1]=='control':control()
    else:run(tuple(map(int,sys.argv[1].split(','))),int(sys.argv[2]),sys.argv[3])
