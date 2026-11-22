"""Check two-pentagon marginal receipts using Python integers, without an LP solver."""
from itertools import combinations
from functools import lru_cache
from pathlib import Path
import json
import sys


def verify(folder):
    totals={};cuts=[]
    for ordinal,(entry,witness) in enumerate(zip((folder/'interfaces.tsv').read_text().splitlines(),(folder/'margins.jsonl').read_text().splitlines(),strict=True)):
        rows=list(map(int,entry.split()[:5]));data=json.loads(witness);assert data['index']==ordinal;weak={(1,4),(6,9)}
        edges={tuple(sorted((base+point,base+(point+1)%5))) for base in (0,5) for point in range(5)}|{(left,right+5) for left in range(5) for right in range(5) if rows[left]>>right&1}
        stars=[{last if first==point else first for first,last in edges if point in (first,last)} for point in range(10)]
        masks=[mask for mask in range(1024) if all(not((mask>>first)&(mask>>last)&1) for first,last in edges|weak)]
        conditions=[]
        def put(faces,low,high):
            require=sum(1<<site for site in faces);conditions.extend([(require,1,high),(require,-1,-low)])
        put([],30,30)
        for site,star in enumerate(stars):put([site],9-len(star),9-len(star))
        for first,last in combinations(range(10),2):
            if (first,last) in edges:continue
            shared=len(stars[first]&stars[last]);low,high=(1,1) if (first,last) in weak else (2,3);put([first,last],low-shared,high-shared)
        status=data['status'];totals[status]=1+totals.get(status,0)
        if status=='rational-feasible':
            counts={masks[int(idx)]:amount for idx,amount in data['primal'].items()};scale=data['scale'];assert scale>0 and min(counts.values())>=0
            for face,sign,bound in conditions:assert sign*sum(value for mask,value in counts.items() if face&mask==face)<=scale*bound
        else:
            assert status=='excluded';costs={mask:0 for mask in masks};maximum=0
            for idx,weight in data['dual'].items():
                assert weight>0;face,sign,bound=conditions[int(idx)];maximum+=weight*bound
                for mask in masks:
                    if mask&face==face:costs[mask]+=weight*sign
            margin=sum(min(0,30*value) for value in costs.values())-maximum;assert margin==data['margin'] and margin>0;cuts.append(ordinal)
    assert totals=={'excluded':30,'rational-feasible':1626};print('PASS all 1656 arithmetic receipts with separately constructed sets, sums and no scipy.',totals);print('excluded interface indices:',*cuts)


if __name__=='__main__':verify(Path(sys.argv[1]))
