"""Rebuild the unsigned domain from full sites first; check the retained forest/window receipts."""
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import sys

from marked_joint import read, reflection
from marked_windows import floor
from orbit_extend import vertices


def verify(size,target,stem,win,external):
    everything=(1<<size)-1
    adj=[sum(1<<idx for idx in range(size) if (abs(idx-site)==1 if size==3 else 6<=abs(idx-site)<=12)) for site in range(size)]
    def neighborhood(positions):
        neighbors=0
        for site in vertices(positions): neighbors |= adj[site]
        return neighbors
    def peel(mask,pins):
        free=mask&~pins
        while free:
            leaves=sum(1<<site for site in vertices(free) if (adj[site]&(free|pins)).bit_count()<=1)
            if not leaves:return False
            free^=leaves
        return True
    required={}
    for count in range((target-1)//2+1):
        for group in combinations(range(size),count):
            holes=sum(1<<idx for idx in group);neighbors=neighborhood(holes)
            if holes&neighbors:continue
            eligible=tuple(vertices(everything&~(holes|neighbors)))
            for num in range(min(len(eligible),target-1-2*count)+1):
                for singles in combinations(eligible,num):
                    occupied=holes+sum(1<<idx for idx in singles)
                    pair=occupied,holes;other=reflection(occupied,size),reflection(holes,size)
                    if pair<=other:required[pair]=1+(pair!=other)
    original=len(required),sum(required.values());residual={}
    for occupied,holes,weight in read(stem+'.rows'):
        assert required.pop((occupied,holes))==weight;residual[occupied,holes]=weight
    for occupied,holes,weight,reason,support,forest in read(stem+'.rejects'):
        assert required.pop((occupied,holes))==weight
        if reason==1:assert support&~holes==0 and not forest&(support|neighborhood(support)) and peel(forest,0) and forest.bit_count()+2*support.bit_count()>=target
        elif reason==2:assert not external and holes and not forest&occupied and peel(forest,0) and forest.bit_count()+2>=target
        elif reason==3:assert (occupied^holes).bit_count()+1>=target
        else:assert reason==4 and not support&holes and 1+support.bit_count()==target and peel(support,support&occupied)
    assert not required
    survivors={}
    for occupied,holes,weight in read(win+'.rows'):
        assert residual.pop((occupied,holes))==weight;survivors[occupied,holes]=weight
    ways=Counter()
    for line in Path(win+'.rejects').read_text().splitlines():
        occ,hol,wei,mode,sub,kraw,nraw,eraw,lraw=line.split(); occupied,holes,weight,chosen=map(int,(occ,hol,wei,sub));singles=occupied^holes
        assert residual.pop((occupied,holes))==weight and chosen&~singles==0
        base={'both':2,'pole':1+chosen.bit_count(),'holes':2*holes.bit_count()+chosen.bit_count()}[mode]
        assert mode=='pole' or holes and (mode!='both' or not external and not chosen)
        selected=[];mates=set()
        for site in range(size):
            bit=1<<site
            if not bit&occupied:
                if mode=='holes' and adj[site]&holes:continue
                hits=(adj[site]&chosen).bit_count()
                if hits<2:selected.append((site,2-hits))
            elif bit&singles and not bit&chosen and mode!='both':selected.append((site,1));mates.add(site)
        order=sum(num for site,num in selected);edges=sum(num==2 for site,num in selected)
        for (left,leftweight),(right,rightweight) in combinations(selected,2):
            if adj[left]>>right&1 and not (left in mates and right in mates):edges+=min(leftweight,rightweight)
        threshold=target-base;limit=floor(threshold,order) if threshold>0 else 999
        assert [threshold,order,edges,limit]==list(map(int,(kraw,nraw,eraw,lraw))) and edges<limit;ways[mode]+=1
    assert not residual
    print(stem,'triangle-admissible',original,'final',len(survivors),sum(survivors.values()),'GR receipts',sorted(ways.items()))


def reverse_count(mark_path='wmark.rows',pole_path='wpole.rows'):
    size=17;adj=[sum(1<<idx for idx in range(size) if 6<=abs(idx-site)<=12) for site in range(size)]
    saturated=sum(1<<site for site in range(size) if adj[site].bit_count()==7)
    cyclic=sum(1<<idx for idx in range(5,12));mark=read(mark_path);poles=read(pole_path);first=[]
    for occ,holes,weight in mark:
        if occ==cyclic and holes==0:continue
        first.append((occ,holes,weight==1))
        if weight==2:first.append((reflection(occ,size),reflection(holes,size),False))
    anyhit=[0]*size;full=[0]*size;canhit=mirror=0;universe=(1<<len(first))-1
    for serial,(occ,holes,fixed) in enumerate(first):
        unit=1<<serial
        for site in vertices(occ):anyhit[site]|=unit
        for site in vertices(holes):full[site]|=unit
        if occ.bit_count()+holes.bit_count()<=8:canhit|=unit
        if fixed:mirror|=unit
    @lru_cache(None)
    def union(mask,kind):
        if not mask:return 0
        bit=mask&-mask;return union(mask^bit,kind)|(anyhit if kind==1 else full)[bit.bit_length()-1]
    labels=[0,0,0];fixed=[0,0,0]
    for occ,holes,weight in poles:
        degree=occ.bit_count()+holes.bit_count();sets=[universe&~union(saturated&occ,2),canhit&~(union(holes,1)|union(occ,2)),canhit&~union(occ,1)]
        for mult,mask in enumerate(sets):
            if degree+mult>=10 or (not holes and mult<2 and degree+mult>=9):continue
            labels[mult]+=weight*mask.bit_count()
            if weight==1:fixed[mult]+=(mirror&mask).bit_count()
    print('changed row only, reversed pair count', 'labels',labels,'fixed',fixed,'orbits',[(left+right)//2 for left,right in zip(labels,fixed)])
    orbits=[(left+right)//2 for left,right in zip(labels,fixed)]
    if mark_path=='wmark.rows':assert orbits==[452132922,357649573,38099207]
    return orbits


if __name__=='__main__':
    if sys.argv[1]=='control':verify(3,4,'small','wsmall',False);verify(3,4,'smallpole','wspole',True)
    else:verify(17,10,'full','wmark',False);verify(17,10,'pole','wpole',True);reverse_count()
