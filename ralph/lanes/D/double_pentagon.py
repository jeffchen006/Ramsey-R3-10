"""Internal ten-vertex adjacencies for two vertex-disjoint marked pentagons."""
from collections import Counter
from itertools import combinations,product
from pathlib import Path
import sys
from kernel_cnf import ROOT,decode


def orbit(rows):
    reflect=lambda vertex:(-vertex)%5
    columns=tuple(sum(1<<idx for idx,row in enumerate(rows) if row>>pos&1) for pos in range(5))
    return min(tuple(sum(1<<(reflect(site) if reverse else site) for site in range(5) if word[(reflect(idx) if flip else idx)]>>site&1) for idx in range(5)) for word in (rows,columns) for flip,reverse in product((False,True),repeat=2))


def catalog():
    edges=[1<<((idx-1)%5)|1<<((idx+1)%5) for idx in range(5)];weak=edges[0];allowed=[mask for mask in range(32) if mask&weak!=weak and all(not(mask>>idx&1 and mask&edges[idx]) for idx in range(5))];profiles=Counter()
    for rows in product(allowed,repeat=5):
        if rows[1]&rows[4] or any(rows[idx]&rows[(idx+1)%5] for idx in range(5)):continue
        cols=[sum(1<<idx for idx,row in enumerate(rows) if row>>site&1) for site in range(5)];graph=[edges[idx]|(rows[idx]<<5) for idx in range(5)]+[(edges[site]<<5)|cols[site] for site in range(5)]
        if any((first&second).bit_count()>3 for first,second in combinations(graph,2)):continue
        profiles[orbit(rows)]+=1
    assert all(8%size==0 for size in profiles.values());return profiles


def planted():
    witnessed=Counter();pairings=Counter();uncoupled=0
    for text in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        edges=decode(text);graph=[{second if first==site else first for first,second in edges if site in (first,second)} for site in range(22)]
        if {len(row) for row in graph}!={6} or any(len(first&second)>3 for first,second in combinations(graph,2)):continue
        flags=[]
        for first,second in combinations(range(22),2):
            common=graph[first]&graph[second]
            if len(common)!=1:continue
            centre=next(iter(common));pentagons=[(centre,first,left,right,second) for left in graph[first]-common for right in graph[left]&graph[second]-common];flags.append(((centre,first,second),pentagons))
        for (first,left),(second,right) in combinations(flags,2):
            if set(first)&set(second):continue
            found=0
            for a,b in product(left,right):
                if set(a)&set(b):continue
                found+=1;rows=tuple(sum(1<<idx for idx,site in enumerate(b) if site in graph[vertex]) for vertex in a);witnessed[orbit(rows)]+=1
            pairings[found]+=1
            if not found:uncoupled+=1
    return witnessed,pairings


if __name__=='__main__':
    root=Path(sys.argv[1]);full=catalog();control,pairs=planted();assert control and set(control)<=full.keys();print('structural internal matrices',sum(full.values()),'orbits',len(full),'C22 disjoint flag pairs',sum(pairs.values()),'with NO disjoint pentagon closure',pairs[0],'actual marked pentagon pairs',sum(control.values()),'occupied orbits',len(control));print('orbit count by cross edges',sorted(Counter(sum(mask.bit_count() for mask in key) for key in full).items()));(root/'interfaces.tsv').write_text(''.join(' '.join(map(str,(*key,size,control[key])))+'\n' for key,size in sorted(full.items())))
