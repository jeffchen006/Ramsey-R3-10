"""Read-only independent source, role, capacity and certificate audit for R12."""

from collections import Counter
from hashlib import sha256
from itertools import combinations, combinations_with_replacement, permutations
from math import comb
import json
from pathlib import Path
import subprocess

from cyclic_check import check, read_base
from orbit_extend import ROOT, independent_sets, parse_graph6, to_graph6


def lines(name):
    return Path(name).read_text().splitlines()


def physical(text, graph, target):
    base=read_base(text);size=len(base)
    assert len(graph)==2*size
    for vertex,neighbors in enumerate(graph):
        assert all(not graph[other]&neighbors for other in range(2*size) if neighbors>>other&1)
        for other in range(2*size):
            assert (neighbors>>other&1)==(graph[vertex^1]>>(other^1)&1)
        assert all(((neighbors>>(2*site))&3).bit_count()==base[vertex//2][site] for site in range(size))
    assert next(independent_sets(graph,(1<<(2*size))-1,target),None) is None


def d(left,right):
    return min((left-right)%19,(right-left)%19)


def source(receipt):
    raw=Counter();simple=set();legal_double=set()
    for multi in combinations_with_replacement(range(1,10),4):
        weights=tuple(multi.count(step) for step in range(1,10))
        if max(weights)>2:continue
        raw['raw']+=1
        def weight(left,right):return weights[d(left,right)-1]
        illegal=any(tuple(sorted((weight(left,right),weight(left,end),weight(right,end)))) in ((1,1,2),(1,2,2),(2,2,2))
                    for left,right,end in combinations(range(19),3))
        if illegal:raw['illegal']+=1;continue
        (simple if max(weights)==1 else legal_double).add(weights)
    assert list(map(len,(simple,legal_double)))==[126,117] and raw=={'raw':414,'illegal':171}
    for kind,parents,unseen in [('simple',lines('parent.q')+lines('exception.q'),simple),('double',lines('../r11/card.q'),legal_double)]:
        for index,text in enumerate(parents):
            base=read_base(text);word=base[0][1:10]
            if kind=='double' and max(word)==1:continue
            assert all(base[left][right]==word[d(left,right)-1] for left,right in combinations(range(19),2))
            assert all(base[site][site]==int(kind=='simple') for site in range(19))
            images={tuple(word[d(0,unit*step)-1] for step in range(1,10)) for unit in range(1,19)}
            assert images<=unseen;unseen-=images
            if kind=='simple' and text==lines('exception.q')[0]:
                assert word==[0]*5+[1]*4;continue
            stem=Path('proof_parent' if kind=='simple' else '../r11/proof')/f'{index:03}'
            add_receipt(receipt,text,stem)
        assert not unseen
    print('verified 414 raw, 171 impossible, 126 simple and 117 double, 13+13 adverse root proofs')


def add_receipt(receipt,text,stem):
    supports=check(text,10,stem)
    receipt.append(' '.join([str(stem),sha256(text.encode()).hexdigest(),str(supports)]+[
        sha256(stem.with_suffix(ext).read_bytes()).hexdigest() for ext in ('.trace','.cnf','.lrat')]))


def roles(receipt):
    by_size=Counter();deficiencies=Counter();gated=[];parent=read_base(lines('exception.q')[0]);mapping=[]
    planted_raw=parse_graph6(lines('../r8/ctl.baseline.g6')[0]); pi=[site+19*side for site in range(19) for side in (0,1)]
    assert all(bool(planted_raw[left]>>right&1)==((right-left)%38 in (6,7,9,11,19,27,29,31,32)) for left in range(38) for right in range(38))
    planted=[sum(1<<index for index,other in enumerate(pi) if planted_raw[vertex]>>other&1) for vertex in pi]
    physical(lines('exception.q')[0],planted,10);same_signing=Counter()
    for amount in (1,2,3,4):
        inputs=lines(f'role{amount}.q'); files=Path(f'proof_role{amount}' if amount>1 else 'pilot_role1'); oldmap={}
        for line in lines(f'role{amount}.map'):
            *subset,index=map(int,line.split());tupled=tuple(subset);assert tupled not in oldmap;oldmap[tupled]=index
        for subset in combinations(range(19),amount):
            close=any(d(left,right)<4 for left,right in combinations(subset,2))
            if close and amount==4:continue
            index=oldmap.pop(subset);base=read_base(inputs[index]);holes={site for site in range(19) if not base[site][site]}
            images={(tuple(sorted((site*unit+offset)%19 for site in holes)),unit,offset) for unit in (-1,1) for offset in range(19)}
            unit,offset=next((unit,offset) for image,unit,offset in sorted(images) if image==subset)
            mapping.append(' '.join(map(str,(amount,*subset,index,unit,offset))))
            assert all(base[left][right]==parent[(left*unit+offset)%19][(right*unit+offset)%19] for left,right in combinations(range(19),2))
            if not close:
                by_size[amount]+=1
                deficits=[max(0,2-sum(d(sat,hole)>=6 for hole in subset)) for sat in range(19) if sat not in subset]
                assert sum(deficits)>0;deficiencies[amount,2*sum(deficits)]+=1
        assert not oldmap
        for index,text in enumerate(inputs):
            base=read_base(text);holes=[site for site in range(19) if not base[site][site]]
            stem=files/f'{index:03}';negative=any(d(left,right)<4 for left,right in combinations(holes,2))
            assert stem.with_suffix('.g6').exists()!=negative
            if negative:add_receipt(receipt,text,stem)
            else:
                candidate=parse_graph6(lines(stem.with_suffix('.g6'))[0]);physical(text,candidate,10);gated.append(to_graph6(candidate))
            one=planted[:]
            for hole in holes:
                one[2*hole]&=~(2<<(2*hole));one[2*hole+1]&=~(1<<(2*hole))
            planted_ok=next(independent_sets(one,(1<<38)-1,10),None) is None
            same_signing[amount,negative,planted_ok]+=1
            assert planted_ok!=negative
    assert not any(all(d(left,right)>=4 for left,right in combinations(subset,2)) for subset in combinations(range(19),5))
    assert len(set(mapping))==len(mapping);Path('role.receipt').write_text('\n'.join(mapping)+'\n')
    Path('strict.g6').write_text('\n'.join(gated)+'\n')
    run=subprocess.run(['python3','-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check','strict.g6','38','10'],capture_output=True,check=True)
    graphs=json.loads(run.stdout)['graphs'];assert len(graphs)==len(gated) and all(item['ok'] and item['n']==38 for item in graphs);Path('strict.gate').write_bytes(run.stdout)
    print('strict hole masks size 1..4',sorted(by_size.items()),'positive models gated',len(gated),'one fixed R8 signing',sorted(same_signing.items()))
    print('positive hole masks: (size, unfilled distinct old-neighborhood/pole incidences), multiplicity',sorted(deficiencies.items()))


def contact_prices():
    records=['holes joined d1 d2 ordered_for_degree_order involution_preserving']
    for holes in (3,4):
        for joined in (0,1):
            for first_degree,second_degree in combinations_with_replacement(range(4,10),2):
                first,second=first_degree-joined,second_degree-joined
                if first+second>2*holes:continue
                ordered=comb(2*holes,first)*comb(2*holes-first,second)
                symmetric=(comb(holes,first)*2**first) if first==second else 0
                old={(left,right) for left in range(1<<(2*holes)) for right in range(1<<(2*holes)) if
                     not left&right and left.bit_count()==first and right.bit_count()==second}
                assert ordered==len(old) and symmetric==sum((((left&85)<<1)|((left&170)>>1))==right for left,right in old)
                records.append(' '.join(map(str,(holes,joined,first_degree,second_degree,ordered,symmetric))))
    Path('contact.prices').write_text('\n'.join(records)+'\n')


def negative_controls():
    for tag,correct in [('yes',True),('no',False)]:
        record,=json.loads(Path(f'control.{tag}.gate').read_text())['graphs'];assert record['ok']==correct
    try:check(lines('role2.q')[3],10,Path('proof_role2/000'))
    except AssertionError:pass
    else:raise AssertionError('invalid diagonal transfer accepted')
    try:physical(lines('role2.q')[0],parse_graph6(lines('proof_role2/003.g6')[0]),10)
    except AssertionError:pass
    else:raise AssertionError('wrong positive mask accepted')
    print('both physical gate verdicts and invalid positive/negative mask substitutions checked')


def supports():
    for other,single in [(1,[2,3,4,5,15,18]),(2,[1,3,4,5,16,18]),(3,[1,2,4,5,17,18])]:
        assert all(d(center,site)<=5 for center in (0,other) for site in single)
        edges=[pair for pair in combinations(single,2) if d(*pair)>=6];forest=set(single)
        while forest:
            leaf=next(vertex for vertex in forest if sum(vertex in edge and set(edge)<=forest for edge in edges)<=1);forest.remove(leaf)
        print('hole pair',other,'forest edges',edges)
    old=lines('../r6/sparse.distinct.g6');degree_floor=[min(mask.bit_count() for mask in parse_graph6(text)) for text in old];assert degree_floor==[7]*33
    print('all 33 R6 inputs incompatible: degree minimum seven vs eight')
    for name,edges in [('round4_seed40_24.g6',178),('round4_seed40_24_e179.g6',179)]:
        graph=parse_graph6(lines(Path(__file__).resolve().parent/name)[0]);assert sum(row.bit_count() for row in graph)==2*edges and sum(1 for _ in independent_sets(graph,(1<<40)-1,10))==24
    print('both outside controls score 24, e178 and e179')


def saturation_small():
    count=Counter();adverse=Counter()
    for size in (3,4):
        order=2*size
        possible=set(combinations(range(order),2));orbits=[]
        while possible:
            edge=min(possible);orbit={edge,tuple(sorted(vertex^1 for vertex in edge))};possible-=orbit;orbits.append(orbit)
        for flags in range(1<<len(orbits)):
            graph=[0]*order
            for index,orbit in enumerate(orbits):
                if flags>>index&1:
                    for left,right in orbit:graph[left]|=1<<right;graph[right]|=1<<left
            if any(graph[left]&graph[right] for left,right in combinations(range(order),2) if graph[left]>>right&1):continue
            table=[[((graph[2*left]>>(2*right))&3).bit_count() for right in range(size)] for left in range(size)]
            automorphisms=[perm for perm in permutations(range(size)) if all(table[left][right]==table[perm[left]][perm[right]] for left,right in combinations(range(size),2))]
            limit=max(mask.bit_count() for mask in graph)
            filled=graph[:]
            for site in range(size):
                pair=(2*site,2*site+1); crossing=table[site][:];crossing[site]=0
                if sum(crossing)<limit and 2 not in crossing:
                    left,right=pair;filled[left]|=1<<right;filled[right]|=1<<left
                elif not table[site][site]:
                    reason='double' if 2 in crossing else 'degree';adverse[reason]+=1
                    assert (graph[pair[0]]&graph[pair[1]]) if reason=='double' else graph[pair[0]].bit_count()==limit
            assert all((graph[vertex]&~mask)==0 and mask.bit_count()<=limit for vertex,mask in enumerate(filled))
            assert not any(filled[left]&filled[right] for left,right in combinations(range(order),2) if filled[left]>>right&1)
            diagonal=[filled[2*site]>>(2*site+1)&1 for site in range(size)]
            assert all(all(diagonal[site]==diagonal[perm[site]] for site in range(size)) for perm in automorphisms)
            count[size,'TF']+=1
            if filled!=graph:count[size,'filled']+=1
            if any(any(table[site][site]!=table[perm[site]][perm[site]] for site in range(size)) for perm in automorphisms):count[size,'restored']+=1
    assert all(count[size,'restored'] for size in (3,4)) and all(adverse.values());print('full quotient saturation controls',sorted(count.items()),'unsafe additions detected',sorted(adverse.items()))


if __name__=='__main__':
    assert __debug__
    receipt=[];saturation_small();supports();source(receipt);roles(receipt);contact_prices();negative_controls()
    Path('proof.receipt').write_text('\n'.join(receipt)+'\n');print('independent semantic + dual LRAT count',len(receipt))
