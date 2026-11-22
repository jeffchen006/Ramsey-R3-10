"""Independent seed-and-extend audit: no maximum flag degree, parity or size cutoff."""
from collections import Counter
from itertools import combinations,permutations,product
from pathlib import Path
import json
import sys


def canonical(family):
    best=None
    for arrangement in permutations(family):
        for directions in product((0,1),repeat=len(family)):
            order={};word=[]
            for flag,reverse in zip(arrangement,directions):
                for vertex in (flag[::-1] if reverse else flag):
                    if vertex not in order:order[vertex]=len(order)
                    word.append(order[vertex])
            key=tuple(word)
            if best is None or key<best:best=key
    return best


def extensions(family):
    size=1+max(map(max,family));used_arcs={(endpoint,centre) for left,centre,right in family for endpoint in (left,right)}
    for triple in combinations(range(size+2),3):
        if size+1 in triple and size not in triple:continue
        if any(not set(triple).intersection(flag) or set(triple)==set(flag) for flag in family):continue
        for centre in triple:
            left,right=sorted(set(triple)-{centre})
            if (left,centre) in used_arcs or (right,centre) in used_arcs:continue
            enlarged=(*family,(left,centre,right));edges={frozenset((endpoint,mid)) for first,mid,second in enlarged for endpoint in (first,second)}
            def joins(first,second):return frozenset((first,second)) in edges
            if any(all(joins(first,second) for first,second in combinations(cycle,2)) for cycle in combinations(range(size+2),3)):continue
            if any(any(other!=mid and joins(first,other) and joins(second,other) for other in range(size+2)) for first,mid,second in enlarged):continue
            yield enlarged


def run(folder):
    seeds=[((0,1,2),(1,0,3)),((0,1,2),(1,3,4))];complete={};opened=set();attempts=Counter()
    def explore(family):
        intersection=set.intersection(*map(set,family));attempts[len(family)]+=1
        if not intersection:
            index=canonical(family)
            if index in complete:return
            complete[index]=family
        for child in extensions(family):
            if intersection and intersection<=set(child[-1]):continue
            explore(child)
    for seed in seeds:explore(seed)
    expected={canonical(family) for family in json.loads((folder/'uncapped/abstract.json').read_text()) if any(not {left[0],left[2]}.intersection({right[0],right[2]}) and left[1]!=right[1] for left,right in combinations(family,2))}
    assert expected==set(complete)
    print('PASS unordered shape identities by independent explicit endpoint reversals/permutations; seeds singly/doubly internal; no valence bound or cardinality cutoff. Visits',sorted(attempts.items()),'empty-intersection classes',sorted(Counter(len(family) for family in complete.values()).items()))


if __name__=='__main__':run(Path(sys.argv[1]))
