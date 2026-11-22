"""Exact marked C16 control for the cyclic eight-star family (no L=7 premise)."""

import argparse
from collections import Counter,defaultdict
from pathlib import Path

from path_growth import ROOT,bits
from punct_path import core_instances,decode,neighbors,pairs,permuter,profile_key,symmetry
from punctured import certificate


def source():
    groups=symmetry(True)
    expected=defaultdict(set)
    canon=permuter(True)
    physical=0
    for line in (ROOT/'gluing/val/r3_6_16.g6').read_text().splitlines():
        graph=neighbors(16,decode(line))
        if {len(row) for row in graph}!={5} or max(len(left&right) for left,right in pairs(graph))>3:
            continue
        for cycle,original in core_instances(graph):
            if not cycle:
                continue
            physical+=1
            for perm in groups:
                core=[original[point] for point in perm]
                outer=sorted(set(range(16))-set(core))
                counts=Counter(sum(1<<index for index,anchor in enumerate(core) if vertex in graph[anchor]) for vertex in outer)
                if profile_key(counts)==canon(counts):
                    expected[profile_key(counts)].add(certificate(graph,[[vertex] for vertex in core]+[outer]))
    assert physical==24
    return expected


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('output',type=Path)
    parser.add_argument('--check',type=Path)
    args=parser.parse_args()
    groups=source()
    keys=sorted(groups)
    args.output.write_text(''.join(' '.join(f'{mask}:{count}' for mask,count in key)+'\n' for key in keys))
    if args.check:
        seen=defaultdict(set)
        current=0
        for line in args.check.read_text().splitlines():
            fields=line.split()
            if fields[0]=='model':
                graph=[set(bits(int(value))) for value in fields[1:]]
                seen[keys[current]].add(certificate(graph,[[point] for point in range(8)]+[list(range(8,16))]))
            else:
                assert int(fields[0])==current and int(fields[1])==0
                current+=1
        assert seen==groups and current==len(keys)
        print('PASS 24 planted C16 cyclic path marks,',len(keys),'eight-star profiles,',sum(map(len,groups.values())),'individualized full graph orbits')
