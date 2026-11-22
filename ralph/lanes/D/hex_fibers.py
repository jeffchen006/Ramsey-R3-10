"""The C6 component of a full wing: exact contact multiset and physical seven-star types."""
from collections import Counter
from itertools import combinations,product
from time import process_time
import json,sys
from equal_roles import DEST
from book_controls import bitset,sites,graph_masks,flags,book,reorder
from kernel_cnf import ROOT


def masks():
    return [1<<site for site in range(6)]+[(1<<site)|(1<<((site+2)%6)) for site in range(6)]+[(1<<site)|(1<<(site+3)) for site in range(3) for _ in range(3)]


def orbit_actions(words):
    actions=[];types=list(dict.fromkeys(words))
    for shift,step in product(range(6),(-1,1)):
        perm=[types.index(bitset((shift+step*site)%6 for site in sites(word))) for word in types];actions.append(perm)
    return actions


def induced_census():
    checks=0;tight=0
    for text in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=graph_masks(text)
        if {word.bit_count() for word in graph}!={6} or max((one&two).bit_count() for one,two in combinations(graph,2))>3:continue
        for ends in flags(graph):
            frame,(left,right)=book(graph,ends);core=list(frame)+list(left)+list(right);outer=sorted(set(range(22))-set(core));wing=left+right
            for side1,side2 in product(combinations(left,3),combinations(right,3)):
                cycle=side1+side2;inside=bitset(cycle)
                if any((inside&graph[site]).bit_count()!=2 for site in cycle):continue
                pairs=[(one,two) for one,two in combinations(cycle,2) if not (graph[one]>>two&1)];demand=sum((graph[site]&bitset(outer)).bit_count() for site in cycle);cap=sum(3-(graph[one]&graph[two]&bitset(core)).bit_count() for one,two in pairs);terms=[(inside&graph[site]).bit_count() for site in outer];assert demand-cap<=len(outer);checks+=1
                if demand-cap==len(outer):
                    assert min(terms)>=1 and max(terms)<=2 and all((graph[one]&graph[two]).bit_count()==3 for one,two in pairs);tight+=1
    print('PASS literal C22 induced-hex footprint and equality side conditions',checks,'tight',tight)


def roster():
    words=masks();types=list(dict.fromkeys(words));actions=orbit_actions(words);seen=set();counts=Counter();out=[]
    for seven in combinations(range(len(words)),7):
        counts['physical']+=1;profile=tuple(sum(words[site]==word for site in seven) for word in types)
        if profile in seen:continue
        orbit={tuple(profile[idx] for idx in perm) for perm in actions};seen.update(orbit);profile=min(orbit);counts['raw_orbits']+=1
        seven=tuple(idx for pos,word in enumerate(types) for idx in [j for j,other in enumerate(words) if other==word][:profile[pos]]);degrees=[sum(words[idx]>>site&1 for idx in seven) for site in range(6)]
        if min(degrees)<1 or max(degrees)>2:continue
        counts['survive']+=1;out.append(dict(profile=profile,seven=seven,hexdeg=degrees))
    return out,counts


if __name__=='__main__':
    if sys.argv[1]=='cal':induced_census()
    else:
        start=process_time();out,counts=roster();print(dict(counts),process_time()-start,file=sys.stderr)
        for row in out:print(json.dumps(row))
