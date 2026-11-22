"""Independent physical/semantic reconstruction of the seven-window reduction."""
from collections import Counter
from itertools import combinations,product
from pathlib import Path
import subprocess

from orbit_extend import ROOT


def adjacent(left,right):return (right-left)%18 in {6,7,8,9,10,11,12}


def cyclelaw():
    passed=0
    for first,second,third in product((0,1),repeat=3):
        graph={(0,2+first),(1,2+(1^first)),(0,4+second),(1,4+(1^second)),(2,4+third),(3,4+(1^third))}
        if any(set(combinations(triple,2))<=graph for triple in combinations(range(6),3)):continue
        for left,right in product((0,1),(2,3)):
            if (left,right) in graph:continue
            assert [site for site in (4,5) if (left,site) in graph]==[site for site in (4,5) if (right,site) in graph]
        passed+=1
    assert passed==4
    for crossing in (0,1):
        for contacts in range(16):
            if contacts&3==3 or contacts&12==12:continue
            if any(contacts>>left & contacts>>(2+(left^crossing)) & 1 for left in range(2)):continue
            transversals=[1<<left | 1<<(2+(left^crossing^1)) for left in range(2)]
            assert not all(contacts & choice for choice in transversals)
    print('physical triangle projection: 4/8 lifts triangle-free; both nonedge mates cannot be hit by a triangle-free singleton column')


def geometry():
    center=0; remote=[site for site in range(18) if adjacent(center,site)]; core=[site for site in range(18) if site!=center and site not in remote]
    remote_edges=[pair for pair in combinations(remote,2) if adjacent(*pair)]; [roots]=remote_edges
    assert all(sum(adjacent(site,root) for root in roots)==1 for site in core)
    core_edges=[pair for pair in combinations(core,2) if adjacent(*pair)]; assert len(core_edges)==15
    assert all(left in range(1,6) and right in range(13,18) for left,right in core_edges)
    tested=0
    for left,right in core_edges:
        first={site for site in remote if adjacent(left,site)};second={site for site in remote if adjacent(right,site)}
        for matching in (0,1):
            words=[dict(zip(remote,word)) for word in product((0,1),repeat=7) if word[0]^word[-1]!=matching]
            for values in product((0,1),repeat=len(first|second)):
                pinned=dict(zip(sorted(first|second),values))
                if pinned[roots[0]]^pinned[roots[1]]==matching:continue
                chosen=next((word for word in words if all(word[site]==value for site,value in pinned.items())),None);assert chosen is not None
                assert all((chosen[site]^1)==(value^1) for site,value in pinned.items());tested+=1
    print('all 15 bad-edge types: both physical seven-transversals re-constructed;',tested,'compatible pin patterns')
    for distance in (1,2,3):
        window=list(range(8));holes={2,2+distance}; others=sorted(set(window)-holes)
        assert all(not adjacent(hole,site) for hole in holes for site in window if site!=hole)
        forest=[pair for pair in combinations(others,2) if adjacent(*pair)]; assert len(forest)==3
        for matching in product((0,1),repeat=3):
            assert any(all((word[others.index(left)]^word[others.index(right)])!=sign for (left,right),sign in zip(forest,matching)) for word in product((0,1),repeat=6))
    fullpeers=[site for site in core if min(site,18-site)>=4]
    assert fullpeers==[4,5,13,14] and all(adjacent(left,right) or min(right-left,18-(right-left))<=3 for left,right in combinations(fullpeers,2))
    print('three short-hole controls positive for all 8 local signings each; every two possible further full sites incompatible')
    return core,core_edges


def audit(core,edges):
    clauses=[]
    for left,right in combinations(range(1,11),2):clauses.append((-left,-right))
    for position,(left,right) in enumerate(edges,11):clauses.append((-position,1+core.index(left),1+core.index(right)))
    for omitted in core:clauses.append(tuple(11+index for index,edge in enumerate(edges) if omitted not in edge))
    rows=Path('no_blind_pole.cnf').read_text().splitlines();assert rows[0]=='p cnf 25 70'
    assert all(row.endswith(' 0') for row in rows[1:]);actual=[tuple(map(int,row.split()[:-1])) for row in rows[1:]]
    assert Counter(tuple(sorted(clause)) for clause in actual)==Counter(tuple(sorted(clause)) for clause in clauses)
    for name,args,expect in [('lrat-check',[],'c VERIFIED'),('cake_lpr',['--CML_HEAP_SIZE=256','--CML_STACK_SIZE=32'],'s VERIFIED UNSAT')]:
        result=subprocess.run([ROOT/'opt/bin'/name,*args,'no_blind_pole.cnf','no_blind_pole.lrat'],text=True,capture_output=True);assert result.returncode==0 and expect in result.stdout.splitlines()
    print('independent edge order/omitted-site CNF comparison and two proof checkers PASS')


if __name__=='__main__':cyclelaw();audit(*geometry())
