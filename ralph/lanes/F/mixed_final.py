"""Join the static lower bounds, odd packings, and all threshold-tree frontiers."""

from collections import Counter
from hashlib import sha256
from pathlib import Path

from cyclic_check import read_base
from mixed_queue import queue
from split_check import check as split_check
from odd_check import check as odd_check,verify
from block_score_check import count
from orbit_extend import parse_graph6


def lines(name):return Path(name).read_text().splitlines()


def rejects(name,callback):
    try:callback()
    except (AssertionError,StopIteration,ValueError):print('REJECT',name)
    else:raise RuntimeError('accepted mutation: '+name)


def audit():
    queue();odd_check('short.q',10,'short');rows=lines('short.q');identities=lines('short.ids')
    levels=[int(line.split()[1]) for line in lines('short.out')];submitted=dict(enumerate(levels));parents=list(range(len(rows)));stats=[]
    for parent,child in [('short','branch'),('branch','deep'),('deep','last')]:
        selected=[index for index,value in enumerate(levels) if value<25]
        assert list(map(int,lines(parent+'.remain')))==selected
        assert lines(child+'.q')==[rows[parents[index]] for index in selected]
        parents=[parents[index] for index in selected];leaves=lines(child+'.tree');log=lines(child+'.out');levels,counts,depths=split_check(lines(child+'.q'),10,leaves,log,25)
        for index,bound in zip(parents,levels):submitted[index]=max(submitted[index],bound)
        stats.append((child,len(parents),sum(value>=25 for value in levels),sum(counts),max(depths)))
    assert min(submitted.values())>=25 and len(identities)==len(submitted)
    with open('threshold.receipt','w') as out:
        for index,text in enumerate(rows):print(index,identities[index],sha256(text.encode()).hexdigest(),submitted[index],file=out)
    forced=[int(line.split()[1]) for line in lines('target.forced')];static=sum(value>=25 for value in forced);assert static+sum(identity.startswith('new ') for identity in identities)==len(forced)
    print('CERTIFIED BOUND COMPOSITION',static,'static;',len(rows),'other proofs including',sum(line.startswith('old ') for line in identities),'old overlaps;',stats)
    print('All',len(forced),'new proof inputs and all seven mapped previous inputs have lower bound >=25.')


def mutation_tests():
    source=lines('small.q');raw=lines('small4.odd');index=next(index for index,line in enumerate(raw) if ' C' in line);tokens=raw[index].split()[1:];conflict=next(token for token in tokens if token.startswith('C'))
    rejects('overdrawn support capacity',lambda:verify(source[index],4,[conflict]*100))
    rejects('one missing odd-circuit member',lambda:verify(source[index],4,[conflict.rsplit(':',1)[0]]))
    last=lines('last.tree');text=lines('last.q');out=lines('last.out')
    rejects('truncated decision cover',lambda:split_check(text,10,last[:-1],out,25))
    changed=last.copy();pos=next(index for index,line in enumerate(changed) if line.startswith('B'));changed[pos]='B 0 0'
    rejects('zero split character',lambda:split_check(text,10,changed,out,25))
    rejects('wrong leaf total',lambda:split_check(text,10,[line.replace('L 25 ','L 26 ',1) if line.startswith('L 25 ') else line for line in last],out,25))
    rejects('mismatched root',lambda:split_check(text[::-1],10,last,out,25))


def scores():
    for tag,order in [('small',5),('mid',7),('pilot',10),('branch',10)]:
        rows=lines(tag+'.q');reached=[];gains=0;best=None
        for line in lines(tag+'.score'):
            index,edges,old,new,_,_,before,after=line.split();index=int(index);reached.append(index);matrix=read_base(rows[index]);assert sum(map(sum,matrix))==int(edges)
            long=2*len(matrix)//5;rot=[start+(pos+1)%length for start,length in [(0,long),(long,long),(2*long,long//2)] for pos in range(length)]
            for value,text,invariant in [(int(old),before,True),(int(new),after,False)]:
                graph=parse_graph6(text);assert len(graph)==2*len(matrix)
                for left in range(len(graph)):
                    for fiber in range(len(matrix)):assert ((graph[left]>>(2*fiber))&3).bit_count()==matrix[left//2][fiber]
                    for right in range(len(graph)):
                        edge=(graph[left]>>right)&1;assert edge==((graph[left^1]>>(right^1))&1) and (not edge or not graph[left]&graph[right])
                        if invariant:assert edge==((graph[2*rot[left//2]+left%2]>>(2*rot[right//2]+right%2))&1)
                assert value==count(graph,order)
            assert int(new)<=int(old);gains+=int(new)<int(old);key=(int(new),int(edges),index);best=key if best is None else min(best,key)
        assert reached==list(map(int,lines(tag+'.scoreids')))
        print('NEARNESS',tag,'matched',len(reached),'strict improvements',gains,'best (score,edge count,row)',best)


if __name__=='__main__':assert __debug__;audit();mutation_tests();scores()
