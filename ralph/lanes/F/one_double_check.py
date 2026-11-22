"""Rebuild the independent-set equations from permitted physical vertices."""
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import sys

from marked_bank_check import consume, insert
from marked_joint import read


def edges_for(tag):
    if tag=='pilot':return 17,10,[(left,right) for right in range(17) for left in range(right) if 6<=right-left<=12]
    size,number=map(int,tag[1:].split('_'));edges=[(left,right) for right in range(size) for left in range(right)]
    return size,4,[edge for index,edge in enumerate(edges) if number>>index&1]


def verify(tag, trace=None, save=True):
    size,target,edges=edges_for(tag);ledger=iter((trace if trace is not None else Path(tag+'.trace').read_text()).splitlines())
    letter={edge:2<<index for index,edge in enumerate(edges)};initial={};out=[];stats=Counter();steps=Counter()
    for triple in combinations(range(size),3):
        sides=list(combinations(triple,2))
        if all(side in letter for side in sides):insert(initial,sum(letter[side] for side in sides))
    bank=set(map(int,Path(tag+'.bank').read_text().split()))
    @lru_cache(4096)
    def project(support,physical):
        system={};coordinates={site:1<<(64+site) for site in range(size) if support>>site&1}
        for (left,right),sign in letter.items():
            if left in coordinates and right in coordinates:insert(system,sign^coordinates[left]^coordinates[right])
        for site,coord in coordinates.items():
            ends=(physical>>(2*site))&3;assert ends
            if ends!=3:insert(system,coord^int(ends==2))
        return tuple(form for form in system.values() if form<(1<<64))
    for occupied,doubled,weight in read(tag+'.rows'):
        assert doubled.bit_count()==1 and doubled&occupied==doubled
        contact={2*site+bit for site in range(size) for bit in (0,1) if (occupied if not bit else doubled)>>site&1}
        header=next(ledger).split();assert header[0]=='begin' and len(header)==5
        occ,full,low,high=map(int,header[1:]);assert (occ,full)==(occupied,doubled)
        actual={2*site+bit for site in range(size) for bit in (0,1) if (high if bit else low)>>site&1};assert actual==contact and (low|high)<1<<size
        space=initial.copy();triangle=False;num=0;forced=False
        for (left,right),sign in letter.items():
            for first in (0,1):
                for second in (0,1):
                    if 2*left+first in contact and 2*right+second in contact:insert(space,sign^first^second)
        triangle=1 in space
        for event in ledger:
            parts=event.split()
            if parts[0]=='end':
                status=parts[1];assert len(parts)==3 and int(parts[2])==num and status==('triangle' if triangle else 'I' if forced else 'open')
                if triangle or forced:out.append((occupied,doubled,weight))
                stats[status]+=1;break
            assert parts[0]=='step' and len(parts)==5 and not (triangle or forced)
            mode,support,pins,advertised=map(int,parts[1:]);assert mode in (0,1,2) and support in bank and support.bit_count()+mode==target
            potential=set(range(2*size))
            if mode==1:potential-=contact
            if mode==2:
                pair={vertex for vertex in contact if vertex^1 in contact};assert len(pair)==2
                site=min(pair)//2;potential-=pair
                for left,right in edges:
                    if site in (left,right):
                        other=left+right-site;potential-=set((2*other,2*other+1))
            physical=sum(1<<vertex for vertex in potential if support>>(vertex//2)&1)
            slices=[(physical>>(2*site))&3 for site in range(size)]
            assert all(slices[site] for site in range(size) if support>>site&1)
            assert pins==sum(1<<site for site,ends in enumerate(slices) if ends==2) and 1 not in slices
            reduced=[word for word in project(support,physical) if consume(space,word)]
            assert bool(reduced)==bool(advertised) and all(not consume(space,word^advertised) for word in reduced)
            if advertised:
                assert 1<advertised<1<<(1+len(edges)) and consume(space,advertised^1)
                insert(space,advertised^1);assert 1 not in space
            else:forced=True
            steps[mode]+=1;num+=1
        else:raise ValueError('missing end')
    assert next(ledger,None) is None
    if save:Path(tag+'.checked').write_text(''.join('%s %s %s\n'%row for row in out));print(tag,'independent outcomes',sorted(stats.items()),'deductions by padding',sorted(steps.items()))
    return out


if __name__=='__main__':verify(sys.argv[1])
