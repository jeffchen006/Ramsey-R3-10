"""Independent sparse boundary check of the shared prism receipts and final repricing."""
from collections import Counter
from functools import lru_cache
from itertools import combinations
from pathlib import Path

from column_audit import insert,normal
from marked_joint import read,count
from marked_replay import reverse_count
from orbit_extend import vertices


def finish():
    adj=[sum(1<<idx for idx in range(17) if 6<=abs(idx-site)<=12) for site in range(17)]
    edges=[(left,right) for right in range(17) for left in range(right) if adj[left]>>right&1];labels={edge:2<<idx for idx,edge in enumerate(edges)};triangle={}
    for sites in combinations(range(17),3):
        sides=list(combinations(sites,2))
        if all(edge in labels for edge in sides):insert(triangle,sum(labels[edge] for edge in sides))
    @lru_cache(None)
    def components(mask):
        groups=[]
        while mask:
            group=mask&-mask
            while True:
                nxt=group
                for site in vertices(group):nxt|=adj[site]&mask
                if nxt==group:break
                group=nxt
            mask^=group;groups.append(group)
        return groups
    @lru_cache(None)
    def cycle(mask):
        assert mask.bit_count()==9
        slow={};forms=[]
        for left,right in edges:
            if not (mask>>left&mask>>right&1):continue
            endpoints=(1<<left)|(1<<right);word=labels[left,right]
            while endpoints:
                level=endpoints.bit_length()
                if level not in slow:slow[level]=(endpoints,word);break
                prior,letter=slow[level];word^=letter;endpoints^=prior
            if not endpoints:forms.append(normal(triangle,word))
        values=set(forms)-{0};assert len(values)==1;return values.pop()
    allrows=set(read('wpole.rows'));left=set(read('prism.rows'));cuts=set()
    for occupied,doubles,weight,first,second,third in read('prism.rejects'):
        key=occupied,doubles,weight;assert key not in cuts;cuts.add(key)
        assert cycle(first)^cycle(second)^cycle(third)==0
        for support in (first,second,third):
            assert not support&doubles
            for group in components(support):assert len(components(group&occupied))<=1
    assert not cuts&left and cuts|left==allrows
    pilot=[line.split() for line in Path('pilot.results').read_text().splitlines()];ruled={tuple(map(int,row[:3])) for row in pilot if row[3]=='I'};assert len(ruled)==96 and ruled<=allrows
    cyclic=(sum(1<<idx for idx in range(5,12)),0,1)
    for tag,cover in [('shared',left),('final',left-ruled)]:
        rows=sorted((set(read('wmark.rows'))&cover)-{cyclic});poles=sorted(cover)
        for name,domain in [('mark',rows),('pole',poles)]:Path(tag+name+'.rows').write_text(''.join(' '.join(map(str,row))+'\n' for row in domain))
        print(tag,'mark reps/labels',len(rows),sum(row[2] for row in rows),'external reps/labels',len(poles),sum(row[2] for row in poles),'full-site strata',sorted(Counter(row[1].bit_count() for row in poles).items()))
        summary=count(17,10,adj,rows,poles);verdict=reverse_count(tag+'mark.rows',tag+'pole.rows');assert verdict==[summary[idx,'orbits'] for idx in range(3)];print(tag,'joint sum',sum(verdict))
    print('distinct checked three-face cuts',len(cuts),'rank-pilot additional',len(ruled-cuts),'overlap',len(ruled&cuts),'unresolved pilot',len(pilot)-len(ruled))


if __name__=='__main__': finish()
