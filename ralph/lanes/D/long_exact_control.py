"""Census of labelled P7 anchor orbits from the intact C22 source vs search."""

import argparse
from collections import Counter,defaultdict
from pathlib import Path

from long_overlap import placements
from long_root import reverse
from path_growth import ROOT,bits,read_profiles
from punct_path import decode,neighbors,pairs,profile_key
from punctured import certificate


def main(profiles,sources):
    keys=[profile_key(profile) for profile in read_profiles(profiles)]
    expected=defaultdict(set)
    count=0
    for line in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=neighbors(22,decode(line))
        if {len(row) for row in graph}!={6} or max(len(left&right) for left,right in pairs(graph))>3:
            continue
        for placement in placements(graph):
            count+=1
            for core in (placement,placement[:2]+tuple(reversed(placement[2:]))):
                exterior=sorted(set(range(22))-set(core))
                signature=profile_key(Counter(sum(1<<index for index,anchor in enumerate(core) if vertex in graph[anchor]) for vertex in exterior))
                if signature not in keys:
                    assert reverse(signature) in keys
                    continue
                expected[keys.index(signature)].add(certificate(graph,[[point] for point in core]+[exterior]))
    assert count==155
    for source in sources:
        actual=defaultdict(set)
        row=0
        total=0
        for line in source.read_text().splitlines():
            fields=line.split()
            if fields[0]=='model':
                graph=[set(bits(int(field))) for field in fields[1:]]
                actual[row].add(certificate(graph,[[point] for point in range(9)]+[list(range(9,22))]))
                total+=1
            else:
                assert int(fields[0])==row and int(fields[1])==0
                row+=1
        assert row==len(keys) and actual==expected,(source,row,{idx:(len(expected[idx]),len(actual[idx])) for idx in set(actual)|set(expected) if actual[idx]!=expected[idx]})
        print('PASS',source.name,'all',count,'physical marks ->',sum(map(len,expected.values())),'individually coloured P7-orbits across',row,'canonical profiles; returned',total,'representatives')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('profiles',type=Path)
    parser.add_argument('samples',nargs='+',type=Path)
    args=parser.parse_args()
    main(args.profiles,args.samples)
