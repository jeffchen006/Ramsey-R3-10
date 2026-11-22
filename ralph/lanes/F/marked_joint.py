"""Count unsigned row/footprint pairs under one simultaneous reflection, not two."""
from itertools import combinations, product
from pathlib import Path
from collections import Counter
import sys

from orbit_extend import vertices


def reflection(word,size): return int(f'{word:0{size}b}'[::-1],2)


def read(path):return [tuple(map(int,line.split())) for line in Path(path).read_text().splitlines()]


def count(size,target,oldadj,rows,feet):
    ranked=[]; fixed=0
    for occupied,doubles,weight in feet:
        reverse=reflection(occupied,size),reflection(doubles,size); assert (occupied,doubles)<=reverse and weight==1+((occupied,doubles)!=reverse)
        if weight==1:fixed |= 1<<len(ranked)
        ranked.append((occupied,doubles))
        if weight==2:ranked.append(reverse)
    assert len(set(ranked))==len(ranked)
    anyhit=[0]*size; fullhit=[0]*size; eligible=[0]*3
    for serial,(occupied,doubles) in enumerate(ranked):
        bit=1<<serial; degree=occupied.bit_count()+doubles.bit_count()
        for site in vertices(occupied):anyhit[site]|=bit
        for site in vertices(doubles):fullhit[site]|=bit
        for multiplicity in range(3):
            if degree+multiplicity<target and not(degree+multiplicity==target-1 and not doubles and multiplicity<=1):eligible[multiplicity]|=bit
    def exclude(mask,sites,data):
        for site in vertices(sites):mask &= ~data[site]
        return mask
    stats=Counter(); highs=sum(1<<idx for idx,neighbors in enumerate(oldadj) if neighbors.bit_count()+2>=target-1)
    for occupied,doubles,weight in rows:
        degree=occupied.bit_count()+doubles.bit_count()
        for multiplicity in range(3):
            if multiplicity and degree+1>=target:continue
            hits=eligible[multiplicity]
            if not multiplicity:hits=exclude(hits,doubles&highs,anyhit)
            elif multiplicity==1:hits=exclude(exclude(hits,doubles,anyhit),occupied,fullhit)
            else:hits=exclude(hits,occupied,anyhit)
            labelled=hits.bit_count(); bothfixed=(hits&fixed).bit_count() if weight==1 else 0
            assert (weight*labelled+bothfixed)%2==0
            stats[multiplicity,'labels']+=weight*labelled;stats[multiplicity,'fixed']+=bothfixed;stats[multiplicity,'orbits']+=(weight*labelled+bothfixed)//2
    return stats


def control():
    size=2;target=4;adj=[2,1];roster=[];lab=[]
    for word in product(range(3),repeat=size):
        occupied=sum(1<<idx for idx,num in enumerate(word) if num);full=sum(1<<idx for idx,num in enumerate(word) if num==2)
        if sum(word)>3 or any(word[idx]==2 and word[1-idx] for idx in range(2)):continue
        lab.append(word)
        other=reflection(occupied,size),reflection(full,size)
        if (occupied,full)<=other:roster.append((occupied,full,1+((occupied,full)!=other)))
    census=count(size,target,adj,roster,roster);actual=[set() for _ in range(3)]
    def admissible(first,second,mult):
        if sum(second)+mult>3 or (sum(second)+mult==3 and mult<2 and 2 not in second):return False
        if mult and sum(first)>=3:return False
        for left,right in zip(first,second):
            if left==2 and right:return False  # here both ordinary sites already have one ordinary neighbor
            if mult and left and right==2:return False
            if mult==2 and left and right:return False
        return True
    for first,second,mult in product(lab,lab,range(3)):
        if admissible(first,second,mult):actual[mult].add((first,second))
    for mult,bucket in enumerate(actual):
        assert len(bucket)==census[mult,'labels'] and len({min((left,right),(left[::-1],right[::-1])) for left,right in bucket})==census[mult,'orbits']
    order=[0,4,2,6,3,7,1]; graph=[sum(1<<idx for idx,dest in enumerate(order) if (dest-src)%8 in (1,4,7)) for src in order]
    def physical(graph):
        first=tuple((graph[0] & (3<<shift)).bit_count() for shift in (2,4)); second=tuple((graph[6]&(3<<shift)).bit_count() for shift in (2,4));mult=(graph[6]&3).bit_count()
        triangle=any(graph[left]&graph[right] for left,right in combinations(range(7),2) if graph[left]>>right&1)
        bad=any(all(not(graph[left]>>right&1) for left,right in combinations(support,2)) for support in combinations(range(7),4));return first,second,mult,triangle,bad
    left,right,mult,triangle,bad=physical(graph);assert not triangle and not bad and (left,right) in actual[mult];print('physical C8-puncture',left,right,mult,triangle,bad)
    for idx in (0,1):graph[idx]|=1<<6;graph[6]|=1<<idx
    left,right,mult,triangle,bad=physical(graph);assert triangle
    # Force an ordinary overlap at the same time as a double contact on the mark.
    graph[6]|=1<<4;graph[4]|=1<<6
    left,right,mult,triangle,bad=physical(graph);assert triangle and (left,right) not in actual[mult]; print('broken physical',left,right,mult,triangle,bad)
    print('independent labelled pair loop and simultaneous orbit sets match',sorted(census.items()))


if __name__=='__main__':
    if sys.argv[1]=='control':control()
    else:
        rows=read('wmark.rows');feet=read('wpole.rows'); size=17;adj=[sum(1<<other for other in range(size) if 6<=abs(other-site)<=12) for site in range(size)]
        if sys.argv[1]=='pilot':rows=rows[::64]
        for tag,roster in [('all',rows),('cyclic', [row for row in rows if row[:2]==(sum(1<<idx for idx in range(5,12)),0)])]:
            print(tag,sorted(count(size,10,adj,roster,feet).items()))
