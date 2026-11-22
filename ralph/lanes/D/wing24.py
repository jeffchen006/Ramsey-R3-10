import hashlib
import json
import sys
from collections import Counter
from itertools import combinations,product
from pathlib import Path

from patch23 import ROOT,build,patch_data,census,Cadical195,book,flags,graph_masks,reorder,bitset,sites
from square23 import WORK,squares,weakhex
from kernel_cnf import neg

OUT=ROOT/'scratch/D/wing24'

def population(rows,points,degree,outer,leaks):
    side=[int(site>=len(rows)//2) for site in range(len(rows))];data=patch_data(rows,side,points,degree);decks=[]
    census(*data,outer,leaks,lambda profile,spent:decks.append(tuple(sorted(mask for mask,count in profile.items() for _ in range(count)))))
    return sorted(decks)

def columns(rows,points,degree,outer,leaks):
    side=len(rows)//2;decks={(0,)*outer:0}
    for index,site in enumerate(points):
        next_decks={};demand=degree-1-rows[site].bit_count()
        for deck,debit in decks.items():
            groups=sorted(Counter(deck).items());ranges=[range(min(demand,count)+1) for _,count in groups]
            for quantities in product(*ranges):
                if sum(quantities)!=demand:continue
                used=debit
                for pos,other in enumerate(points[:index]):
                    common=sum(quantity for (mask,count),quantity in zip(groups,quantities) if mask>>pos&1)
                    if rows[site]>>other&1:
                        if common:break
                    else:
                        total=common+(rows[other]&rows[site]).bit_count()+int((site<side)==(other<side))
                        if total>3:break
                        used+=max(0,2-total)
                else:
                    if used<=leaks:next_decks[tuple(sorted(word for (mask,count),qty in zip(groups,quantities) for word in [mask]*(count-qty)+[mask|(1<<index)]*qty))]=used
        decks=next_decks
    return sorted(decks)

def pick(rows):
    size=len(rows);side=[int(v>=size//2) for v in range(size)];options=[]
    for points in combinations(range(size),4):
        patch,demand,bounds=patch_data(rows,side,points,size//2+1);edges=sum(word.bit_count() for word in patch)//2
        if edges<3:continue
        options.append((sum(high for low,high in bounds.values())-sum(demand),-edges,points))
    return min(options)[-1]

def roster():
    done={json.loads(line)['number'] for line in (WORK/'hex/spec.jsonl').read_text().splitlines()};records=[];keys=[]
    for number,text in enumerate((WORK/'raw.g6').read_text().splitlines(),1):
        rows=graph_masks(text)
        if number in done or any((a&b).bit_count()>2 for a,b in combinations(rows,2)) or squares(rows) or weakhex(rows):continue
        points=pick(rows);decks=population(rows,points,9,21,1);records.append(dict(number=number,g6=text,points=points,decks=decks));keys.extend(f'{number}_{idx}' for idx in range(len(decks)))
    assert len(records)==57; (OUT/'spec.json').write_text(json.dumps(records));keys.sort(key=lambda key:hashlib.sha256(key.encode()).digest());(OUT/'manifest').write_text('\n'.join(keys)+'\n');print('shapes',len(records),'roots',len(keys),'hist',Counter(len(row['decks']) for row in records))

def expand(rows,points,words,qedges,degree,target):
    span=len(rows);outer=len(words);side=span//2;hub=span+outer;blocks=range(span,hub);form=build(rows,[int(site>=side) for site in range(span)],list(range(span)),points,words,qedges,degree,target)
    for index in range(outer-1):
        if words[index]!=words[index+1]:continue
        prior=True
        for site in [hub,*[v for v in range(span) if v not in points]]:
            first=form.edge(site,span+index);second=form.edge(site,span+index+1);form.add(neg(prior),neg(first),second)
            equal=form.new();form.add(neg(prior),neg(first),neg(second),equal);form.add(neg(prior),first,second,equal);prior=equal
    core=[*rows,0,0,0];middle=span+2
    for site in range(span):
        tip=span+int(site>=side);core[site]|=1<<tip;core[tip]|=1<<site
    for tip in (span,span+1):core[tip]|=1<<middle;core[middle]|=1<<tip
    def indep(mask,rest):
        if mask.bit_count()+rest.bit_count()<degree-1:return
        if not rest:
            if mask.bit_count()>=degree-1:yield mask
            return
        bit=rest&-rest;yield from indep(mask,rest^bit);yield from indep(mask|bit,(rest^bit)&~core[bit.bit_length()-1])
    for mask in indep(0,(1<<len(core))-1):
        physical=[hub if v==middle else v for v in sites(mask) if v not in (span,span+1)];avoids=[]
        for point in blocks:
            terms=[form.edge(v,point) for v in physical];terms=[v for v in terms if v is not False]
            if any(v is True for v in terms):flag=False
            elif not terms:flag=True
            else:
                flag=form.new();form.add(flag,*terms)
            avoids.append(flag)
        if mask.bit_count()>=degree:
            for flag in avoids:form.add(neg(flag))
        else:
            for first,second in combinations(range(outer),2):form.add(neg(avoids[first]),neg(avoids[second]),form.edge(span+first,span+second))
    return form

def calibration(length=4):
    count=0
    for line in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=graph_masks(line)
        if {row.bit_count() for row in graph}!={6} or max((a&b).bit_count() for a,b in combinations(graph,2))>3:continue
        for ends in flags(graph):
            (hub,*tips),(left,right)=book(graph,ends);wing=left+right;rows=reorder(graph,wing);points=tuple([0,1,5,6,3,8][:length]);outside=set(range(22))-set(wing)-{hub,*tips}
            def key(point):return (bitset(idx for idx,site in enumerate(points) if graph[point]>>wing[site]&1),tuple(graph[v]>>point&1 for v in [hub,*[wing[v] for v in range(10) if v not in points]]))
            outside=sorted(outside,key=key);words=tuple(key(v)[0] for v in outside);leaks=sum((graph[wing[v]]&graph[wing[w]]).bit_count()==1 for v,w in combinations(points,2) if not rows[v]>>w&1)
            if length==6:assert census(*patch_data(rows,[int(site>=5) for site in range(10)],points,6),len(words),leaks,None,Counter(words))[0]==1
            else:
                decks=population(rows,points,6,len(words),leaks);assert words in decks and decks==columns(rows,points,6,len(words),leaks)
            if length==5:
                from split24 import children
                base=tuple(sorted(word&15 for word in words));assert words in children(rows,points[:4],base,points[4],6,leaks)
            form=expand(rows,points,words,sum(v.bit_count() for v in reorder(graph,outside))//2,6,False);true=reorder(graph,[*wing,*outside,hub]);pins=[form.edge(i,j,False)*(1 if true[i]>>j&1 else -1) for i,j in combinations(range(len(true)),2)];mut=form.edge(0,10,False)
            with Cadical195(bootstrap_with=form.clauses) as solver:assert solver.solve(assumptions=pins) and not solver.solve(assumptions=[-v if abs(v)==mut else v for v in pins]);count+=1
    assert count==125;print(count,'sorted C22 plants pass, 125 mutations reject;', 'six-site literal population membership' if length==6 else 'both censuses agree')

def formula(key):
    number,idx=map(int,key.split('_'));row=next(row for row in json.loads((OUT/'spec.json').read_text()) if row['number']==number);return expand(graph_masks(row['g6']),row['points'],row['decks'][idx],45,9,True)

if __name__=='__main__':
    if sys.argv[1]=='cal':calibration(int(sys.argv[2]) if len(sys.argv)>2 else 4)
    elif sys.argv[1]=='roster':roster()
    elif sys.argv[1]=='audit':
        records=json.loads((OUT/'spec.json').read_text());counts=Counter()
        for row in records:
            actual=columns(graph_masks(row['g6']),row['points'],9,21,1);assert actual==list(map(tuple,row['decks']));counts[len(actual)]+=1
        print('independent column census all',len(records),'shapes; count histogram',counts)
    elif sys.argv[1]=='bind':formula(sys.argv[2]).write(Path('input.cnf'))
