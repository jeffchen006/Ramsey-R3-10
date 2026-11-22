"""An exact low pair marks two vertices. Both are admissible single hubs."""
import argparse
from collections import Counter,defaultdict
from itertools import combinations
from pathlib import Path


def cover(source,out,size):
    eligible=defaultdict(set)
    for text in source.read_text().splitlines():
        hub,key=text.split(' ',1);eligible[key].add(int(hub).bit_length()-1)
    stats=Counter()
    with out.open('w') as output:
        for key,sites in sorted(eligible.items()):
            masks=[int(term.split(':')[0]) for term in key.split() for _ in range(int(term.split(':')[1]))];order=len(masks)+size
            graph=[0]*size+masks
            def add(first,second):graph[first]|=1<<second;graph[second]|=1<<first
            add(0,1)
            for point in range(2,size):
                add(point%2,point)
                if point+1<size:add(point,point+1)
            for point,mask in enumerate(masks,size):
                for anchor in range(size):
                    if mask>>anchor&1:add(point,anchor)
            forbidden={(first,second)for first,second in combinations(range(size),2) if not graph[first]>>second&1 and (graph[first]&graph[second]).bit_count()==1}
            options=list(combinations(sorted(sites),2))+[(point,point+1)for point in sorted(sites)if point>=size and point+1<order and graph[point]==graph[point+1]]
            for first,second in options:
                stats['raw']+=1
                if forbidden and forbidden!={(first,second)}:continue
                if graph[first]>>second&1 or (graph[first]&graph[second]).bit_count()>1:continue
                if second<size and (graph[first]&graph[second]).bit_count()!=1:continue
                print((1<<first)|(1<<second),key,file=output);stats['kept']+=1
    print('source profile keys',len(eligible),dict(stats))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=Path);parser.add_argument('out',type=Path);parser.add_argument('--size',type=int,default=8);args=parser.parse_args();cover(args.source,args.out,args.size)
