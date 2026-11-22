"""Prejoin size for an induced P8; do not materialize paired ten-star rows."""

import argparse
from collections import Counter
from pathlib import Path

from long_root import reverse
from path_growth import ROOT,bits,read_profiles
from punct_path import decode,neighbors,pairs,profile_key


PINS=(tuple(range(9)),(1,0,9,8,7,6,5,4,3))
SHARED=1023^((1<<2)|(1<<9))
MAPS=[[sum(1<<order[index] for index in bits(mask)) & SHARED for mask in range(512)] for order in PINS]


def restriction(profile,side):
    totals=Counter()
    for mask,count in profile:
        if mask!=258:
            totals[MAPS[side][mask]]+=count
    return profile_key(totals)


def size(profiles):
    counts=[Counter(),Counter()]
    marks=0
    for profile in profiles:
        canonical=profile_key(profile)
        for directed in {canonical,reverse(canonical)}:
            if (258,1) not in directed:
                continue
            for side in range(2):
                counts[side][restriction(directed,side)]+=1
            marks+=1
    matching=counts[0].keys() & counts[1].keys()
    print('extendible oriented half-candidates',marks,'shared fingerprints matching',len(matching),'raw matched pairs before endpoint overlaps',sum(counts[0][key]*counts[1][key] for key in matching))


def control():
    marks=0
    for code in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=neighbors(22,decode(code))
        if {len(row) for row in graph}!={6} or max(len(left&right) for left,right in pairs(graph))>3:
            continue
        for root in range(22):
            for other in graph[root]:
                if root>=other:
                    continue
                block=(graph[root]|graph[other])-{root,other}
                walks=[(start,) for start in graph[root]-{other}]
                for _ in range(7):
                    walks=[walk+(point,) for walk in walks for point in (graph[walk[-1]]&block)-set(walk)]
                for walk in walks:
                    if walk[-1] in graph[walk[0]]:
                        continue
                    core=(root,other)+walk
                    shared=[]
                    for side,order in enumerate(PINS):
                        pins=[core[index] for index in order]
                        hist=Counter(sum(1<<index for index,anchor in enumerate(pins) if vertex in graph[anchor]) for vertex in range(22) if vertex not in pins)
                        assert hist[258]==1
                        shared.append(restriction(profile_key(hist),side))
                    assert shared[0]==shared[1]
                    marks+=1
    assert marks>0
    print('PASS induced P8 C22 marks, compatible halves and omitted endpoint mask',marks)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    args=parser.parse_args()
    control()
    size(read_profiles(args.source))
