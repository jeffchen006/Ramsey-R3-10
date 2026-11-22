"""Verify fully bound physical independent transversals, without producer paths."""
from collections import Counter
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path

from marked_bank_check import consume, insert
from marked_joint import read


def board(tag):
    if tag == 'pilot':
        return 17,10,[(left,right) for right in range(17) for left in range(right) if 6<=right-left<=12]
    if tag == 'pin':return 6,5,[(2,3)]
    assert tag in {'s'+str(mask) for mask in range(8)} | {'old'}
    mask=0 if tag=='old' else int(tag[1:])
    return 3,5,[edge for index,edge in enumerate([(0,1),(0,2),(1,2)]) if mask>>index&1]


def verify(tag, text=None):
    size,target,edges=board(tag); sites=range(size); vertices=range(2*size)
    ledger=iter((Path(tag+'.trace').read_text() if text is None else text).splitlines())
    bank=set(map(int,Path(tag+'.bank').read_text().split()));letters={edge:2<<idx for idx,edge in enumerate(edges)}
    initial={};stats=Counter();statuses=Counter();cuts=[]
    for triple in combinations(sites,3):
        sides=list(combinations(triple,2))
        if all(side in letters for side in sides):insert(initial,sum(letters[side] for side in sides))
    @lru_cache(None)
    def project(eligible):
        coords={vertex//2:1<<(64+vertex//2) for vertex in eligible};system={}
        for (left,right),letter in letters.items():
            if left in coords and right in coords:insert(system,letter^coords[left]^coords[right])
        for vertex in eligible:
            if vertex^1 not in eligible:insert(system,coords[vertex//2]^(vertex%2))
        return tuple(word for word in system.values() if word<1<<64)
    def site_mask(values):return sum(1<<site for site in set(values))
    def adjacent(first,second):return tuple(sorted((first//2,second//2))) in letters
    rows=read(tag+'.rows');assert len(set(row[:2] for row in rows))==len(rows)
    for row in rows:
        occupied,doubled,weight=row; assert 0<=occupied<1<<size and doubled&occupied==doubled and doubled.bit_count()==2
        contact={vertex for vertex in vertices if (doubled if vertex%2 else occupied)>>(vertex//2)&1}
        header=next(ledger).split();assert header[0]=='begin' and len(header)==6
        occ,full,low,high,missing=map(int,header[1:]);assert (occ,full)==row[:2] and (low|high)<1<<size
        assert {vertex for vertex in vertices if (high if vertex%2 else low)>>(vertex//2)&1}==contact,'row contact'
        absent={site for site in sites if {2*site,2*site+1}<=contact}
        assert missing==site_mask(absent),'missing vertical'
        space=initial.copy()
        for first,second in combinations(sorted(contact),2):
            if adjacent(first,second):insert(space,letters[first//2,second//2]^(first%2)^(second%2))
        triangle=1 in space;forced=False;num=0
        for event in ledger:
            fields=event.split()
            if fields[0]=='end':
                assert len(fields)==3 and int(fields[-1])==num and fields[1]==('triangle' if triangle else 'I' if forced else 'open')
                statuses[fields[1]]+=1
                if triangle or forced:cuts.append(row)
                break
            assert fields[0]=='step' and len(fields)==7 and not (triangle or forced),'unbound step'
            mode,padding,support,low,high,advertised=map(int,fields[1:])
            assert mode in (0,1,2,4) and 0<=padding<1<<size and support in bank and 0<=support<1<<size
            padded={vertex for vertex in vertices if padding>>(vertex//2)&1}
            assert len(padded)+(mode==1)==mode and mode+support.bit_count()==target
            for first,second in combinations(sorted(padded),2):
                if first//2==second//2:assert first//2 in absent,'unjustified vertical'
                else:assert not adjacent(first,second),'inter-padding edge'
            assert not padding&support,'reused site'
            eligible=frozenset(vertex for vertex in vertices if support>>(vertex//2)&1 and not (mode==1 and vertex in contact) and all(not adjacent(vertex,other) for other in padded))
            assert site_mask(vertex//2 for vertex in eligible)==support,'unavailable site'
            assert (low,high)==tuple(site_mask(vertex//2 for vertex in eligible if vertex%2==parity) for parity in (0,1)),'endpoint pins'
            equations=[word for word in project(eligible) if consume(space,word)]
            assert bool(equations)==bool(advertised) and all(not consume(space,word^advertised) for word in equations),'projected equations'
            if advertised:
                assert 1<advertised<1<<(1+len(edges)) and consume(space,advertised^1),'false unit'
                insert(space,advertised^1);assert 1 not in space
            else:forced=True
            stats[mode]+=1;num+=1
        else:raise ValueError('missing end')
    assert next(ledger,None) is None
    if text is None:
        Path(tag+'.checked').write_text(''.join('%d %d %d\n'%row for row in cuts));print(tag,'outcomes',sorted(statuses.items()),'steps',sorted(stats.items()))
    return set(cuts)
