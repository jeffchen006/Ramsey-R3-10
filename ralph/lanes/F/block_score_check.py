"""Independent memoized include/exclude witness scoring on the preregistered pilot rows."""

from functools import lru_cache
from pathlib import Path

from cyclic_check import read_base
from orbit_extend import parse_graph6


def count(graph, target):
    @lru_cache(None)
    def number(available, need):
        size=available.bit_count()
        if not need: return 1
        if size<need: return 0
        if need==1: return size
        vertex=(available&-available).bit_length()-1
        rest=available^(1<<vertex)
        return number(rest,need)+number(rest&~graph[vertex],need-1)
    result=number((1<<len(graph))-1,target);number.cache_clear();return result


if __name__=='__main__':
    assert __debug__
    for tag,scorelog,idfile in [('target','score_pilot.stdout','score.ids'),('bitarget','biscore_pilot.stdout','biscore.ids')]:
        rows=Path(tag+'.q').read_text().splitlines();indices=list(map(int,Path(idfile).read_text().splitlines()))
        reported=Path(scorelog).read_text().splitlines();assert len(reported)==len(indices)==len(set(indices))
        best=1<<62;gains=0
        for index,line in zip(indices,reported):
            fields=line.split('\t');assert len(fields)==8 and int(fields[0])==index
            start,score=map(int,fields[1:3]);assert score<=start
            graph=parse_graph6(fields[-1]);base=read_base(rows[index]);assert len(graph)==2*len(base)==40
            for left in range(40):
                for right in range(40):
                    assert (graph[left]>>right)&1==(graph[left^1]>>(right^1))&1
                    if graph[left]&(1<<right):assert not(graph[left]&graph[right])
                for fiber in range(20):assert ((graph[left]>>(2*fiber))&3).bit_count()==base[left//2][fiber]
            assert count(graph,10)==score
            best=min(best,score);gains+=start>score
        print('WITNESSES',tag,'rows',len(indices),'strict matched gains',gains,'best',best,flush=True)
