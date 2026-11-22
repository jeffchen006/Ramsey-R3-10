"""Boolean degree-two necessary equations and a source-level XOR receipt."""
from collections import Counter,defaultdict
from itertools import combinations,product,permutations
from pathlib import Path
import subprocess,sys

from column_audit import normal,insert,put,replay,parse_request
from cyclic_check import read_base
from relift_audit import encode,explicit_lift
from orbit_extend import independent_sets,vertices


def polynomial(first,second):
    result=0
    for left in vertices(first^1):
        for right in vertices(second^1):
            small,big=sorted((left,right));pos=big*(big+1)//2+small if 0<small<big else big*(big+1)//2
            result^=1<<pos
    return result


def contradiction(rows):
    basis={}
    for index,(_,_,first,second) in enumerate(rows):
        value=polynomial(first,second);proof=1<<index
        while value>1:
            pivot=value.bit_length()-1
            if pivot not in basis:basis[pivot]=value,proof;break
            prior,mask=basis[pivot];value^=prior;proof^=mask
        if value==1:return list(vertices(proof))
    return None


def fix_space(base,feet,tops,unit):
    keys={(left,right):0 for right in range(len(base)) for left in range(right) if base[left][right]};keys={edge:2<<idx for idx,edge in enumerate(keys)};space={}
    for triple in combinations(range(len(base)),3):
        sides=list(combinations(triple,2))
        if all(edge in keys for edge in sides):insert(space,sum(keys[edge] for edge in sides))
    for foot,high in zip(feet,tops):
        for left,right in combinations(vertices(foot),2):
            if (left,right) in keys:insert(space,keys[left,right]^(((high>>left)^(high>>right))&1))
    for form in unit:insert(space,form^1)
    assert 1 not in space;return keys,space


def verifyflat(bind,scope,feet,tops,edges,row):
    flags,mask,first,second=row;sites=list(vertices(mask));poles=list(vertices(flags));assert len(sites)+len(poles)==scope and len(feet)>=flags.bit_length()
    assert all(not(edges>>(right*(right-1)//2+left)&1) for left,right in combinations(poles,2));keys,space=bind;lift={}
    for left,right in combinations(sites,2):
        if (left,right) in keys:insert(lift,keys[left,right]^(1<<(64+left))^(1<<(64+right)))
    for index in poles:
        for site in vertices(feet[index]&mask):insert(lift,(1<<(64+site))^(1-((tops[index]>>site)&1)))
    flat={};proposed={}
    for pivot,value in lift.items():
        if pivot<1<<64:insert(flat,normal(space,value))
    for value in (first,second):insert(proposed,normal(space,value))
    assert len(flat)==len(proposed)==2 and 1 not in flat and all(not normal(flat,value) for value in proposed.values())


def analyze(basepath,order,prefix):
    replay(basepath,order,prefix+'.request',prefix+'.trace');base=read_base(Path(basepath).read_text().strip());groups=defaultdict(list);units=defaultdict(list)
    for line in Path(prefix+'.flat').read_text().splitlines():
        name,*words=line.split();groups[name].append(tuple(map(int,words)))
    for line in Path(prefix+'.trace').read_text().splitlines():
        if ' step ' in line:
            name,_,_,_,raw=line.split();units[name].append(int(raw))
    stats=Counter();proofs=[]
    for line in Path(prefix+'.request').read_text().splitlines():
        name,edges,feet,tops=parse_request(line);rows=groups[name];bind=fix_space(base,feet,tops,units[name]);indices=contradiction(rows);chosen=range(len(rows)) if indices is None else indices
        for idx in chosen:verifyflat(bind,order,feet,tops,edges,rows[idx]);
        if indices is not None:
            parity=set()
            for idx in indices:
                for left,right in product(vertices(rows[idx][2]^1),vertices(rows[idx][3]^1)):
                    monomial=frozenset((left,right))-{0};parity.symmetric_difference_update([frozenset(monomial)])
            assert parity=={frozenset()};proofs.append(' '.join(map(str,(name,*indices))))
        stats['open' if indices is None else 'I']+=1;print(name,'rank2',len(rows),'XOR',None if indices is None else len(indices))
    put(prefix+'.xor',proofs);print('quadratic',dict(stats))


def checksmall():
    matrix=[[int(left==right or (left<2)!=(right<2)) for right in range(5)] for left in range(5)]
    put('qsmall.q',[encode(matrix)]);put('qsmall.request',['ramsey 0 0']);subprocess.run(['./join2','qsmall.q','5','qsmall.request','qsmall.trace','4','qsmall.flat'],check=True)
    analyze('qsmall.q',5,'qsmall');rows=[list(map(int,line.split()[1:])) for line in Path('qsmall.flat').read_text().splitlines()];assert len(rows)==1
    first,second=rows[0][2:];valid=0
    for word in range(64):
        point=(word<<1)|1;graph=explicit_lift(matrix,iter(1-((word>>idx)&1) for idx in range(6)));known=next(independent_sets(graph,1023,5),None) is None
        assert known==bool((first&point).bit_count()%2 or (second&point).bit_count()%2);valid+=known
    assert valid==48
    synthetic=[(0,0,first^a,second^b) for a,b in product(range(2),repeat=2)]
    assert len(contradiction(synthetic))==4 and contradiction(synthetic[:-1]) is None
    print('K2,3 crossing lift: 48/64 strict order-10 positives, 16 literal I5; all four quadrants XOR to one, three do not.')


def pilot():
    rows={line.split()[0]:line for line in Path('quartet.request').read_text().splitlines()};opens=[row.split()[0] for row in Path('quartet.result').read_text().splitlines() if row.split()[1]=='open'];assert len(opens)==54
    put('quadpilot.request',[rows[key] for key in opens[:2]]);put('quadall.request',[rows[key] for key in opens])


if __name__=='__main__':
    if sys.argv[1]=='analyze':analyze(sys.argv[2],int(sys.argv[3]),sys.argv[4])
    else:{'control':checksmall,'pilot':pilot}[sys.argv[1]]()
