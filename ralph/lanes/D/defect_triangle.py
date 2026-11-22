"""Six-cycle core with alternating singleton-codegree pairs."""

import argparse
from collections import Counter
from itertools import combinations,permutations,product
from pathlib import Path

from induced_pilot import ROOT,graph_key,line
from punct_path import decode,neighbors,pairs,profile_key


def template():
    return neighbors(6,{(i,3+j)for i in range(3)for j in range(3)if i!=j})


def canonical(key):
    return min(tuple(sorted((sum(1<<(perm[pos%3]+3*(pos//3))for pos in range(6)if mask>>pos&1),num)for mask,num in key))for perm in permutations(range(3)))


def catalog(order,degree,minimum):
    found=set();labelled=0
    for opposite in product(range(minimum,4),repeat=3):
        if max(opposite)>degree-2:continue
        size=[degree-2-value for value in opposite]
        for meeting in product(range(minimum-1,3),repeat=3):
            for triple in range(min(meeting)+1):
                hist=Counter();hist[56]=triple
                for point in range(3):
                    hist[1<<point]=degree-2-opposite[point];hist[(1<<point)|(8<<point)]=opposite[point]
                    hist[56^(8<<point)]=meeting[point]-triple
                    hist[8<<point]=size[point]-sum(meeting[other]for other in range(3)if other!=point)+triple
                hist[0]=order-6-sum(hist.values())
                if min(hist.values())<0:continue
                key=profile_key(+hist);found.add(canonical(key));labelled+=1
    return found,labelled


def raw(key):
    core=template();graph=[sum(1<<point for point in row)for row in core]
    for mask,num in key:
        for _ in range(num):
            index=len(graph);graph.append(mask)
            for point in range(6):
                if mask>>point&1:graph[point]|=1<<index
    return ' '.join(map(str,(7,63,*graph)))


def controls(dest):
    actual=set();marks=0
    for text in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=neighbors(22,decode(text))
        if {len(row)for row in graph}!={6}or max(len(first&second)for first,second in pairs(graph))>3:continue
        for choice in combinations(range(22),3):
            other=[graph[choice[(k+1)%3]]&graph[choice[(k+2)%3]]for k in range(3)]
            if any(len(cell)!=1 for cell in other):continue
            pins=choice+tuple(next(iter(cell))for cell in other);assert len(set(pins))==6
            assert all((pins[second]in graph[pins[first]])==(second in template()[first]) for first,second in pairs(range(6)))
            actual.add(canonical(graph_key(graph,pins)));marks+=1
    full,labelled=catalog(22,6,1);assert actual and actual<=full
    (dest/'tri-cal.in').write_text(''.join(raw(key)+'\n'for key in sorted(full)))
    (dest/'tri-cal.ids').write_text(''.join(str(index)+'\n'for index,key in enumerate(sorted(full))if key in actual))
    print('C22 planted triangle marks',marks,'live profiles',len(actual),'complete incidence candidates',len(full),'labelled',labelled)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('dest',type=Path);args=parser.parse_args();controls(args.dest);full,labelled=catalog(40,9,2);(args.dest/'tri.in').write_text(''.join(raw(key)+'\n' for key in sorted(full)));(args.dest/'tri.keys').write_text(''.join(line(key)+'\n'for key in sorted(full)));print('target',len(full),'profiles',labelled,'labelled')
