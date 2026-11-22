"""Price and reconstruct the named-hole chart without enumerating global signings."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import sys
from time import process_time

from column_audit import insert, normal
from cyclic_check import read_base
from hole_price import control, edgespace, support_list
from hole_verify import Original, calibration
from old_indicator import cycle_basis


def target():
    base = read_base(Path('../r13/max.q').read_text().splitlines()[8])
    assert base == [[int(min(abs(left-right),18-abs(left-right)) in (0,6,7,8,9)) for right in range(18)] for left in range(18)]
    base[0][0] = 0
    return base


def coordinates(form,chart):
    answer = 0
    for index, item in enumerate(chart):
        if form & (1 << (item.bit_length()-1)):
            form ^= item
            answer |= 1 << index
    assert not form
    return answer


def prepare():
    base = target(); keys = edgespace(base); supports = support_list(base,0,10)
    eligible = tuple(site for site in range(1,18) if not base[0][site]); assert len(eligible)==10
    original = Original(18,set(keys)); combined = {}; independent = {}; raw = {}
    pairs = {pair:2<<index for index,pair in enumerate(keys)}
    rows=[]; histogram=Counter()
    for sites in supports:
        mask=sum(1<<site for site in sites); forms=cycle_basis(keys,sites,64)
        for form in forms:insert(combined,form)
        rawforms=cycle_basis(pairs,sites,64)
        for form in rawforms:insert(raw,form)
        checked=original.flat(original.triangle,mask); basis={}
        for form in forms:insert(basis,normal(original.triangle,original.translate(form)))
        assert len(checked)==len(forms)==len(basis) and all(not normal(basis,form) for form in checked)
        for form in checked:insert(independent,form)
        rows.append((mask,forms));histogram[len(rawforms),len(forms)]+=1
    chart=sorted(combined.values(),key=int.bit_length,reverse=True)
    assert len(chart)==len(independent); assert len(rows)==45
    print('eligible',eligible,'edges',len(keys),'triangle dimension',len(original.triangle),'nonneighbor induced cycle rank',len(cycle_basis(pairs,eligible,64)),'raw span',len(raw),'effective',len(chart),'(raw,effective) histogram',sorted(histogram.items()),flush=True)
    return chart,[(mask,[coordinates(form,chart) for form in forms]) for mask,forms in rows]


def run(mode):
    chart,rows=prepare(); assert len(chart)<=12
    total=1<<len(chart); step=1 if mode=='full' else max(1,total//32)
    start=process_time(); points=list(range(0,total,step)); surviving=[]
    for point in points:
        if all(any((form&point).bit_count()%2 for form in forms) for mask,forms in rows):surviving.append(point)
    expense=process_time()-start
    print(mode,'sample size',len(points),'survive',len(surviving),'scan projected CPU sec',expense*total/len(points),flush=True)
    if mode=='full':
        Path('roles.pass').write_text(''.join(f'{point}\n' for point in surviving)); Path('roles.chart').write_text(''.join(f'{form}\n' for form in chart))


if __name__=='__main__':
    if sys.argv[1]=='control':control(); calibration()
    else:run(sys.argv[1])
