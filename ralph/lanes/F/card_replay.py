"""Read-only independent source, deletion, counting and finite proof replay."""

from hashlib import sha256
from itertools import combinations, product
from math import comb
from pathlib import Path
import json

from cyclic_check import check, read_base, rank
from odd_check import verify
from orbit_extend import parse_graph6, independent_sets


def lines(name):
    return Path(name).read_text().splitlines()


def restrictions(base, absent):
    return [[weight for column, weight in enumerate(row) if column not in absent]
            for index, row in enumerate(base) if index not in absent]


def minimum_occupied(base, target=10):
    for number in range(target//2,-1,-1):
        for full in combinations(range(len(base)),number):
            if any(base[left][right] for left in full for right in full):continue
            free=sum(vertex not in full and all(not base[vertex][other] for other in full) for vertex in range(len(base)))
            if free >= target-2*number:return target-number
    raise AssertionError('unreachable')


def costs(base):
    edges = {ending:1<<index for index,ending in enumerate(pair for pair in combinations(range(19),2) if base[pair[0]][pair[1]]==1)}
    equations=[]
    for triple in combinations(range(19),3):
        parts=list(combinations(triple,2))
        if all(pair in edges for pair in parts):equations.append(sum(edges[pair] for pair in parts))
    signed = len(edges)-rank(equations)
    switch_rank=rank((1<<left)|(1<<right) for left,right in edges)
    return signed,signed-switch_rank


def ceildiv(value,denom):
    return (value+denom-1)//denom


def replay():
    sources=lines('card.q');maps=lines('r8.bind');previous=lines('../r8/ctl.q');older=lines('../r8/ctl.log')
    expected={};raw=0;impossible=0
    for halves in product(range(3),repeat=9):
        if sum(halves)!=4:continue
        raw+=1
        word=(0,)+halves+halves[::-1]
        bad=next(((0,step,alt) for step in range(1,19) if word[step]==2 for alt in range(1,19) if word[alt] and word[(alt-step)%19]),None)
        if bad is not None:
            assert len(set(bad))==3
            impossible+=1
            continue
        representative=min(tuple(word[unit*step%19] for step in range(19)) for unit in range(1,19))
        expected[representative]=expected.get(representative,0)+1
    assert len(sources)==len(maps)==len(expected)==27 and raw==414 and impossible==171
    childrows=lines('card.core.q');holes=lines('card.core.maps');pack=lines('card.core.odd');outputs=lines('card.core.out')
    assert len(childrows)==len(holes)==len(pack)==len(outputs)==243
    proof_receipt=[];numeric=[];signed_cost=[0]*4;missing_min=[10**9]*3
    audited=set();sourcecerts=lines('card.odd');assert len(sourcecerts)==27
    for index,text in enumerate(sources):
        base=read_base(text);word=tuple(base[0]);assert all(base[left][right]==word[(right-left)%19] for left in range(19) for right in range(19))
        orbit=expected.pop(word)
        ident,old,image=maps[index].split();image=list(map(int,image.split(',')));old=int(old)
        actual=read_base(previous[old]);assert int(ident)==index and sorted(image)==list(range(19)) and all(base[left][right]==actual[image[left]][image[right]] for left in range(19) for right in range(19))
        rawsigns,gauge=costs(base);assert f'free={gauge}' in older[old].split() and 'status=no' in older[old].split()
        for pos,value in enumerate([2**rawsigns,2**gauge,orbit*2**rawsigns,orbit*2**gauge]):signed_cost[pos]+=value
        ident,*pieces=sourcecerts[index].split();assert int(ident)==index and verify(text,10,pieces)>=25
        stem=Path('proof')/f'{index:03}'
        count=check(text,10,stem)
        proof_receipt.append(' '.join(map(str,[index,old,orbit,count,sha256(text.encode()).hexdigest(),*[sha256(stem.with_suffix(ext).read_bytes()).hexdigest() for ext in ('.trace','.cnf','.lrat')]])))
        lb=[]
        for dist in range(1,10):
            child=index*9+dist-1
            assert tuple(map(int,holes[child].split()))==(index,0,dist)
            assert read_base(childrows[child])==restrictions(base,{0,dist})
            ident,*tokens=pack[child].split();row,reported,*_=map(int,outputs[child].split());assert int(ident)==row==child
            result=verify(childrows[child],10,tokens);assert result==reported>=1;lb.append(result)
            for shift in range(19):audited.add((index,*sorted([shift,(shift+dist)%19])))
        occ=minimum_occupied(base)
        full=ceildiv(19*sum(lb),comb(19-occ,2));one=ceildiv(2*sum(lb),18-occ);two=min(lb)
        numeric.append(f'{index} {orbit} {rawsigns} {gauge} {occ} {full} {one} {two} '+','.join(map(str,lb)))
        missing_min=[min(value,oldvalue) for value,oldvalue in zip([full,one,two],missing_min)]
    assert not expected and audited=={(index,left,right) for index in range(27) for left,right in combinations(range(19),2)}
    print('independent source / raw structurally invalid / quotient classes',raw,impossible,len(sources))
    print('signed TF counts: profile reps labelled/gauged, all distance words labelled/gauged:',*signed_cost)
    print('card floors for zero, one, two holes',*missing_min)
    for path,receipt in [('proof.receipt',proof_receipt),('core.receipt',numeric)]:Path(path).write_text('\n'.join(receipt)+'\n')
    oldgraphs=lines('../r6/sparse.distinct.g6');reasons=lines('r6.bind');assert len(reasons)==len(oldgraphs)==33
    for index,(reason,line) in enumerate(zip(reasons,oldgraphs)):
        physical=parse_graph6(line);degrees=sorted(map(int.bit_count,physical));assert len(degrees)==38 and degrees!=[8]*38
        assert reason==f'{index} degree-invariant '+','.join(map(str,degrees))
    for tag,flag in [('positive',True),('adverse',False)]:
        record,=json.loads(Path(tag+'.gate').read_text())['graphs'];assert record['ok']==flag and record['n']==12
        graph=parse_graph6(lines(tag+'.g6')[0]);assert (next(independent_sets(graph,4095,6),None) is None)==flag
    lane=Path(__file__).resolve().parent
    for name,edges in [('round4_seed40_24.g6',178),('round4_seed40_24_e179.g6',179)]:
        graph=parse_graph6(lines(lane/name)[0]);assert sum(map(int.bit_count,graph))==2*edges and sum(1 for _ in independent_sets(graph,2**40-1,10))==24
        print('unchanged outside control',edges,24)
    print('actual weighted R8 maps 27; R6 impossible degree invariants 33; dual zero proofs 27; projected pairs bound',len(audited))


if __name__=='__main__':
    assert __debug__
    replay()
