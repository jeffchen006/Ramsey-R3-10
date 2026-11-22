"""Reroot the four-defect triangle-plus-pendant shape at its alternating C6."""
from itertools import combinations
from pathlib import Path
import sys
from defect_triangle import catalog,raw


def build(root):
    folder=root/'pendant';folder.mkdir(exist_ok=True)
    for order,degree in [(22,6),(40,9)]:
        source,_=catalog(order,degree,1);rows=[];positions=[]
        for key in sorted(source):
            _,fixed,*graph=map(int,raw(key).split());low=[0]*order
            for left,right in combinations(range(6),2):
                if (graph[left]&graph[right]).bit_count()==1:low[left]|=1<<right;low[right]|=1<<left
            weak=[index for index in range(3) if low[index]>>(index+3)&1]
            if len(weak)!=1 or sum(mask.bit_count() for mask in low)!=8:continue
            rows.append(' '.join(map(str,(fixed,*graph,*low))));positions.append(weak[0])
        (folder/f'c{order}.in').write_text('\n'.join(rows)+'\n');print(order,'complete triangle templates',len(source),'pendant',len(rows),'root placements',positions.count(0),positions.count(1),positions.count(2))


if __name__=='__main__':build(Path(sys.argv[1]))
