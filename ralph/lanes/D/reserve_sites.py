"""Endpoint positions for K=2, or complete candidate pair positions after endpoint pruning."""
from collections import defaultdict
from itertools import combinations
from pathlib import Path
import sys


def graph_for(text):
    exterior=[int(field.split(':')[0]) for field in text.split() for _ in range(int(field.split(':')[1]))];graph=[0]*8+exterior
    def link(first,second):graph[first]|=1<<second;graph[second]|=1<<first
    link(0,1)
    for vertex in range(2,8):
        link(vertex%2,vertex)
        if vertex<7:link(vertex,vertex+1)
    for vertex,mask in enumerate(exterior,8):
        for anchor in range(8):
            if mask>>anchor&1:link(vertex,anchor)
    return graph


def placements(source,target,role):
    groups=defaultdict(set)
    for text in source.read_text().splitlines():
        if role=='endpoint':groups[text]=None
        else:
            mark,key=text.split(' ',1);groups[key].add(int(mark).bit_length()-1)
    total=0
    with target.open('w') as output:
        for key,allowed in groups.items():
            graph=graph_for(key);representatives=[*range(8),*sorted({8+graph[8:].index(row) for row in graph[8:]})];flags=[]
            for left,right in combinations(range(8),2):
                common=graph[left]&graph[right]
                if common.bit_count()==1:flags.append((left,common.bit_length()-1,right))
            if len(flags)>2 or any(set(first)&set(second) for first,second in combinations(flags,2)):continue
            if role=='endpoint':options=[(site,) for site in representatives]
            else:options=[*combinations(sorted(allowed),2),*((site,site+1) for site in sorted(allowed) if site>=8 and site+1<len(graph) and graph[site]==graph[site+1])]
            for choice in options:
                if sum(not set(choice)&{first,last} for first,centre,last in flags)>1:continue
                if len(choice)==2:
                    first,last=choice;overlap=graph[first]&graph[last]
                    if graph[first]>>last&1 or overlap.bit_count()>1 or (last<8 and not overlap):continue
                    if any(set(choice)!={a,b} and (set(choice)&set(flag) or overlap&(1<<a|1<<z|1<<b)) for flag in flags for a,z,b in [flag]):continue
                print(sum(1<<site for site in choice),key,file=output);total+=1
    print(role,'source profiles',len(groups),'placements',total)


if __name__=='__main__':placements(Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3])
