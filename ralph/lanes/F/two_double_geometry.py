"""Inventory legal outside sites for the four-endpoint pad; no signing input."""
from collections import Counter
from itertools import combinations

from marked_joint import read
from two_double_check import board


def outside(tag,padded):
    size,target,edges=board(tag);sites=set(range(size));inside={site for site in sites if padded>>site&1}
    assert len(inside)==2
    safe=sorted(sites-inside-{site for edge in edges if inside.intersection(edge) for site in edge})
    return safe,len(list(combinations(safe,target-4)))


if __name__=='__main__':
    assert outside('s0',3)==([2],1) and outside('s1',5)==([],0)
    for mask,num in sorted(Counter(row[1] for row in read('pilot.open')).items()):
        safe,total=outside('pilot',mask);assert total==0;print(mask,num,'rows; eligible zero-based sites',safe,'size-six supports',total)
