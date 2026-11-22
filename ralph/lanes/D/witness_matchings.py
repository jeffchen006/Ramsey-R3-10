"""Bind exact K=2,4 common-centre seeds to the previously audited frontier."""
from collections import Counter
from pathlib import Path
import sys
from induced_pilot import ROOT,decode,neighbors


def sources(dest):
    by_parent=[];records=[]
    for text in (dest/'all3840.out').open():
        if text.startswith('child'):records.append(tuple(map(int,text.split()[1:])))
        else:by_parent.append(records);records=[]
    old=dest.parent/'ind10';roots=(old/'four-40.in').read_text().splitlines();live=(old/'four-open-live.in').read_text().splitlines();two=[];four=[];keys=[]
    for parent,children in zip(live,by_parent,strict=True):
        _,*partial=map(int,parent.split());center=partial[0]&partial[1]
        if center!=partial[2]&partial[3]:continue
        assert len(children)==1;fixed,*graph=children[0];focus=center.bit_length()-1
        available=[point for point in range(4,40) if graph[focus]>>point&1];assert len(available)==5 and len({graph[point]&fixed for point in available})==1
        deficient=[2,1,8,4]+[0]*36;two.append(' '.join(map(str,[fixed,*graph,*deficient])))
        high=sum((graph[left]&graph[right]).bit_count()==3 for left in (0,1) for right in (2,3));ordinal=roots.index(parent)
        if high>=3:
            for first,last in zip(available[:4:2],available[1:4:2]):deficient[first]|=1<<last;deficient[last]|=1<<first
            four.append(' '.join(map(str,[fixed,*graph,*deficient])))
        keys.append((ordinal,focus,high,available))
    print('shared roots, marked centre / high cross entries / five interchangeable other neighbours',keys)
    for number,rows in [(2,two),(4,four)]:(dest/f'mono-K{number}.in').write_text('\n'.join(rows)+'\n')
    cal=[];true=[]
    for code in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=[sum(1<<v for v in row) for row in neighbors(22,decode(code))]
        if {v.bit_count() for v in graph}!={6} or any((a&b).bit_count()>3 for i,a in enumerate(graph)for b in graph[:i]):continue
        lows=[sum(1<<other for other in range(22) if (row&graph[other]).bit_count()==1)for row in graph]
        for omit in (4,6,9):
            fixed=(1<<(22-omit))-1;raw=[row if fixed>>idx&1 else row&fixed for idx,row in enumerate(graph)];cal.append(' '.join(map(str,[fixed,*raw,*lows])));true.append(' '.join(map(str,graph)))
    (dest/'exact-cal.in').write_text('\n'.join(cal)+'\n');(dest/'exact-cal.truth').write_text('\n'.join(true)+'\n')


if __name__=='__main__':sources(Path(sys.argv[1]).resolve())
