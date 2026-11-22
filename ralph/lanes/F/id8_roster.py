"""Freshly bind the first-column domains and replay each elimination on literal endpoint equations."""
from collections import Counter
from itertools import combinations
from pathlib import Path

from column_audit import parse_request,replay
from cyclic_check import read_base


def audit():
    text=Path('id8.q').read_text().strip();base=read_base(text)
    assert len(base)==18 and all(base[left][right]==(left==right or 6<=abs(left-right)<=12) for left in range(18) for right in range(18))
    expected=set()
    for count in range(8):
        for occupied in combinations(range(18),count):
            if not occupied:continue
            gaps=[second-first for first,second in zip(occupied,occupied[1:]+(occupied[0]+18,))]
            if max(gaps)<=7:expected.add(sum(1<<site for site in occupied))
    totals=Counter(); reps=set()
    for line in Path('feet.request').read_text().splitlines():
        name,edges,feet,tops=parse_request(line);assert len(feet)==1 and tops==[0] and not edges
        foot,=feet;assert foot==int(name) and foot not in reps;reps.add(foot)
        group={sum(1<<((shift+direction*index)%18) for index in range(18) if foot>>index&1) for direction in (1,-1) for shift in range(18)}
        assert min(group)==foot and group<=expected;expected-=group;totals[foot.bit_count()]+=len(group)
    assert not expected and len(reps)==1406
    ended={}
    for line in Path('feet.trace').read_text().splitlines():
        tag,command,*args=line.split()
        if command=='end':assert int(tag) not in ended and args[0]=='I';ended[int(tag)]=int(args[1])
    assert reps==ended.keys();print('exact first-column domains',dict(sorted(totals.items())),'full',sum(totals.values()),'orbits',len(ended),'deductions',sum(ended.values()),flush=True)
    replay('id8.q',10,'feet.request','feet.trace')


if __name__=='__main__':audit()
