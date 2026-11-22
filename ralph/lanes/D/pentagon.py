"""All pentagon diagonal profiles, both direct and from marked planted graphs."""
from collections import Counter
from itertools import combinations,permutations,product
from pathlib import Path
import sys
from kernel_cnf import ROOT,decode


def bracelet(word):return min(tuple(t[(offset+step*idx)%5] for idx in range(5)) for offset in range(5) for step in (1,-1) for t in (word,))


def frame(order,degree,word):
    graph=[1<<((idx+1)%5)|1<<((idx-1)%5) for idx in range(5)];hist=Counter()
    for idx,num in enumerate(word):hist[(1<<((idx-1)%5))|(1<<((idx+1)%5))]=num
    for idx in range(5):hist[1<<idx]=degree-2-word[(idx-1)%5]-word[(idx+1)%5]
    hist[0]=order-5-sum(hist.values())
    if min(hist.values())<0:return None
    for mask,num in sorted(hist.items()):
        for _ in range(num):
            for idx in range(5):
                if mask>>idx&1:graph[idx]|=1<<len(graph)
            graph.append(mask)
    return ' '.join(map(str,[31,*graph]))


def verify(folder):
    graphs=(ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines();hits=Counter();allwords={bracelet(word) for word in product(range(3),repeat=5)}
    for text in graphs:
        edges=decode(text);graph=[{last if first==idx else first for first,last in edges if idx in (first,last)} for idx in range(22)]
        if {len(row) for row in graph}!={6} or any(len(left&right)>3 for left,right in combinations(graph,2)):continue
        for core in combinations(range(22),5):
            if any(len(graph[vertex]&set(core))!=2 for vertex in core):continue
            ordering=min((core[0],*tail) for tail in permutations(core[1:]) if all(second in graph[first] for first,second in zip((core[0],*tail),(*tail,core[0]))))
            word=tuple(len(graph[ordering[(idx-1)%5]]&graph[ordering[(idx+1)%5]])-1 for idx in range(5));base=frame(22,6,word);assert base
            hist=Counter(sum(1<<idx for idx,vertex in enumerate(ordering) if point in graph[vertex]) for point in range(22) if point not in core)
            assert hist==Counter(int(field)&31 for field in base.split()[6:]);hits[bracelet(word)]+=1
    for order,degree in [(22,6),(40,9)]:
        output=[];keys=[]
        for word in sorted(allwords):
            text=frame(order,degree,word)
            if text:output.append(text);keys.append(''.join(map(str,word)))
        (folder/f'c{order}.in').write_text('\n'.join(output)+'\n');(folder/f'c{order}.keys').write_text('\n'.join(keys)+'\n')
        if order==22:(folder/'pent-plants.tsv').write_text(''.join(f'{keys.index("".join(map(str,word)))} {count}\n' for word,count in sorted(hits.items())))
        print(order,'possible',len(keys),'marked control' if order==22 else '',(len(hits),sum(hits.values())) if order==22 else '')


if __name__=='__main__':verify(Path(sys.argv[1]))
