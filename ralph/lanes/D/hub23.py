from collections import Counter
from itertools import combinations,product
from pathlib import Path
import json
import sys

from closure22 import ROOT,task
from flap23 import WORK,STORE,SIDE,OLD,addcard,formula,masks,separate,Cadical195
from book_controls import graph_masks,flags,book,bitset,sites,reorder
from patchbind23 import build

OUT=STORE/'hub'


def groups(words):
    types=sorted(set(words),key=lambda mask:(-words.count(mask),mask));return [[i for i,word in enumerate(words) if word==mask] for mask in types[:2]]


def histogram(words,picked,vertices,bounds):
    cells=groups(words);hist=Counter()
    for chosen in combinations(range(len(words)),picked):
        if any(not bounds[0]<=sum(words[i]>>v&1 for i in chosen)<=bounds[1] for v in range(vertices)):continue
        hist[tuple(sum(i in chosen for i in cell) for cell in cells)]+=1
    return hist


def units(form,start,cells,counts):
    return [form.edge(start+i,form.n-1,False)*(1 if j<count else -1) for cell,count in zip(cells,counts) for j,i in enumerate(cell)]


def cal():
    total=0
    for line in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=graph_masks(line)
        if {x.bit_count() for x in graph}!={6} or max((a&b).bit_count() for a,b in combinations(graph,2))>3:continue
        for ends in flags(graph):
            (middle,a,b),(left,right)=book(graph,ends);wing=left+right;points=[0,1,2,5,6,7];chosen=points+[8];outer=sorted(set(range(22))-set(wing)-{middle,a,b});mask=lambda q:bitset(i for i,site in enumerate(points) if graph[q]>>wing[site]&1);words=list(map(mask,outer));cells=groups(words)
            for cell in cells:
                ordered=sorted([outer[i] for i in cell],key=lambda q:graph[q]>>middle&1,reverse=True)
                for idx,vertex in zip(cell,ordered):outer[idx]=vertex
            assert list(map(mask,outer))==words;counts=tuple(sum(graph[middle]>>outer[i]&1 for i in cell) for cell in cells);hit=[sum((graph[middle]>>outer[i]&1)*(words[i]>>p&1) for i in range(len(outer))) for p in range(6)];assert histogram(words,4,6,(min(hit),max(hit)))[counts]>0
            form=build(reorder(graph,wing),[0]*5+[1]*5,chosen,points,words,None,6,False);pins=units(form,len(chosen),cells,counts);truth=reorder(graph,[wing[i] for i in chosen]+outer+[middle]);actual=[form.edge(i,j,False)*(1 if truth[i]>>j&1 else -1) for i,j in combinations(range(form.n),2)]
            with Cadical195(bootstrap_with=form.clauses) as solver:assert solver.solve(assumptions=actual+pins);assert not solver.solve(assumptions=actual+[-pins[0]])
            total+=1
    assert total==125;print('125 C22 repeated contact group reorderings and complete count cells retain actual boards; all flipped hub pins rejected')


def roster():
    for number in [1,4]:
        words=masks()[number];cells=groups(words);hist=histogram(words,7,6,(1,2));report=[]
        for first,second in product(*(range(len(cell)+1) for cell in cells)):
            report.append((f'{number}_{first}_{second}',hist[first,second],sum(1<<i for i in cells[0]),sum(1<<i for i in cells[1])))
        (OUT/f'cover{number}.tsv').write_text(''.join('\t'.join(map(str,row))+'\n' for row in report));print(number,cells,len(hist),sum(hist.values()))


def base(token,deck):
    number,first,second=map(int,token.split('_'));form=formula(number)
    for lit in units(form,7,groups(masks()[number]),(first,second)):form.add(lit)
    for mask in sorted(deck):addcard(form,SIDE[:7],mask,10)
    return form


def discover(token):
    number=token.split('_')[0];deck={int(v) for v in (WORK/number/'cards').read_text().splitlines()};form=base(token,deck)
    with Cadical195(bootstrap_with=form.clauses) as solver:
        while True:
            solver.conf_budget(max(1,180000-solver.accum_stats()['conflicts']));answer=solver.solve_limited()
            if answer is not True:break
            extra=separate(form,SIDE[:7],set(solver.get_model()),10)
            if not extra:break
            for mask in extra:addcard(form,SIDE[:7],mask,10);solver.add_clause(form.clauses[-1]);deck.add(mask)
            if solver.accum_stats()['conflicts']>=180000:answer=None;break
        Path('cards').write_text(''.join(f'{mask}\n' for mask in sorted(deck)));print(answer,len(deck));return 0 if answer is False else 10 if answer else 3


if __name__=='__main__':
    if sys.argv[1]=='cal':cal()
    elif sys.argv[1]=='roster':roster()
    elif sys.argv[1]=='discover':sys.exit(discover(sys.argv[2]))
    elif sys.argv[1]=='bind':base(sys.argv[2],set(map(int,Path('cards').read_text().splitlines()))).write(Path('input.cnf'))
    else:
        for token in sys.argv[2:]:
            if not (OUT/token).exists():task(token,[],80,60000000,OUT,str(Path(__file__).resolve()),400000000,OLD/'lrat-trim')
