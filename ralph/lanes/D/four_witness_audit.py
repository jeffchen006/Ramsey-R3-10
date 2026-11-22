"""Alternative census: place the two unique witnesses, then fill only double cells."""

from collections import Counter
from itertools import combinations,product
from pathlib import Path
import sys

from defect_four import CROSS,MAPS,PERMS
from induced_pilot import line
from punct_path import pairs,profile_key


def audit(dest,order,degree):
    expected={shape:set((dest/f'four-{order}-{shape}.in').read_text().splitlines()) for shape in (0,1,3,6,7)}
    found={shape:set()for shape in expected};labelled=0
    for shape in range(16):
        graph=[0]*4
        for idx,(a,b)in enumerate(CROSS):
            if shape>>idx&1:graph[a]|=1<<b;graph[b]|=1<<a
        demand=[1-(graph[a]&graph[b]).bit_count() for a,b in ((0,1),(2,3))]
        if min(demand)<0:continue
        doubles=[(1<<a)|(1<<b)for a,b in CROSS if not graph[a]>>b&1]
        witness=[[mask for mask in range(16)if mask&part==part and not any(mask>>point&1 and mask&graph[point]for point in range(4))] if need else [0] for part,need in zip((3,12),demand)]
        images=[]
        for perm,trans in zip(PERMS,MAPS):
            newshape=0
            for idx,(a,b)in enumerate(CROSS):
                if shape>>idx&1:newshape|=1<<CROSS.index(tuple(sorted((perm[a],perm[b]))))
            images.append((newshape,trans))
        canonical=min(score for score,_ in images);transforms=[trans for score,trans in images if score==canonical]
        for left,right in product(*witness):
            if (left==15)!=(right==15):continue
            fixed=Counter([15] if left==15 else [mask for mask in (left,right)if mask]);ranges=[]
            for mask in doubles:
                a,b=[point for point in range(4)if mask>>point&1];used=(graph[a]&graph[b]).bit_count()+sum(size for support,size in fixed.items()if support&mask==mask);ranges.append(range(max(0,1-used),4-used))
            for amounts in product(*ranges):
                table=fixed+Counter(dict(zip(doubles,amounts)))
                for point in range(4):table[1<<point]=degree-graph[point].bit_count()-sum(size for mask,size in table.items()if mask>>point&1)
                table[0]=order-4-sum(table.values())
                if min(table.values())<0:continue
                labelled+=1;key=min(tuple(sorted((trans[mask],size)for mask,size in table.items()if size))for trans in transforms)
                rows=[0]*4
                for idx,(a,b)in enumerate(CROSS):
                    if canonical>>idx&1:rows[a]|=1<<b;rows[b]|=1<<a
                for mask,size in key:
                    for _ in range(size):
                        site=len(rows);rows.append(mask)
                        for point in range(4):
                            if mask>>point&1:rows[point]|=1<<site
                found[canonical].add(' '.join(map(str,(15,*rows))))
    assert found==expected,(order,{shape:(len(found[shape]),len(expected[shape]))for shape in found});print('PASS witness-first',order,'labelled',labelled,'per-shape exact byte sets',{shape:len(keys)for shape,keys in found.items()})


if __name__=='__main__':
    for order,degree in ((22,6),(40,9)):audit(Path(sys.argv[1]),order,degree)
