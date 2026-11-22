"""Abstract intersecting deficient paths: extend one flag, retaining its centre."""
from collections import Counter
from itertools import combinations
from pathlib import Path
import json
import sys
import pynauty


def support(flags):
    size = 1 + max(max(flag) for flag in flags)
    graph = [set() for _ in range(size)]
    for left, centre, right in flags:
        graph[left].add(centre)
        graph[right].add(centre)
        graph[centre].update([left, right])
    return graph


def key(flags):
    graph = support(flags)
    size = len(graph)
    for flag in flags:
        for vertex in flag:
            graph[vertex].add(len(graph))
        graph.append(set(flag))
    return pynauty.certificate(pynauty.Graph(len(graph), adjacency_dict=dict(enumerate(graph)), vertex_coloring=[set(range(size)), set(range(size,len(graph)))]))


def usable(flags):
    graph = support(flags)
    if any(graph[first] & graph[last] for first in range(len(graph)) for last in graph[first]):
        return False
    slots = set()
    for left, centre, right in flags:
        if graph[left] & graph[right] != {centre} or (left,centre) in slots or (right,centre) in slots:
            return False
        slots.update([(left,centre), (right,centre)])
    return True


def extend(flags,cap=6):
    size = len(support(flags))
    loads = Counter(vertex for flag in flags for vertex in flag)
    for triple in combinations(range(size+2), 3):
        if size+1 in triple and size not in triple: continue
        if any(loads[vertex] == cap for vertex in triple): continue
        if any(not set(triple).intersection(flag) for flag in flags) or any(set(triple)==set(flag) for flag in flags): continue
        for centre in triple:
            left, right = sorted(set(triple)-{centre})
            family = (*flags, (left,centre,right))
            if usable(family): yield family


def classify(dest):
    stages = [{key(((0,1,2),)): ((0,1,2),)}]
    for size in range(2,20):
        level = {}
        for family in stages[-1].values():
            for child in extend(family):level.setdefault(key(child),child)
        stages.append(level)
        if not level:break
    cycle = [(min((idx-1)%5,(idx+1)%5), idx, max((idx-1)%5,(idx+1)%5)) for idx in range(5)]
    for size in range(1,6):
        for sub in combinations(cycle,size):
            vertices=sorted(set().union(*map(set,sub))); sub=tuple(tuple(vertices.index(vertex) for vertex in flag) for flag in sub)
            assert key(sub) in stages[size-1]
    print('C5: all 31 nonempty coloured subsets retained; same-centre repeated endpoint rejected', flush=True)
    assert not usable(((0,1,2),(0,1,3)))
    output=[]
    for size,level in enumerate(stages,1):
        nonstar=[family for family in level.values() if not set.intersection(*map(set,family))]
        output.extend(nonstar);print(size,len(level),len(nonstar),Counter(len(support(family)) for family in nonstar))
    (dest/'abstract.json').write_text(json.dumps(output)+'\n')


if __name__=='__main__':classify(Path(sys.argv[1]))
