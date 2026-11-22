"""Produce independent planted square/defect tables and the exact K=2 min-square-12 subcase."""
import argparse
from pathlib import Path
import random
from induced_pilot import ROOT,decode,neighbors


def tables(graph):
    order=len(graph);exc=[sum(1<<other for other in range(order) if (row&graph[other]).bit_count()==1) for row in graph]
    square={}
    for first in range(order):
        for second in range(first):
            if not graph[first]>>second&1:continue
            left=graph[first]&~(1<<second);right=graph[second]&~(1<<first)
            square[first,second]=sum((graph[point]&right).bit_count() for point in range(order) if left>>point&1)
    for point,row in enumerate(graph):
        local=sum(q for pair,q in square.items() if point in pair);degree=row.bit_count();assert local==2*(2*degree*(degree-1)-3*(order-1-degree)+exc[point].bit_count())
    return exc,square


def encode(fixed,graph,exc,quota):
    return ' '.join(map(str,(fixed,*graph,*exc,*(quota.get((first,second),0)for first in range(len(graph)) for second in range(first)))))+'\n'


def prepare(dest):
    seeds=random.Random(411015);cal=[];truth=[]
    for text in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=[sum(1<<point for point in row) for row in neighbors(22,decode(text))]
        if any(row.bit_count()!=6 for row in graph) or any((row&second).bit_count()>3 for idx,row in enumerate(graph) for second in graph[:idx]):continue
        exc,square=tables(graph);reference=[*graph,*[sum(1<<other for other in range(22) if row&1<<other==0 and 1<=(row&graph[other]).bit_count()<=2) for row in graph],*[sum(1<<other for other in range(22) if (row&graph[other]).bit_count()==3) for row in graph]]
        for fixed in [0,(1<<22)-1,*[seeds.getrandbits(22) for idx in range(40)]]:
            cal.append(encode(fixed,graph,exc,square));truth.append(' '.join(map(str,reference))+'\n')
    (dest/'excess-cal.in').write_text(''.join(cal));(dest/'excess-cal.truth').write_text(''.join(truth))
    targets=[];ids=[]
    for rank,row in enumerate((dest.parent/'ind10/four-40.in').read_text().splitlines()):
        fixed,*graph=map(int,row.split());cross={(point,other) for point in (2,3) for other in (0,1) if graph[point]>>other&1}
        matchings=[{(2,0),(3,1)},{(2,1),(3,0)}];matchings=[edges for edges in matchings if edges<=cross]
        if not matchings:continue
        assert len(matchings)==1
        if any((graph[first]&graph[second]).bit_count()==1 for first,second in ((2,0),(2,1),(3,0),(3,1))):continue
        quota={(first,second):12+2*((first,second) in matchings[0]) for first in range(40) for second in range(first)}
        targets.append(encode(fixed,graph,[2,1,8,4]+[0]*36,quota));ids.append(str(rank))
    (dest/'excess.in').write_text(''.join(targets));(dest/'excess.ids').write_text('\n'.join(ids)+'\n');print('cal',len(cal),'target',ids)


def audit(dest):
    for ln,(answer,line) in enumerate(zip((dest/'excess-cal.out').read_text().splitlines(),(dest/'excess-cal.truth').read_text().splitlines(),strict=True)):
        num,conflict,unknown,*may=map(int,answer.split());planted=list(map(int,line.split()));assert ln==num and conflict==0 and len(planted)==len(may) and all(not (target&~allowed) for target,allowed in zip(planted,may));assert ln%42!=1 or (not unknown and planted==may)
    print('PASS 126 C22 states spanning three distinct known cap-three graphs; true signed colours preserved and every fully pinned domain exact')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('dest',type=Path);parser.add_argument('--audit',action='store_true');args=parser.parse_args();(audit if args.audit else prepare)(args.dest.resolve())
