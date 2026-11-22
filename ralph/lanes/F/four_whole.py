"""Static four-way compatibility: every pole column here consists of whole fibers."""
from collections import Counter
from functools import lru_cache
from itertools import combinations,combinations_with_replacement
from pathlib import Path

from cyclic_check import read_base
from four_slot import put,shapes
from orbit_extend import independent


def price():
    base=read_base(Path('col53.q').read_text().strip());size=len(base);allmask=(1<<size)-1
    adjacency=[sum(1<<other for other in range(size) if other!=site and row[other]) for site,row in enumerate(base)]
    columns=[]
    for row in Path('col53.rows').read_text().splitlines():
        full,single,number,stage=map(int,row.split());assert single==0 and number==2*full.bit_count() and stage==3
        columns.append(full)
    assert len(columns)==24
    @lru_cache(None)
    def alpha(mask):
        if not mask:return 0
        bit=mask&-mask;return max(alpha(mask^bit),1+alpha(mask&~(bit|adjacency[bit.bit_length()-1])))
    @lru_cache(100000)
    def forced(holes,available,threshold):
        choices=holes&available
        subset=choices
        while True:
            if independent(subset,adjacency):
                rest=available^subset;pending=subset
                while pending:
                    bit=pending&-pending;pending^=bit;rest &= ~adjacency[bit.bit_length()-1]
                if 2*subset.bit_count()+alpha(rest)>=threshold:return True
            if not subset:return False
            subset=(subset-1)&choices
    def rotate(mask,step):return ((mask<<step)|(mask>>(size-step)))&allmask
    assert all(rotate(mask,1) in columns for mask in columns)
    counts=Counter();good=[];cover=[];small=[]
    for quartet in combinations_with_replacement(sorted(columns),4):
        orbit={tuple(sorted(rotate(mask,step) for mask in quartet)) for step in range(size)}
        if quartet!=min(orbit):continue
        weight=len(orbit);counts['all quartets']+=weight;counts['rotation reps']+=1
        if any(a&b&c for a,b,c in combinations(quartet,3)):continue
        holes=quartet[0]|quartet[1]|quartet[2]|quartet[3]
        if forced(holes,allmask,10):continue
        counts['pure old surviving quartets']+=weight
        if any(forced(holes,allmask^mask,9) for mask in quartet):continue
        counts['one-pole surviving quartets']+=weight
        mandatory=0;edges=list(combinations(range(4),2))
        for index,(left,right) in enumerate(edges):
            if forced(holes,allmask&~(quartet[left]|quartet[right]),8):mandatory|=1<<index
        occupied=sum((1<<index) for index,(left,right) in enumerate(edges) if quartet[left]&quartet[right]);options=[]
        for flags in range(64):
            if mandatory&~flags or flags&occupied:continue
            graph=[0]*4
            for index,(left,right) in enumerate(edges):
                if flags>>index&1:graph[left]|=1<<right;graph[right]|=1<<left
            if not all(independent(row,graph) for row in graph):continue
            if any(2*mask.bit_count()+row.bit_count()>9 for mask,row in zip(quartet,graph)):continue
            edgecount=144-holes.bit_count()+2*sum(mask.bit_count() for mask in quartet)+flags.bit_count()
            if edgecount<161:continue
            failed=False
            for subset in (7,11,13,14,15):
                if not independent(subset,graph):continue
                rest=allmask
                for pole in range(4):
                    if subset>>pole&1:rest &=~quartet[pole]
                if forced(holes,rest,10-subset.bit_count()):failed=True;break
            if not failed:options.append(flags)
        if options:
            counts['quad surviving quartets']+=weight;good.append(' '.join(map(str,(*quartet,*options))))
        cover.append(' '.join(map(str,(*quartet,weight,mandatory,occupied,len(options)))))
    put('whole53.cover',cover);put('whole53.good',good);print(sorted(counts.items()),'open reps',len(good))


if __name__=='__main__':price()
