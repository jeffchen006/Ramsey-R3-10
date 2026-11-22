"""Four arbitrary poles on an unsigned paired card: source and contact prices."""

from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations, product
from pathlib import Path
import subprocess
import sys

from cyclic_base import matrix, profiles
from orbit_extend import ROOT, independent, independent_sets, to_graph6
from pole_audit import relabel
from relift_audit import encode


def put(name, records):
    Path(name).write_text(''.join(f'{record}\n' for record in records))


def max_alpha(graph, allowed):
    return max(mask.bit_count() for mask in range(1 << len(graph))
               if not mask & ~allowed and independent(mask, graph))


def obligations(graph, core, target):
    poles = relabel(graph, list(range(core,core+4)))
    for vertex in range(core):
        hood = graph[vertex] & ((1<<core)-1)
        unseen = sum(1<<index for index in range(4) if not graph[core+index]&hood)
        if hood.bit_count()+max_alpha(poles,unseen)>=target:
            return vertex,hood,unseen


def control():
    found = []
    for modulus,jumps,removed in [(13,(1,5),0),(12,(2,3),None),(12,(1,5),None),(9,(1,3),0),(8,(1,4),None)]:
        target = 5 if modulus>=12 else 4
        graph = [sum(1<<j for j in range(modulus) if min((j-i)%modulus,(i-j)%modulus) in jumps) for i in range(modulus)]
        sites = [i for i in range(modulus) if i!=removed]
        if not all(independent(hood,graph) for hood in graph) or next(independent_sets(graph,sum(1<<i for i in sites),target),None) is not None:continue
        for offset in range(modulus):
            mates = [(site,(offset-site)%modulus) for site in sites if site<(offset-site)%modulus and (offset-site)%modulus in sites]
            for paired in combinations(mates,(len(sites)-4)//2):
                for order in permutations(paired[1:]):
                    pairs = (paired[0],)+order
                    old=[i for pair in pairs for i in pair]; count=len(old); size=len(pairs)
                    witness = relabel(graph,old+sorted(set(sites)-set(old)))
                    weights = [[((witness[2*left]>>(2*right))&3).bit_count() for right in range(size)] for left in range(size)]
                    if any(weights[left][right]!=weights[0][(right-left)%size] for left,right in permutations(range(size),2)):continue
                    assert all((witness[i]>>j&1)==(witness[i^1]>>(j^1)&1) for i,j in combinations(range(count),2))
                    assert not obligations(witness,count,target)
                    for vertex,pole in product(range(count),range(count,count+4)):
                        if not (witness[vertex]>>pole)&1:continue
                        bad = witness[:];bad[vertex]^=1<<pole;bad[pole]^=1<<vertex
                        conflict=obligations(bad,count,target)
                        if conflict:
                            key=(count,weights[0][size//2]==1,len({weights[i][i] for i in range(size)}),sum(row.bit_count() for row in witness))
                            found.append((key,witness,bad,weights,vertex,pole,conflict,target))
                            break
    key,witness,bad,weights,vertex,pole,conflict,target=max(found)
    put('small.yes.g6',[to_graph6(witness)]);put('small.no.g6',[to_graph6(bad)]);put('small.q',[encode(weights)])
    print('old order,odd antipodal,multiple verticals,twice edges:',key,'crossing row:',weights[0],'deleted:',vertex,pole,'violation vertex,hood,unseen:',conflict,'n,k:',len(witness),target)
    for tag in ('yes','no'):
        import json
        result=subprocess.check_output([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',f'small.{tag}.g6',str(len(witness)),str(target)],text=True)
        Path(f'small.{tag}.gate').write_text(result)
        assert json.loads(result)['graphs'][0]['ok']==(tag=='yes')


def shapes():
    pairs=list(combinations(range(4),2));result={}
    for flags in range(64):
        graph=[0]*4
        for index,(left,right) in enumerate(pairs):
            if flags>>index&1:graph[left]|=1<<right;graph[right]|=1<<left
        if all(independent(hood,graph) for hood in graph):
            result[tuple(sorted(hood.bit_count() for hood in graph))]=graph
    return result


@lru_cache(None)
def roles(degree,verticals,shape):
    cap=9; old_edges=18*degree+verticals; edge_sum=sum(x.bit_count() for x in shape); internal=edge_sum//2
    alpha=[max_alpha(shape,mask) for mask in range(16)]
    oldcounts=[36-2*verticals,2*verticals]
    capacities=[min(max(0,cap-degree-bit),alpha[-1]) for bit in (0,1)]
    if verticals and degree==9:return None
    demand=[4-max(mask.bit_count() for mask in range(16) if alpha[mask]<=max(0,cap-degree-bit)) for bit in (0,1)]
    slot=sum(size*c for size,c in zip(oldcounts,capacities))
    low=max(161-old_edges-internal,sum(max(0,4-hood.bit_count()) for hood in shape))
    high=min(slot,36-edge_sum,180-old_edges-internal)
    if low>high:return None
    need=sum(size*req for size,req in zip(oldcounts,demand))
    usable_high= min(high,oldcounts[1]*capacities[1]); reach=high*degree+usable_high
    if need>reach:return None
    return (low,high,slot,need,reach,*capacities,*demand)


def source():
    families=[]; rows=[]; counts=Counter(); shapes4=shapes();assert len(shapes4)==7
    for profile,orbit in profiles(18,0,9):
        if profile[0]:continue
        degree=2*sum(profile[1:-1])+profile[-1]; double=max(profile)==2
        vrange=range(1 if double or degree==9 else 19)
        data=[(verticals,''.join(map(str,key)),price) for verticals in vrange for key,shape in shapes4.items() if (price:=roles(degree,verticals,tuple(shape))) is not None]
        if not data:continue
        assert degree in (6,7,8)
        index=len(families);families.append((profile,orbit));counts[degree,double]+=1
        rows += [' '.join(map(str,(index,degree,verticals,key,*price))) for verticals,key,price in data]
    put('parents.tsv',[f'{index} {"".join(map(str,profile[1:]))} {orbit}' for index,(profile,orbit) in enumerate(families)])
    put('max.q',[encode(matrix(18,(int(max(profile)<2),)+profile[1:])) for profile,orbit in families]);put('roles.tsv',rows)
    print('simple/double counts',sorted(counts.items()),'parents',len(families),'labelled words',sum(orbit for profile,orbit in families),'arithmetic roles',len(rows))


if __name__=='__main__':
    {'control':control,'source':source}[sys.argv[1]]()
