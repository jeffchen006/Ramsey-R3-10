import argparse
from collections import defaultdict
from itertools import combinations
from pathlib import Path

from induced_pilot import flip,graph_key,line,planted
from path_growth import bits
from punctured import certificate


def label(graph,pins,sites):
    key=graph_key(graph,pins);start=len(pins);index={}
    for mask,size in key:index[mask]=start;start+=size
    marked=0
    for site in sites:
        if site in pins:point=pins.index(site)
        else:
            mask=sum(1<<pos for pos,anchor in enumerate(pins) if site in graph[anchor]);point=index[mask];index[mask]+=1
        marked|=1<<point
    return key,marked


def evidence(graph,pins,sites):
    ext=set(range(len(graph)))-set(pins);marked=set(sites)&ext
    return certificate(graph,[[point]for point in pins]+([sorted(marked)] if marked else [])+([sorted(ext-marked)] if ext-marked else []))


def census(dest,output):
    expected=defaultdict(set);total=0
    for graph,forward in planted():
        for pins in (forward,(forward[1],forward[0],*reversed(forward[2:]))):
            key=graph_key(graph,pins)
            if key>flip(key):continue
            for sites in combinations(range(22),2):
                first,second=sites
                if len(graph[first]&graph[second])!=1:continue
                name=label(graph,pins,sites);total+=1;expected[name].add(evidence(graph,pins,sites))
    keys=sorted(expected)
    if output is None:
        with (dest/'pair-cal22.tsv').open('w')as stream:
            for key,mark in keys:print(mark,line(key),file=stream)
        print('C22 physical-oriented defect marks',total,'distinct anchored inputs',len(keys),'classes',sum(map(len,expected.values())))
    else:
        found=set();index=0
        for text in output.read_text().splitlines():
            words=text.split();key,mark=keys[index]
            if words[0]=='model':
                graph=[set(bits(int(field)))for field in words[1:]];found.add(evidence(graph,tuple(range(10)),list(bits(mark))))
            else:
                assert int(words[0])==index and words[1]=='0' and found==expected[key,mark],(index,len(found),len(expected[key,mark]));index+=1;found=set()
        assert index==len(keys);print('PASS paired coloured positive',index,'inputs,',sum(map(len,expected.values())),'classes')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('dest',type=Path);parser.add_argument('output',type=Path,nargs='?');args=parser.parse_args();census(args.dest,args.output)
