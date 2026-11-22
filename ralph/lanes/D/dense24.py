from collections import Counter
from itertools import product
import json
import sys
from high24 import HIGH,OUT,graph_masks,squares,weakhex,pick,population,columns,independent
from wing24 import sites

def choose_collar(wing,marks):
    candidates=[]
    for square in marks:
        first,second,*opposite=square
        if sum(wing[site].bit_count() for site in square)<11:return 'squarebound',None
        for lhs,rhs in product((first,second),opposite):
            leftflap=[site for site in sites(wing[lhs]) if site not in square];rightflap=[site for site in sites(wing[rhs]) if site not in square]
            if not leftflap or not rightflap:continue
            outerleft,=leftflap;outerright,=rightflap;degrees=sorted((wing[outerleft].bit_count(),wing[outerright].bit_count()));hasthree=any(wing[site].bit_count()==2 for site in square)
            if wing[outerleft]>>outerright&1 or (hasthree and min(degrees)<3):return 'forbidden_collar',None
            size=3 if hasthree else {(2,2):4,(2,3):13,(3,3):42}[tuple(degrees)];points=tuple(sorted((*square,outerleft,outerright)));score=sum((wing[a]&wing[b]).bit_count() for i,a in enumerate(points) for b in points[:i]);candidates.append((size,-score,points))
    return 'square',min(candidates)[2]

def roster(edges):
    count=Counter();summaries=[];keys=[];shapes=[];cache={}
    for number,line in enumerate((HIGH/f'raw{edges}.g6').read_text().splitlines(),1):
        wing=graph_masks(line);marks=squares(wing);reason=None
        if any((lhs&rhs).bit_count()>2 for i,lhs in enumerate(wing) for rhs in wing[:i]):reason='paircap'
        elif marks:
            reason,points=choose_collar(wing,marks)
            if reason=='square':reason=None
        else:points=pick(wing)
        if not reason and weakhex(wing):reason='hex01'
        if reason:count[reason]+=1;shapes.append((number,reason,0));continue
        cachekey=(tuple(wing[v].bit_count() for v in points),tuple(-1 if wing[v]>>w&1 else (wing[v]&wing[w]).bit_count()+int((v<8)==(w<8)) for idx,v in enumerate(points) for w in points[:idx]));
        if cachekey in cache:decks=cache[cachekey]
        else:
            decks=population(wing,points,9,21,1)
            if len(points)==4:assert decks==columns(wing,points,9,21,1)
            else:
                core=wing[:]+[0,0,0]
                for site in range(16):tip=16+(site>=8);core[site]|=1<<tip;core[tip]|=1<<site
                for tip in (16,17):core[tip]|=1<<18;core[18]|=1<<tip
                assert set(decks)==independent(core,points,(1<<19)-1,21,1)
            cache[cachekey]=decks
        sector='square' if marks else 'squarefree';count[sector]+=1;shapes.append((number,sector,len(decks)));summaries.append(dict(number=number,g6=line,points=points,decks=decks));keys.extend(f'h{edges}_{number}_{idx}' for idx in range(len(decks)))
    (HIGH/f'spec{edges}.json').write_text(json.dumps(summaries,separators=(',',':')));(HIGH/f'keys{edges}').write_text(''.join(key+'\n' for key in keys));(HIGH/f'shapes{edges}.tsv').write_text(''.join(f'{number}\t{sector}\t{length}\n' for number,sector,length in shapes));print('edge',edges,'raw',len(shapes),'disjoint sectors',count,'different physical alphabets',len(cache),'keys',len(keys),flush=True)

if __name__=='__main__':roster(int(sys.argv[1]))
