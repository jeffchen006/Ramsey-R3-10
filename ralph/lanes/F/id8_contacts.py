"""Physical neighborhood of a named hole. One tree-normalized local lift only."""
from collections import Counter
from itertools import combinations,product
from pathlib import Path
import sys
from id8_local import target
from orbit_extend import vertices,independent_sets,to_graph6


def materialize():
    base=target();sites=sorted(site for site in range(1,18) if not base[0][site]); edges=[pair for pair in combinations(range(10),2) if base[sites[pair[0]]][sites[pair[1]]]]
    components=list(range(10));chords=[]
    for left,right in edges:
        first,other=components[left],components[right]
        if first==other:chords.append((left,right))
        else:components=[first if component==other else component for component in components]
    assert len(chords)==6
    passing=[]
    for point in range(64):
        adj=[1<<(site^1) for site in range(20)]
        for left,right in edges:
            bit=1^(point>>chords.index((left,right))&1) if (left,right) in chords else 1
            for endpoint in (0,1):
                first=2*left+endpoint;second=2*right+(endpoint^bit);adj[first]|=1<<second;adj[second]|=1<<first
        if next(independent_sets(adj,(1<<20)-1,8),None) is None:passing.append((point,adj))
    assert len(passing)==1
    point,adj=passing[0];print('independent physical reconstruction; tree-normalized unique role',point,'chords',chords,'sites',sites,'g6',to_graph6(adj));return adj


def covering(graph,orders,limit):
    allmask=(1<<len(graph))-1
    crossing=[n&~(1<<(idx^1)) for idx,n in enumerate(graph)]
    witnesses=[mask for order in orders for mask in independent_sets(graph,allmask,order)];counts=Counter();keep=[]
    for size in range(limit+1):
        for column in independent_sets(crossing,allmask,size):
            if all(column&mask for mask in witnesses):
                counts[size]+=1;keep.append(column)
    print('orders',orders,'mandatory sets',len(witnesses),'passing independent-on-crossings columns',sorted(counts.items()));return keep


def small():
    adj=[2,1,8,4]; survivors=covering(adj,[2],4)
    assert set(survivors)=={3,7,11,12,13,14,15}
    print('two restored verticals, mandatory transversals and optional double contacts: PASS')


if __name__=='__main__':
    if sys.argv[1]=='control':small()
    else:
        adj=materialize(); poles=covering(adj,[7],9)
        Path('missing_pole.rows').write_text(''.join(f'{mask}\n' for mask in poles))
