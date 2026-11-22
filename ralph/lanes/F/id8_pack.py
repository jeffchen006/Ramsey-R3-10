"""One-hole, four poles avoiding the hole: direct 20-to-24 vertex extension."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import sys

from id8_contacts import materialize
from orbit_extend import independent_sets,vertices,to_graph6


def physical(graph,count):
    return tuple(independent_sets(graph,(1<<len(graph))-1,count))


def hosts():
    base=materialize();sevens=physical(base,7)
    cols=[mask for size in range(10) for mask in physical(base,size) if all(mask&row for row in sevens)]; assert len(cols)==22
    fours=[seq for seq in combinations(cols,4) if all(not (left&right) for left,right in combinations(seq,2))];assert len(fours)==1
    seq,=fours; roster=[]
    for flags in range(64):
        graph=base.copy()+list(seq)
        for index,column in enumerate(seq):
            for vertex in vertices(column):graph[vertex]|=1<<(20+index)
        for index,(left,right) in enumerate(combinations(range(20,24),2)):
            if flags>>index&1:graph[left]|=1<<right;graph[right]|=1<<left
        if any(graph[left]&graph[right] for left,right in combinations(range(24),2) if graph[left]>>right&1):continue
        if next(independent_sets(graph,(1<<24)-1,8),None) is not None:continue
        roster.append((flags,graph))
    print('22 columns; lone disjoint four-pack',seq,'legal pole edge masks',[flags for flags,_ in roster],flush=True);return roster


if __name__=='__main__':
    for flags,graph in hosts():print(flags,to_graph6(graph),len(physical(graph,7)))
