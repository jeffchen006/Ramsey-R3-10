from collections import Counter
from functools import lru_cache
from itertools import combinations
from math import comb,factorial
import json
import sys
import pynauty
from wing24 import OUT,graph_masks,sites,expand,population,columns,pick
from square23 import squares,weakhex,patch_data
from squareaudit23 import independent

HIGH=OUT/'high'

@lru_cache(None)
def matrices(rows,cols):
    if not rows:return int(not any(cols))
    result=0
    for choice in combinations([pos for pos,val in enumerate(cols) if val],rows[0]):
        after=list(cols)
        for pos in choice:after[pos]-=1
        result+=matrices(rows[1:],tuple(sorted(after)))
    return result

def object16(wing):return pynauty.Graph(16,False,{site:list(sites(mask)) for site,mask in enumerate(wing)},[set(range(8)),set(range(8,16))])

def audit():
    for edges in range(18,25):
        high=edges-16;degrees=tuple([2]*(8-high)+[3]*high);expected=comb(8,high)**2*matrices(degrees,degrees);seen=set();mass=0;passkeys=set();free=0
        for line in (HIGH/f'all{edges}.g6').read_text().splitlines():
            wing=graph_masks(line);assert tuple(sorted(row.bit_count() for row in wing[:8]))==tuple(sorted(row.bit_count() for row in wing[8:]))==degrees;graph=object16(wing);key=pynauty.certificate(graph);assert key not in seen;seen.add(key);_,man,exp,*_=pynauty.autgrp(graph);order=int(man)*10**exp;weight,rem=divmod(factorial(8)**2,order);assert not rem;mass+=weight
            if all((lhs&rhs).bit_count()<=2 for lhs,rhs in combinations(wing,2)):passkeys.add(key);free+=not squares(wing)
        from square23 import WORK
        source=WORK/'raw.g6' if edges==18 else HIGH/f'raw{edges}.g6';capkeys=set()
        for line in source.read_text().splitlines():
            wing=graph_masks(line)
            if all((lhs&rhs).bit_count()<=2 for lhs,rhs in combinations(wing,2)):capkeys.add(pynauty.certificate(object16(wing)))
        assert mass==expected and passkeys==capkeys;print(edges,len(seen),mass,len(passkeys),free,flush=True)

def choices(wing,marks):
    best=None
    for square in marks:
        for left in set(range(8))-set(square):
            for right in set(range(8,16))-set(square):
                points=tuple(sorted((*square,left,right)));rows,demand,bounds=patch_data(wing,[0]*8+[1]*8,points,9);option=(sum(upper for lower,upper in bounds.values())-sum(demand),-sum(mask.bit_count() for mask in rows),points)
                if best is None or option<best:best=option
    return best[-1]

def roster(edges):
    allrows=[];keys=[];counts=Counter();studied=HIGH/f'spec{edges}.json';hist=Counter()
    for number,line in enumerate((HIGH/f'raw{edges}.g6').read_text().splitlines(),1):
        wing=graph_masks(line);counts['raw']+=1
        if any((lhs&rhs).bit_count()>2 for lhs,rhs in combinations(wing,2)):counts['paircap']+=1;continue
        marks=squares(wing)
        if any(sum(wing[v].bit_count() for v in square)<11 for square in marks):counts['squarebound']+=1;continue
        if weakhex(wing):counts['hex01']+=1;continue
        points=choices(wing,marks) if marks else pick(wing);decks=population(wing,points,9,21,1)
        if len(points)==6:
            graph=wing[:]+[0,0,0]
            for site in range(16):tip=16+(site>=8);graph[site]|=1<<tip;graph[tip]|=1<<site
            for tip in (16,17):graph[tip]|=1<<18;graph[18]|=1<<tip
            assert set(decks)==independent(graph,points,(1<<19)-1,21,1)
        else:assert decks==columns(wing,points,9,21,1)
        keys.extend(f'h{edges}_{number}_{idx}' for idx in range(len(decks)));counts['squares' if marks else 'squarefree']+=1;hist[len(decks)]+=1;allrows.append(dict(number=number,g6=line,points=points,decks=decks))
    studied.write_text(json.dumps(allrows));(HIGH/f'keys{edges}').write_text(''.join(key+'\n' for key in keys));print(edges,counts,hist,'complete dual census',len(keys),flush=True)

def formula_high(key):
    edges,number,idx=map(int,key[1:].split('_'));row=next(row for row in json.loads((HIGH/f'spec{edges}.json').read_text()) if row['number']==number);return expand(graph_masks(row['g6']),row['points'],row['decks'][idx],27+edges,9,True)

if __name__=='__main__':
    if sys.argv[1]=='audit':audit()
    else:roster(int(sys.argv[1]))
