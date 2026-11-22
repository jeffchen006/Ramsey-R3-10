from itertools import combinations
from pathlib import Path
import json
import sys

from patch23 import ROOT,STORE,OLD,patch_data,build,task,census,bitset,sites,Cadical195
from book_controls import graph_masks,book,flags,reorder

WORK=STORE/'flap'; SIDE=[0,1]*3+[1,0,0]; WING=[(1<<((index+1)%6))|(1<<((index-1)%6)) for index in range(6)]+[1|1<<7|1<<8,1<<6,1<<6];WING[0]|=1<<6


def masks():
    out=[];data=patch_data(WING,SIDE,list(range(6)),9)
    census(*data,21,1,lambda profile,leak:out.append(sorted(mask for mask,n in profile.items() for _ in range(n))))
    assert len(out)==12;return out


def edges(form,side,left,right):
    if right<form.n:return form.edge(left,right)
    if right==form.n+1 and left==form.n:return False
    if left==form.n-1:return True
    return left<len(side) and side[left]==right-form.n


def addcard(form,side,mask,width):
    assert mask.bit_count()==width and mask<1<<(form.n+2)
    form.add(*(edges(form,side,l,r) for l,r in combinations(sites(mask),2)))


def separate(form,side,positive,width,limit=256):
    order=form.n+2;adj=[0]*order
    for left,right in combinations(range(order),2):
        entry=edges(form,side,left,right)
        if entry is True or type(entry) is int and entry in positive:adj[left]|=1<<right;adj[right]|=1<<left
    def rec(chosen,rest,need):
        if not need:yield chosen;return
        while rest.bit_count()>=need:
            low=rest&-rest;rest^=low;yield from rec(chosen|low,rest&~adj[low.bit_length()-1],need-1)
    import itertools
    return list(itertools.islice(rec(0,(1<<order)-1,width),limit))


def formula(number):return build(WING,SIDE,list(range(7)),list(range(6)),masks()[number],None,9,True,(),{6:(5,6)})


def control():
    total=0
    for text in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=graph_masks(text)
        if {word.bit_count() for word in graph}!={6} or max((a&b).bit_count() for a,b in combinations(graph,2))>3:continue
        for ends in flags(graph):
            (middle,a,b),(left,right)=book(graph,ends);wing=left+right;outside=sorted(set(range(22))-set(wing)-{middle,a,b});pin=[0,1,2,5,6,7];selected=pin+[8];words=[bitset(i for i,v in enumerate(pin) if graph[site]>>wing[v]&1) for site in outside];sides0=[0]*5+[1]*5;active=[sides0[v] for v in selected];labels=[wing[v] for v in selected]+outside+[middle];true=reorder(graph,labels+[a,b]);form=build(reorder(graph,wing),sides0,selected,pin,words,None,6,False,(),{8:(0,len(outside))});pins=[form.edge(i,j,False)*(1 if true[i]>>j&1 else -1) for i,j in combinations(range(form.n),2)]
            with Cadical195(bootstrap_with=form.clauses) as solver:assert solver.solve(assumptions=pins);positive=set(solver.get_model());assert not separate(form,active,positive,7)
            for i,j in combinations(range(form.n+2),2):
                entry=edges(form,active,i,j);assert (entry is True or type(entry) is int and entry in positive)==bool(true[i]>>j&1)
            total+=1
    assert total==125;print('125 C22 variable-residual no-edge-total partial projections + all tip edges/independent-set witnesses verified')


def discover(number):
    form=formula(number);found=[]
    with Cadical195(bootstrap_with=form.clauses) as solver:
        while True:
            solver.conf_budget(max(1,240000-solver.accum_stats()['conflicts']));answer=solver.solve_limited()
            if answer is not True:break
            cuts=separate(form,SIDE[:7],set(solver.get_model()),10)
            if not cuts:break
            for mask in cuts:addcard(form,SIDE[:7],mask,10);solver.add_clause(form.clauses[-1]);found.append(mask)
            if solver.accum_stats()['conflicts']>=240000:answer=None;break
    Path('cards').write_text(''.join(f'{mask}\n' for mask in sorted(set(found))));print(answer,len(found),flush=True);return 0 if answer is False else 10 if answer else 3


if __name__=='__main__':
    if sys.argv[1]=='cal':control()
    elif sys.argv[1]=='bind':
        form=formula(int(sys.argv[2]));
        for mask in map(int,Path('cards').read_text().splitlines()):addcard(form,SIDE[:7],mask,10)
        form.write(Path('input.cnf'))
    elif sys.argv[1]=='discover':sys.exit(discover(int(sys.argv[2])))
    else:
        for token in sys.argv[2:]:task(token,[],80,60000000,WORK,str(Path(__file__).resolve()),345000000,OLD/'lrat-trim')
