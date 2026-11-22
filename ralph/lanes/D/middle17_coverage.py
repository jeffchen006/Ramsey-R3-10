"""Independent exact set audit, without scout catalogue, shore ranks or bitset join."""
from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product
import json
from pathlib import Path
import sys


def labelled_supports(order, degree):
    vertices=tuple(range(order)); pairs=list(combinations(vertices,2)); place={pair:1<<index for index,pair in enumerate(pairs)}
    def matchings(available):
        if not available:
            yield (); return
        first,*others=available
        yield from matchings(others)
        for neighbor in others:
            for rest in matchings([vertex for vertex in others if vertex!=neighbor]):
                yield ((first,neighbor),)+rest
    def fill(first, need, doubled, edges):
        if first==order:
            if all(not any((min(site,left),max(site,left)) in edges and (min(site,right),max(site,right)) in edges for site in vertices) for left,right in doubled):
                yield sum(place[pair] for pair in edges|doubled),sum(place[pair] for pair in doubled)
            return
        choices=[neighbor for neighbor in vertices[first+1:] if need[neighbor] and (first,neighbor) not in doubled]
        for neighbors in combinations(choices,need[first]):
            updated=need.copy(); updated[first]=0
            for neighbor in neighbors:updated[neighbor]-=1
            yield from fill(first+1,updated,doubled,edges|{(first,neighbor) for neighbor in neighbors})
    universe=set()
    for matching in matchings(vertices):
        need=[degree]*order
        for left,right in matching:need[left]-=2;need[right]-=2
        if min(need)>=0:universe.update(fill(0,need,set(matching),set()))
    return universe


def layers(sites):
    count=Counter(sites); assert max(count.values(),default=0)<=2
    return (sum(1<<site for site in count),sum(1<<site for site,weight in count.items() if weight==2))


def right_profiles(pairs, hostcounts, left, width):
    counts=hostcounts.copy()
    for site in left:counts[site]+=1
    if max(counts)>2:return
    forced=[site for site,count in enumerate(counts) if count==0]; added=width-len(forced)
    if added<0:return
    allowed=[site for site,count in enumerate(counts) if count<2]
    for extra in combinations(allowed,added):
        sites=forced+list(extra)
        if max(Counter(pole for site in sites for pole in pairs[site]).values(),default=0)<=2:yield layers(sites)


def control():
    pairs=list(combinations(range(4),2)); expected=set()
    for word in product(range(3),repeat=len(pairs)):
        if not all(sum(word[index] for index,pair in enumerate(pairs) if pole in pair)==2 for pole in range(4)):continue
        expected.add(layers([index for index,count in enumerate(word) for _ in range(count)]))
    assert len(expected)==6 and labelled_supports(4,2)==expected
    pairs=list(combinations(range(3),2)); total=0
    for counts in product(range(3),repeat=3):
        for left in range(3):
            observed=set(right_profiles(pairs,list(counts),[left],1))
            truth={layers([right]) for right in range(3) if all(1<=num+(left==site)+(right==site)<=2 for site,num in enumerate(counts))}
            assert observed==truth; total+=1
    print('controls labelled 2-regular multigraphs on four: 6; small literal joins:',total,flush=True)


def audit(directory):
    control(); order=7; pairs=list(combinations(range(order),2)); loc={pair:index for index,pair in enumerate(pairs)}
    actions=[tuple(loc[tuple(sorted((perm[left],perm[right])))] for left,right in pairs) for perm in permutations(range(order))]
    remaining=labelled_supports(order,4); print('all labelled Hall-surviving supports',len(remaining),flush=True)
    def transform(word,action):
        return tuple(sum(1<<action[site] for site in range(21) if part>>site&1) for part in word)
    def visit(prefix,low,free):
        if len(prefix)==6:
            yield tuple(prefix);return
        for site in range(low,len(pairs)):
            left,right=pairs[site]
            if free[left] and free[right]:
                state=free.copy();state[left]-=1;state[right]-=1
                yield from visit(prefix+[site],site,state)
    lefts=list(visit([],0,[2]*order)); assert len(lefts)==6202
    weight=total_ids=0
    for file in sorted(directory.glob('*.jsonl')):
        rows=list(map(json.loads,file.read_bytes().splitlines())); host=int(file.stem)
        assert [row['id'] for row in rows]==list(range(len(rows))) and all(row['host']==host for row in rows)
        masks=rows[0]['Y']; assert len(masks)==14 and all(row['Y']==masks for row in rows)
        counts=[masks.count((1<<left)|(1<<right)) for left,right in pairs]; assert sum(counts)==14
        word=layers([site for site,count in enumerate(counts) for _ in range(count)])
        orbit={transform(word,action) for action in actions}; assert orbit<=remaining; remaining-=orbit
        aut=[action for action in actions if transform(word,action)==word]
        joined={(layers(left),right) for left in lefts for right in right_profiles(pairs,counts,left,6)}
        ordered=len(joined)
        @lru_cache(None)
        def images(side):return [transform(side,action) for action in aut]
        for row in rows:
            left,right=tuple(row['word'][:2]),tuple(row['word'][2:]); assert (left,right) in joined
            imageset=set(zip(images(left),images(right))); imageset|={(second,first) for first,second in imageset}
            assert len(imageset)==row['weight'] and imageset<=joined,(host,row['id']); joined-=imageset
        assert not joined
        print('host',host,'support labellings',len(orbit),'aut',len(aut),'IDs',len(rows),'ordered',ordered,flush=True)
        total_ids+=len(rows);weight+=ordered
    assert not remaining and (total_ids,weight)==(15282,320878)
    print('PASS every actual word/orbit/weight, no missing or repeated support or ordered pair')


if __name__=='__main__':audit(Path(sys.argv[1]))
