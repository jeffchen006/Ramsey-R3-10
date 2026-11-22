"""Reconstruct the nonstar endpoint profiles by extending the nine anchored rows."""
from collections import Counter
from itertools import combinations,permutations
from pathlib import Path
import sys
from witness_frontier import raw_children


def identity(points,graph):
    flags=[(first,last,(graph[first]&graph[last]).bit_length()-1) for first,last in combinations(points,2) if (graph[first]&graph[last]).bit_count()==1]
    if len(flags)!=4 or {site for left,right,centre in flags for site in (left,right)}!=set(points):return None
    if len({(site,centre) for left,right,centre in flags for site in (left,right)})!=8:return None
    if set.intersection(*map(set,flags)) or any(not set(first)&set(second) for first,second in combinations(flags,2)):return None
    weak={frozenset((left,right)) for left,right,centre in flags};width=len(points)
    wanted={(0,1),(1,2),(2,3),(3,4)} if width==5 else {(0,1),(1,2),(1,3),(2,3)}
    possible=[]
    for order in permutations(points):
        if not all(frozenset((order[left],order[right])) in weak for left,right in wanted):continue
        edges=tuple((left,right) for left,right in combinations(range(width),2) if graph[order[left]]>>order[right]&1)
        mask=Counter(sum(1<<idx for idx,site in enumerate(order) if graph[site]>>point&1) for point in range(len(graph)) if point not in points)
        possible.append((edges,tuple(sorted(mask.items()))))
    assert possible;return min(possible)


def run(folder):
    old=folder.parent/'ind10';rows=(old/'four-40.in').read_text().splitlines();expect=[]
    for text in (folder/'nonstar.in').read_text().splitlines():
        fixed,*data=map(int,text.split());expect.append(identity(tuple(range(fixed.bit_count())),data[:40]))
    assert len(set(expect))==len(expect) and None not in expect
    from_nine=set();addresses=[]
    for ordinal,text in enumerate(rows):
        fixed,*graph=map(int,text.split());first,last=graph[0]&graph[1],graph[2]&graph[3]
        if first==last or not (first|last)&fixed:continue
        used=set();sizes=Counter();basic=identity(tuple(range(4)),graph)
        if basic:used.add(basic)
        for label in sorted(set(graph[4:])):
            point=graph.index(label,4)
            for _,*child in raw_children(graph,fixed,[point]):
                record=identity((0,1,2,3,point),child)
                if record:used.add(record)
        from_nine.update(used);addresses.append((ordinal,sorted(expect.index(item) for item in used)))
    assert from_nine==set(expect);print('PASS all 26 from the 9 internal roots by an independent fifth-star extension',addresses,flush=True)
    emitted=[];batch=set()
    for text in (folder/'nonstar-wit.out').read_text().splitlines():
        if text.startswith('child '):batch.add(tuple(map(int,text.split()[1:])))
        else:emitted.append(batch);batch=set()
    extras=folder/'raw-extra.in';exids=folder/'raw-extra.ids';total=0
    with extras.open('w') as add,exids.open('w') as labels:
        for idx,text in enumerate((folder/'nonstar.in').read_text().splitlines()):
            if (folder/'nonstar.ids').read_text().splitlines()[idx].split()[1] not in ('1','2'):continue
            fixed,*data=map(int,text.split());graph=data[:40];low=data[40:];pairs=[(left,right) for left,right in combinations(range(40),2) if low[left]>>right&1];assert len(pairs)==4
            centers=sorted({(graph[left]&graph[right]).bit_length()-1 for left,right in pairs if not (graph[left]&graph[right]&fixed)})
            expected=set()
            for row in raw_children(graph,fixed,centers):
                frozen,*candidate=row;sites=[point for point in range(40) if frozen>>point&1]
                if all(((candidate[left]&candidate[right]).bit_count()==1)==bool(low[left]>>right&1) for left,right in combinations(sites,2)):expected.add(row)
            assert emitted[idx]<=expected;missing=sorted(expected-emitted[idx]);total+=len(expected)
            for row in missing:print(*row,*low,file=add);print(idx,file=labels)
    print('raw exact-star count',total,'minus C++ live',len(extras.read_text().splitlines()),'need separate direct test')


if __name__=='__main__':run(Path(sys.argv[1]))
