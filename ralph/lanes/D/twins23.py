from itertools import combinations
from pathlib import Path
from collections import Counter
import json
import os
import sys

from closure22 import Cadical195,DECK,ROOT,bits,task
from m14queue22 import BASE,data,hall_cards
from rebind import physical
from shadow import decode
from pysat.card import CardEnc
from pysat.formula import IDPool

NEW=BASE.parent/'m14r23'; HARD=NEW/'hard'


def join(rows,sides,inside,degree,cards):
    base=len(rows)+len(sides[0][2]); count=len(sides[0][2]); wings=[]; formulas=[]; edges=[]
    for index,parameters in enumerate(sides):
        head,ranks,hits,wd,yw,yd,total=parameters
        formula,_,edge=physical(rows,head,ranks,hits,wd,yw,yd,total,inside,degree,cards[index]);formulas.append(formula);edges.append(edge);wings.append(list(range(base,base+len(ranks))))
    first,second=formulas; limit=first.nv
    lookup={edges[1](u,v):edges[0](u,v) for u,v in combinations(range(base),2)}
    def second_var(var):return lookup.get(var,limit+var)
    first.extend([[second_var(abs(lit))*(1 if lit>0 else -1) for lit in clause] for clause in second.clauses]);
    edge_a=edges[0];edge_b=lambda u,v:second_var(edges[1](u,v));pool=IDPool(start_from=limit+second.nv+1)
    for site,mask in enumerate(rows,count):
        neighborhood=[edge_a(site,other) for other in range(count,base) if other!=site]+[edge_a(site,other) for other in wings[0]]+[edge_b(site,other) for other in wings[1]]
        first.extend(CardEnc.equals(neighborhood,bound=degree-mask.bit_count(),vpool=pool).clauses)
    return first,[edge_a,edge_b]


def sides(key,head):
    _,first,ranks=data(key);second=first if key[0]=='D' else [2]*7 if key[0]=='S' else [2,1]+[2]*5
    def params(pin,margin):return (pin,[2]*(sum(margin)-8)+[1]*(16-sum(margin)),margin,(5,6),(2,3),(6,7),64-17-sum(margin))
    return [params(head,first),params([],second)]


def controls():
    total=0
    for row in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        full=decode(row)
        if min(word.bit_count() for word in full)!=6 or max(word.bit_count() for word in full)!=6 or max((x&y).bit_count() for x,y in combinations(full,2))>3:continue
        for tip in range(22):
            for opp in range(22):
                common=full[tip]&full[opp]
                if common.bit_count()!=1 or full[tip]>>opp&1:continue
                middle=common.bit_length()-1;poles=list(bits(full[middle]&~(1<<tip|1<<opp)));inside=sorted(set(range(22))-{tip,opp,middle}-set(bits(full[tip]|full[opp]|full[middle])))
                mask=lambda site:sum(1<<i for i,p in enumerate(poles) if full[site]>>p&1);bounds=lambda seq:(min(seq),max(seq));deg=lambda left,right:[sum(full[u]>>v&1 for v in right) for u in left]
                core=poles+inside;supp=list(map(mask,inside));sidespec=[];labels=[];decks=[]
                for idx,center in enumerate([tip,opp]):
                    wing=sorted(bits(full[center]&~common),key=lambda v:(mask(v).bit_count(),mask(v)),reverse=True);label=core+wing;labels.append(label);rs=[mask(v).bit_count() for v in wing];yw=deg(inside,wing);wy=deg(wing,inside);yy=deg(inside,inside)
                    sidespec.append(([mask(wing[0])] if idx==0 else [],rs,deg(poles,wing),bounds([x+y for x,y in zip(rs,wy)]),bounds(yw),bounds([m.bit_count()+x+y for m,x,y in zip(supp,yw,yy)]),sum(wy)));decks.append([sum(1<<v for v in group) for ground,width in [(len(label),6),(len(core),5)] for group in combinations(range(ground),width)])
                model,edges=join(supp,sidespec,sum(yy)//2,6,decks);pins=[]
                for label,edge in zip(labels,edges):
                    pins.extend(edge(i,j)*(1 if full[label[i]]>>label[j]&1 else -1) for i,j in combinations(range(len(label)),2))
                assert all(edges[0](i,j)==edges[1](i,j) for i,j in combinations(range(len(core)),2));mut=edges[1](len(poles),len(core));
                with Cadical195(bootstrap_with=model.clauses) as solver:
                    assert solver.solve(assumptions=pins);assert not solver.solve(assumptions=[-lit if abs(lit)==mut else lit for lit in pins])
                total+=1
    assert total==250;print('250 joint physical C22 boards pass, 250 adverse opposite-wing Y-edge toggles reject',flush=True)


def cardsplit(raw):
    masks=list(raw);return [[abs(mask) for mask in masks if (mask<0)==bool(side)] for side in range(2)]


def build(key,head,mode,raw):
    rows,_,_=data(key);params=sides(key,head);cards=cardsplit(raw)
    if mode=='twins':return join(rows,params,14,9,cards)
    side=int(mode=='reverse');args=params[side];formula,_,edge=physical(rows,*args,14,9,cards[side]);return formula,[edge]


def unpack(token):
    key,suffix=token.split('-');return key,[] if suffix in ('reverse','joint') else [int(suffix)]


def style(token):
    key,head=unpack(token)
    if token.endswith('-reverse'):return 'reverse'
    if token.endswith('-joint'):return 'twins'
    root=next(place/key for place in (NEW,BASE) if (place/key/'progress.json').is_file() and json.loads((place/key/'progress.json').read_text())['status'] not in ('staging_guard','open'))
    return 'single' if (root/'cards').is_file() else 'twins'


def findcards(edge,model):
    adj=[0]*29
    for u,v in combinations(range(29),2):
        if edge(u,v) in model:adj[u]|=1<<v;adj[v]|=1<<u
    def visit(word,avail,need):
        if not need:yield word;return
        while avail.bit_count()>=need:
            low=avail&-avail;avail^=low;yield from visit(word|low,avail&~adj[low.bit_length()-1],need-1)
    for length,size in [(21,8),(29,9)]:yield from visit(0,(1<<length)-1,size)


def discover(token):
    key,head=unpack(token);mode=style(token);parent=next((b/key/'cards' for b in (BASE,NEW) if (b/key/'cards').is_file()),None)
    if mode=='single' and parent:
        Path('cards').write_bytes(parent.read_bytes()); print('inherited unpinned physical cards');return 0
    rows,_,_=data(key);seed=set(hall_cards(rows,7))|set(map(int,DECK.read_text().splitlines()));raw=seed if mode=='single' else {-m for m in seed} if mode=='reverse' else seed|{-m for m in seed}
    cnf,edges=build(key,head,mode,sorted(raw));rounds=0
    with Cadical195(bootstrap_with=cnf.clauses) as solver:
        while True:
            solver.conf_budget(max(1,600000-solver.accum_stats()['conflicts']));answer=solver.solve_limited()
            if answer is not True:break
            model=set(solver.get_model());extra=0
            for side,edge in enumerate(edges):
                for mask in findcards(edge,model):
                    signed=-mask if side==1 or mode=='reverse' else mask
                    if signed in raw:raise AssertionError((mode,signed))
                    raw.add(signed);solver.add_clause([edge(u,v) for u,v in combinations(bits(mask),2)]);extra+=1
                    if extra>=2000:break
                if extra>=2000:break
            if not extra:break
            rounds+=1
            if solver.accum_stats()['conflicts']>=600000:answer=None;break
        Path('cards').write_text(''.join(f'{mask}\n' for mask in sorted(raw)));print(mode,answer,'rounds',rounds,'cards',len(raw),'conflicts',solver.accum_stats()['conflicts'],flush=True)
        return 0 if answer is False else 10 if answer is True else 3


def run(token,place=HARD):task(token,[],120,90000000,place,str(Path(__file__).resolve()),485000000,BASE/'lrat-trim')


if __name__=='__main__':
    if sys.argv[1]=='cal':controls()
    elif sys.argv[1]=='bind':
        token=sys.argv[2];key,head=unpack(token);cnf,edges=build(key,head,style(token),map(int,Path('cards').read_text().splitlines()));cnf.to_file('input.cnf')
    elif sys.argv[1]=='discover':sys.exit(discover(sys.argv[2]))
    else:run(sys.argv[2])
