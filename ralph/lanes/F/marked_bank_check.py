"""Receipt checker from physical lift equations, not the searcher's tree paths."""
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import sys


def consume(pivots, word):
    while word:
        prior=pivots.get(word.bit_length())
        if prior is None:break
        word^=prior
    return word


def insert(pivots,word):
    reduced=consume(pivots,word)
    if reduced:pivots[reduced.bit_length()]=reduced


def verify(tag, rows, bankfile, tracefile):
    size,threshold=(3,4) if tag in ('small','tamper') else (17,10)
    def matched(left,right):return abs(left-right)==1 if size==3 else 6<=abs(left-right)<=12
    edges=[(left,right) for right in range(size) for left in range(right) if matched(left,right)]
    letter={edge:2<<idx for idx,edge in enumerate(edges)}
    for left,right in edges:assert (size-1-right,size-1-left) in letter
    initial={}
    for triangle in combinations(range(size),3):
        sides=list(combinations(triangle,2))
        if all(side in letter for side in sides):insert(initial,sum(letter[side] for side in sides))
    @lru_cache(None)
    def projection(support,pinned):
        system={}; low={}
        for (left,right),sign in letter.items():
            if support>>left&support>>right&1:insert(system,sign^(1<<(64+left))^(1<<(64+right)))
        for site in range(size):
            if pinned>>site&1:insert(system,(1<<(64+site))^1)
        for row in system.values():
            if row<(1<<64):insert(low,row)
        return tuple(low.values())
    bank=set(map(int,Path(bankfile).read_text().split()));ledger=iter(Path(tracefile).read_text().splitlines());checked=[];stats=Counter();steps=Counter();occupied_seen=set()
    for raw in Path(rows).read_text().splitlines():
        occupied,doubles,weight=map(int,raw.split());assert not doubles and occupied not in occupied_seen;occupied_seen.add(occupied)
        space=initial.copy()
        for (left,right),sign in letter.items():
            if occupied>>left&occupied>>right&1:insert(space,sign)
        assert 1 not in space
        done=False;num=0
        for event in ledger:
            first,typ,*data=event.split();assert int(first)==occupied
            if typ=='end':
                status,nsteps=data;assert status in ('I','open') and (status=='I')==done and int(nsteps)==num
                if done:checked.append(raw)
                stats[status]+=1;steps[num]+=1;break
            poles,support,advertised=map(int,data)
            assert typ=='step' and not done and poles in (0,1) and support in bank and support.bit_count()+poles==threshold and 0<=support<1<<size
            forms=projection(support,(occupied&support) if poles else 0)
            reduced=[form for form in forms if consume(space,form)]
            assert bool(reduced)==bool(advertised) and all(not consume(space,form^advertised) for form in reduced)
            if advertised:
                assert 1<advertised<(1<<(len(edges)+1)) and consume(space,advertised^1)
                insert(space,advertised^1);assert 1 not in space
            else:done=True
            num+=1
        else:raise ValueError('incomplete receipt')
    assert next(ledger,None) is None
    if tag=='small':assert checked==['0 0 1']
    Path(tag+'.checked').write_text(''.join(line+'\n' for line in checked))
    print('physical projection replay',tag,'outcomes',sorted(stats.items()),'deductions',sum(num*count for num,count in steps.items()),'range',min(steps),max(steps),'cached systems',projection.cache_info())


def tamper():
    prior=Path('small.trace').read_text();assert '5 step 1 7 6' in prior
    Path('forged.trace').write_text(prior.replace('5 step 1 7 6','5 step 1 7 0'))
    try:verify('tamper','small.rows','small.bank','forged.trace')
    except AssertionError:print('wrong forced contradiction on positive site labels rejected')
    else:raise AssertionError('forged receipt accepted')


if __name__=='__main__':
    if sys.argv[1]=='tamper':tamper()
    else:verify(*sys.argv[1:])
