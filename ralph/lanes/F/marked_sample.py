"""A stratified price of row-independent exterior cuts; no signing or joint-header scan."""
from collections import Counter, defaultdict
from hashlib import sha256
from pathlib import Path
import subprocess
import sys

from column_audit import replay
from marked_joint import read
from orbit_extend import ROOT, vertices
from relift_audit import encode


def bucket(rows):
    groups=defaultdict(list)
    for occupied,doubles,weight in rows:groups[doubles.bit_count(),occupied.bit_count()+doubles.bit_count()].append((occupied,doubles,weight))
    return [entry for key in sorted(groups) for entry in sorted(groups[key],key=lambda row: sha256(str(row).encode()).digest())[:4]]


def run(control):
    size,target=(3,4) if control else (17,10)
    sample=[(5,0,1),(0,0,1),(1,1,2),(5,1,2)] if control else bucket(read('wpole.rows'))
    join=Path('join').resolve(); banks=defaultdict(list)
    for occupied,doubles,weight in sample:banks[doubles].append((occupied,doubles,weight))
    prefix='small' if control else 'pilot'; sums=Counter();results=[]
    for doubles,rows in sorted(banks.items()):
        ordinary=[site for site in range(size) if not doubles>>site&1]
        def mask(sites):return sum(1<<idx for idx,site in enumerate(ordinary) if sites>>site&1)
        def edge(left,right):return abs(left-right)==1 if control else 6<=abs(left-right)<=12
        graph=[[int(left==right or edge(left,right)) for right in ordinary] for left in ordinary]
        group=prefix+str(doubles);Path(group+'.q').write_text(encode(graph)+'\n');requests=[];local={}
        for occupied,full,weight in rows:
            name=f'{occupied}_{full}';local[name]=(occupied,full,weight);entry=[name,1,0,mask(occupied^full),0]
            if full:
                restored=min(vertices(full));feet=mask(sum(1<<site for site in ordinary if edge(site,restored)))
                assert not feet&mask(occupied)
                entry=[name,3,3,mask(occupied^full),0,feet,0,feet,feet]
            requests.append(' '.join(map(str,entry)))
        Path(group+'.requests').write_text('\n'.join(requests)+'\n')
        outcome=subprocess.run([join,group+'.q',str(target),group+'.requests',group+'.trace','8'],capture_output=True,text=True,check=True)
        replay(group+'.q',target,group+'.requests',group+'.trace')
        for line in outcome.stdout.splitlines():
            name,status,steps=line.split();occupied,full,weight=local.pop(name);assert status in ('open','I')
            results.append(' '.join(map(str,[occupied,full,weight,status,steps])));sums[full.bit_count(),status]+=1
        assert not local
    Path(prefix+'.results').write_text('\n'.join(results)+'\n');print(len(sample),'columns in',len(banks),'base groups; per-full outcomes',sorted(sums.items()))
    if control:
        assert any(row.startswith('5 0 1 open ') for row in results) and any(row.startswith('0 0 1 I ') for row in results)


if __name__=='__main__':run(sys.argv[1]=='control')
