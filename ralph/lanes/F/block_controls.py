"""Explicit labelled oracle on eight vertices; adversarial tests for the source and bound checker."""

from itertools import combinations
from pathlib import Path

from block_audit import lines, source, support_total
from cyclic_check import read_base,check


def rejects(label,action):
    try: action()
    except (AssertionError,IndexError): print('REJECT',label,flush=True)
    else: raise AssertionError(label+' unexpectedly accepted')


def oracle():
    size=8
    edge_orbits=set()
    for left,right in combinations(range(size),2):
        edge_orbits.add(tuple(sorted({(left,right),tuple(sorted((left^1,right^1)))})))
    assert len(edge_orbits)==16
    masks=[sum(1<<vertex for vertex in subset) for subset in combinations(range(size),4)]
    direct={}
    for bits in range(1<<len(edge_orbits)):
        adjacent=[0]*size
        for index,orbit in enumerate(sorted(edge_orbits)):
            if (bits>>index)&1:
                for left,right in orbit:
                    adjacent[left]|=1<<right;adjacent[right]|=1<<left
        if any(adjacent[left]&adjacent[right] for left,right in combinations(range(size),2) if adjacent[left]&(1<<right)):continue
        base=[[(adjacent[2*left]>>(2*right)&3).bit_count() for right in range(4)] for left in range(4)]
        if any(base[left][right]!=base[left^1][right^1] for left in range(4) for right in range(4)):continue
        key=tuple(map(tuple,base))
        score=sum(all(not adjacent[vertex]&mask for vertex in range(size) if mask&(1<<vertex)) for mask in masks)
        direct[key]=min(score,direct.get(key,score))
    rows=lines('bismall.q'); bounds=lines('bismall.fcert');status=lines('bismall.log')
    assert len(direct)==112 and len(status)==len(bounds)==len(rows)==40
    matches=0
    for index,(text,line,record) in enumerate(zip(rows,status,bounds)):
        base=read_base(text);expected=direct[tuple(map(tuple,base))];ident,decision,*rest=line.split(); assert int(ident)==index
        assert decision==('yes' if expected==0 else 'no');ident,*entries=record.split();assert int(ident)==index
        bound=support_total(base,4,entries);assert bound<=expected
        matches+=bound==expected
    print('PASS 65536 labelled graphs; 112 eligible two-block quotients; all 40 representative zero decisions correct;',
          matches,'unconditional bounds attain their exact optimum')


def mutations():
    receipts=lines('bismall.maps');replay=lambda changed:source('bismall',[],'counts.small','B',receipts=changed)
    rejects('missing affine orbit',lambda:replay(receipts[:-1]))
    rejects('duplicate affine orbit',lambda:replay(receipts+[receipts[-1]]))
    fields=receipts[-1].split();fields[-1]='0,0,0,0'
    rejects('invalid isomorphism',lambda:replay([*receipts[:-1],' '.join(fields)]))
    base=read_base(lines('small.q')[0]);_,*entries=lines('small.fcert')[0].split()
    rejects('duplicate support',lambda:support_total(base,4,entries+[entries[0]]))
    full,single,weight=entries[0].split(':')
    rejects('inflated multiplicity',lambda:support_total(base,4,[f'{full}:{single}:{int(weight)+1}']))
    cycle=[[0]*4 for _ in range(4)]
    for index in range(4):cycle[index][(index+1)%4]=cycle[(index+1)%4][index]=1
    rejects('non-forced four-cycle',lambda:support_total(cycle,4,['0:15:2']))
    sample=read_base(lines('ctl.q')[5]);assert sample[0][0]==0
    original=Path('hardproof/0313');wrong=Path('hardproof/0317');stem=Path('mutated')
    for extension in ['.cnf','.trace','.lrat']:
        stem.with_suffix(extension).write_bytes((wrong if extension=='.lrat' else original).with_suffix(extension).read_bytes())
    rejects('crossed target LRAT',lambda:check(lines('target.q')[313],10,stem))


if __name__=='__main__':
    assert __debug__;oracle();mutations()
