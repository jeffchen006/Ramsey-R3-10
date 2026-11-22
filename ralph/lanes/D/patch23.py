from collections import Counter
from functools import lru_cache
from itertools import combinations,product
from pathlib import Path
import json
import os
import sys

from closure22 import ROOT,Cadical195,task
from book_controls import bitset,book,flags,graph_masks,reorder,sites
from patchbind23 import build
from path_fibers import census

STORE=ROOT/'scratch/D/c6r23'; OLD=ROOT/'scratch/D/m14r22'


def patch_data(wing,side,points,degree):
    demand=[degree-1-wing[site].bit_count() for site in points];bounds={}
    for left,right in combinations(range(len(points)),2):
        first,second=points[left],points[right]
        if wing[first]>>second&1:continue
        used=(wing[first]&wing[second]).bit_count()+int(side[first]==side[second]);bounds[left,right]=(2-used,3-used)
    return reorder(wing,points),demand,bounds


def choose(wing,side):
    groups=[[site for site,value in enumerate(side) if value==wanted] for wanted in (0,1)]
    candidates=[]
    for left,right in product(*(combinations(group,3) for group in groups)):
        points=left+right;rows,demand,bounds=patch_data(wing,side,points,9)
        slack=21+sum(hi for lo,hi in bounds.values())-sum(demand)
        candidates.append((slack,-sum(word.bit_count() for word in rows),points))
    return min(candidates)


def roster():
    reports=[];tot=0
    for number,word in enumerate((STORE/'shapes.g6').read_text().splitlines(),1):
        wing=graph_masks(word);side=[0]*8+[1]*8;slack,edges,points=choose(wing,side);rows,demand,bounds=patch_data(wing,side,points,9);decks=[]
        def save(profile,leak):decks.append(sorted(mask for mask,qty in profile.items() for _ in range(qty)))
        _,leaks,_=census(rows,demand,bounds,21,1,save);assert len(set(map(tuple,decks)))==len(decks)
        meta=dict(shape=number,g6=word,pinned=points,slack=slack,patch_edges=-edges//2,count=len(decks),debit=leaks)
        print(json.dumps(meta),flush=True);reports.append(meta);tot+=len(decks)
        (STORE/f'decks{number}.jsonl').write_text(''.join(json.dumps(deck)+'\n' for deck in decks))
    (STORE/'shapes.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in reports));print('all shape-decks',tot,flush=True)


def physical(token):
    number,idx=map(int,token.split('_'));row=json.loads((STORE/'shapes.jsonl').read_text().splitlines()[number-1]);words=json.loads((STORE/f'decks{number}.jsonl').read_text().splitlines()[idx]);wing=graph_masks(row['g6']);return build(wing,[0]*8+[1]*8,list(range(16)),row['pinned'],words,44,9,True)


def calibration():
    count=0
    for text in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=graph_masks(text)
        if {word.bit_count() for word in graph}!={6} or max((one&two).bit_count() for one,two in combinations(graph,2))>3:continue
        for ends in flags(graph):
            frame,(left,right)=book(graph,ends);wing=left+right;side=[0]*len(left)+[1]*len(right);outside=sorted(set(range(22))-set(frame+wing));points=[0,1,2,5,6,7];rows=reorder(graph,wing);words=[bitset(idx for idx,site in enumerate(points) if graph[p]>>wing[site]&1) for p in outside];fixed=[wing[site] for site in points];debit=sum((graph[u]&graph[v]).bit_count()==1 for u,v in combinations(fixed,2) if not graph[u]>>v&1);array=patch_data(rows,side,points,6);assert census(*array,len(outside),debit,None,Counter(words))[0]==1
            edges=sum(word.bit_count() for word in reorder(graph,outside))//2;form=build(rows,side,list(range(10)),points,words,edges,6,False);true=reorder(graph,list(wing)+outside+[frame[0]]);pins=[form.edge(i,j,False)*(1 if true[i]>>j&1 else -1) for i,j in combinations(range(len(true)),2)];mut=form.edge(0,10,False)
            with Cadical195(bootstrap_with=form.clauses) as solver:assert solver.solve(assumptions=pins);assert not solver.solve(assumptions=[-lit if abs(lit)==mut else lit for lit in pins]);count+=1
    assert count==125;print('125 C22 unsorted patch populations/complete physical boards pass, 125 altered wing–Q edges reject')


def stage(token,program):
    if program=='discover':Path('cards').write_text('');return
    physical(token).write(Path('input.cnf'))


if __name__=='__main__':
    if sys.argv[1]=='roster':roster()
    elif sys.argv[1]=='cal':calibration()
    elif sys.argv[1] in ('discover','bind'):stage(sys.argv[2],sys.argv[1])
    else:
        for token in sys.argv[2:]:task(token,[],20,30000000,STORE,str(Path(__file__).resolve()),int(os.environ.get('PATCHBUDGET','370000000')),OLD/'lrat-trim')
