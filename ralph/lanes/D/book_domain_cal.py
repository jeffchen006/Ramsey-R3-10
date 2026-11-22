"""Truth controls for static required/forbidden domain row search."""
from itertools import permutations,combinations
from pathlib import Path
import json,random,sys
from book_controls import bitset


def prepare(path):
    rng=random.Random(150212);c5=set()
    for seq in permutations(range(5)):
        c5.add(tuple(bitset((seq[(idx-1)%5],seq[(idx+1)%5])) for idx in map(seq.index,range(5))))
    assert len(c5)==12
    for order in [5,22]:
        population=(list(sorted(c5)) if order==5 else [row[2] for row in map(json.loads,(path/'cal.in').read_text().splitlines())]);samples=[];truth=[]
        for original in population:
            for attempt in range(10):
                fixed=rng.getrandbits(order) if order==5 else bitset(rng.sample(range(order),6));lo=[0]*order;ban=[0]*order
                for left,right in combinations(range(order),2):
                    if not fixed&(1<<left|1<<right) and rng.randrange(3):continue
                    val=original[left]>>right&1
                    if attempt>=5 and order==5 and rng.randrange(4)==0:val^=1
                    table=lo if val else ban;table[left]|=1<<right;table[right]|=1<<left
                if attempt>=5 and order==22:
                    group=rng.sample(range(order),7)
                    for left,right in combinations(group,2):ban[left]|=1<<right;ban[right]|=1<<left
                samples.append(' '.join(map(str,[fixed,*lo,*ban]))+'\n')
                truth.append(int(any(all(not((need&~row)|(row&blocked)) for need,blocked,row in zip(lo,ban,pattern)) for pattern in population)) if order==5 else int(attempt<5))
        (path/f'dom{order}.in').write_text(''.join(samples));(path/f'dom{order}.truth').write_text(''.join(str(val)+'\n'for val in truth))


def check(path):
    for order in [5,22]:
        expected=list(map(int,(path/f'dom{order}.truth').read_text().splitlines()));out=[line.split() for line in (path/f'dom{order}.out').read_text().splitlines() if not line.startswith('model')];assert len(out)==len(expected)
        for idx,((key,verdict,nodes,cpu),val) in enumerate(zip(out,expected)):assert int(key)==idx and int(verdict)==val,(idx,verdict,val)
        print('PASS',order,len(out),sum(expected),'positive')


if __name__=='__main__':(prepare if len(sys.argv)==2 else check)(Path(sys.argv[1]))
