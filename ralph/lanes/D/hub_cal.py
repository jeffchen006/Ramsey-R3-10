"""Exact six-star path cover for an individualized site on planted Ramsey graphs."""
import argparse
from collections import Counter,defaultdict
from pathlib import Path

from induced_pilot import graph_key,line
from path_growth import ROOT,bits
from punct_path import core_instances,decode,neighbors,pairs
from punctured import certificate


def prepare(dest):
    cases=defaultdict(set);physical=0
    for code in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=neighbors(22,decode(code))
        if {len(row) for row in graph}!={6} or max(len(first&second) for first,second in pairs(graph))>3:continue
        for cycle,original in core_instances(graph):
            if cycle:continue
            physical+=1
            forward=[original[pos] for pos in (4,0,1,7,2,5,3,6)]
            for pins in (forward,[forward[1],forward[0],*reversed(forward[2:])]):
                key=graph_key(graph,pins)
                masks={point:sum(1<<pos for pos,anchor in enumerate(pins) if point in graph[anchor]) for point in set(range(22))-set(pins)}
                for site in range(22):
                    if site in pins:hub=pins.index(site)
                    else:hub=8+sum(size for mask,size in key if mask<masks[site])
                    groups=[[point]for point in pins]+([[site]] if site not in pins else [])
                    other=sorted(set(range(22))-{site}-set(pins));groups.append(other)
                    cases[(key,hub)].add(certificate(graph,groups))
    assert physical==239
    with (dest/'hub-cal.tsv').open('w')as out,(dest/'hub-cal.expect').open('w')as truth:
        for (key,hub),classes in sorted(cases.items()):
            print(1<<hub,line(key),file=out);print(hub,*sorted(classes),file=truth)
    print('physical C22 induced-P6 marks (22 sites, both directions)',physical,'distinct input rows',len(cases),'classes with 8 individualized anchors+hub',sum(map(len,cases.values())))


def audit(dest,outputs):
    expected=[(int(row.split()[0]),set(row.split()[1:])) for row in (dest/'hub-cal.expect').read_text().splitlines()]
    for output in outputs:
        counts=Counter();found=set();index=0
        for text in output.read_text().splitlines():
            fields=text.split();hub,truth=expected[index]
            if fields[0]=='model':
                graph=[set(bits(int(field)))for field in fields[1:]];blocks=[[point] for point in range(8)]+([[hub]] if hub>=8 else [])+[sorted(set(range(8,22))-{hub})];found.add(certificate(graph,blocks))
            else:
                assert int(fields[0])==index and fields[1]=='0';assert found==truth,(output,index,len(found),len(truth));counts['classes']+=len(found);found=set();index+=1
        assert index==len(expected);print('PASS',output.name,index,'roots',counts['classes'],'marked classes')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('dest',type=Path);parser.add_argument('outputs',nargs='*',type=Path);args=parser.parse_args();prepare(args.dest) if not args.outputs else audit(args.dest,args.outputs)
