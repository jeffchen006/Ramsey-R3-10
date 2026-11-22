from collections import Counter
from functools import lru_cache
from itertools import combinations,combinations_with_replacement,permutations
import json
import math
from pathlib import Path
import sys

from triple18 import pairs,known_graphs


def actions(degrees):
    masks=pairs(len(degrees))
    result=[]
    for perm in permutations(range(len(degrees))):
        if tuple(degrees[index] for index in perm)!=degrees:continue
        images=tuple(sum(1<<target for source,target in enumerate(perm) if mask>>source&1) for mask in range(1<<len(degrees)))
        result.append((images,tuple(masks.index(images[mask]) for mask in masks)))
    return result


def triple_classes(degrees):
    group=actions(degrees);domain=[mask for mask in range(1<<len(degrees)) if mask.bit_count()==3];remaining=set(combinations_with_replacement(domain,2))
    while remaining:
        first=min(remaining);images=[tuple(sorted((action[first[0]],action[first[1]]))) for action,_ in group]; remaining-=set(images)
        stabilizer=[perm for image,(_,perm) in zip(images,group) if image==first];yield first,stabilizer,len(set(images))


def words(degrees,triples):
    order=len(degrees);target=tuple(degree-sum(word>>site&1 for word in triples) for site,degree in enumerate(degrees));masks=pairs(order)
    caps={mask:2-sum(mask&word==mask for word in triples) for mask in masks}
    @lru_cache(None)
    def compositions(total,limits):
        if total<0 or total>sum(limits):return ()
        if not limits:return ((),)
        return tuple((amount,*tail) for amount in range(min(total,limits[0])+1) for tail in compositions(total-amount,limits[1:]))
    def rec(need,index,prefix):
        if not need:yield bytes(prefix);return
        limits=tuple(min(rest,caps[(1<<index)|(1<<nextsite)]) for nextsite,rest in enumerate(need[1:],index+1))
        for row in compositions(need[0],limits):yield from rec(tuple(rest-amount for rest,amount in zip(need[1:],row)),index+1,prefix+row)
    yield from rec(target,0,())


def obstruction(order,triples,ordinary):
    for size in range(3):
        for selected in combinations(triples,size):
            if len(selected)==2 and not selected[0]&selected[1]:continue
            allowed=[word for word in ordinary if all(word&special for special in selected)]
            families=([word for word in allowed if word>>site&1] for site in range(order))
            triangles=([word for word in allowed if word&mask==word] for mask in TRIS[order])
            for category in (families,triangles):
                for family in category:
                    entire=[*selected,*family];union=0
                    for word in entire:union|=word
                    if union.bit_count()<len(entire):return tuple(entire)
    return ()


TRIS={order:tuple(sum(1<<site for site in triple) for triple in combinations(range(order),3)) for order in range(4,8)}


def test():
    known_graphs();counts=Counter();degrees=(4,4,3,3);order=len(degrees)
    for triples,group,multi in triple_classes(degrees):
        for word in words(degrees,triples):
            ordinary=[mask for mask,amount in zip(pairs(order),word) for _ in range(amount)];allrows=list(triples)+ordinary
            def visit(selected,rest,union):
                if selected>union.bit_count():return True
                return any(visit(selected+1,[other for other in rest[offset+1:] if other&item],union|item) for offset,item in enumerate(rest))
            bad=bool(obstruction(order,triples,ordinary));assert bad==visit(0,allrows,0);counts[bad]+=1
    assert all(counts[flag] for flag in [False,True]);print('literal intersecting-subfamily and sorted/triple-repetition controls',counts,flush=True)


def census(destination):
    with destination.open('x') as stream:
        for kind,degrees in [('one',(6,4,4,4,4,4,4)),('two',(5,5,4,4,4,4,4))]:
            for triples,group,multi in triple_classes(degrees):
                universe=set(words(degrees,triples));raw=len(universe);counts=Counter()
                for word in sorted(universe):
                    if word not in universe:continue
                    orbit={bytes(word[source] for source in perm) for perm in group};assert orbit<=universe; universe-=orbit
                    ordinary=[mask for mask,amount in zip(pairs(7),word) for _ in range(amount)];bad=obstruction(7,triples,ordinary);counts['hosts']+=1;counts['labelled']+=len(orbit);counts['pass']+=not bad
                    stream.write(json.dumps(dict(kind=kind,triples=triples,pairs=list(word),weight=len(orbit)*multi,aut=len(group)//len(orbit),hall=bad),separators=(',',':'))+'\n')
                assert not universe and counts['labelled']==raw
                print(kind,triples,multi,raw,dict(counts),flush=True)


if __name__=='__main__':
    if sys.argv[1]=='cal':test()
    else:census(Path(sys.argv[1]))
