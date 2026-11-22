import json
import sys
from collections import Counter
from itertools import combinations,product
from pathlib import Path
from patch23 import patch_data,build,census,ROOT,Cadical195
from flap23 import addcard,separate,edges
from wing24 import OUT,graph_masks,sites
from wingaudit23 import independent
from book_controls import book,flags,reorder,bitset

SIDE=[0,0,1,1,1,0];GEN=OUT/'generic'

def abstract(degrees,link):
    rows=[0]*6;sides=SIDE.copy()
    def edge(first,second):rows[first]|=1<<second;rows[second]|=1<<first
    for first,second in [(0,2),(0,3),(1,2),(1,3),(0,4),(2,5)]:edge(first,second)
    if link:edge(4,5)
    for site in range(6):
        assert rows[site].bit_count()<=degrees[site]
        for _ in range(degrees[site]-rows[site].bit_count()):rows.append(0);sides.append(1-sides[site]);edge(site,len(rows)-1)
    return rows,sides

def roster():
    records=[];keys=[];points=list(range(6));hist=Counter()
    for cubic,first,second,link in product((3,4),(2,3),(2,3),(0,1)):
        if cubic==4 and first>second:continue
        degrees=[3,2+(cubic==4),3,3,first,second];rows,sides=abstract(degrees,link);decks=[];census(*patch_data(rows,sides,points,9),21,1,lambda profile,loss:decks.append(tuple(sorted(mask for mask,count in profile.items() for _ in range(count)))));decks.sort();size=len(rows);core=rows.copy()+[0,0,0]
        for site,side in enumerate(sides):tip=size+side;core[site]|=1<<tip;core[tip]|=1<<site
        for tip in (size,size+1):core[tip]|=1<<(size+2);core[size+2]|=1<<tip
        assert independent(core,points,(1<<len(core))-1,21,1)==set(decks);records.append(dict(degrees=degrees,link=link,decks=decks));hist[cubic,len(decks)]+=1;keys.extend(f'u{len(records)-1}_{idx}' for idx in range(len(decks)))
    (GEN/'spec.json').write_text(json.dumps(records));(GEN/'keys').write_text('\n'.join(keys)+'\n');print(len(records),'relaxed local square geometries',len(keys),'keys',hist)

def construct(rows,sides,words,degree,target):
    points=list(range(6));form=build(rows,sides,points,points,words,None,degree,target)
    for pos in range(len(words)-1):
        if words[pos]==words[pos+1]:form.add(-form.edge(6+pos,form.n-1),form.edge(7+pos,form.n-1))
    return form

def formula_generic(key):
    number,idx=map(int,key[1:].split('_'));row=json.loads((GEN/'spec.json').read_text())[number];rows,sides=abstract(row['degrees'],row['link']);form=construct(rows,sides,row['decks'][idx],9,True);cards=GEN/f'{key}.cards'
    if key.startswith(('v','w')) and cards.is_file():
        for mask in map(int,cards.read_text().splitlines()):addcard(form,SIDE,mask,10)
    return form

def discover(key):
    form=formula_generic(key);witnesses=set();limit=90000
    with Cadical195(bootstrap_with=form.clauses) as solver:
        while True:
            solver.conf_budget(max(1,limit-solver.accum_stats()['conflicts']));status=solver.solve_limited()
            if status is not True:break
            patches=separate(form,SIDE,set(solver.get_model()),10,128)
            if not patches:
                positive=set(solver.get_model());order=form.n+2;adj=[0]*order
                for lhs,rhs in combinations(range(order),2):
                    value=edges(form,SIDE,lhs,rhs)
                    if value is True or type(value) is int and value in positive:adj[lhs]|=1<<rhs;adj[rhs]|=1<<lhs
                import networkx as nx
                graph=nx.Graph();graph.add_nodes_from(range(order));graph.add_edges_from((lhs,rhs) for lhs,rhs in combinations(range(order),2) if adj[lhs]>>rhs&1);assert max(map(len,nx.find_cliques(graph)))<=2 and max(map(len,nx.find_cliques(nx.complement(graph))))<10;(GEN/f'{key}.partial.g6').write_bytes(nx.to_graph6_bytes(graph,header=False));break
            for mask in patches:addcard(form,SIDE,mask,10);solver.add_clause(form.clauses[-1]);witnesses.add(mask)
            if solver.accum_stats()['conflicts']>=limit:status=None;break
    print(key,'UNSAT' if status is False else 'RELAXED_MODEL' if status else 'cap',len(witnesses),flush=True)
    (GEN/f'{key}.cards').write_text(''.join(str(mask)+'\n' for mask in sorted(witnesses)));return 0 if status is False else 10 if status is True else 3

def calibrate():
    count=0
    for line in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=graph_masks(line)
        if {row.bit_count() for row in graph}!={6} or max((lhs&rhs).bit_count() for lhs,rhs in combinations(graph,2))>3:continue
        for ends in flags(graph):
            (hub,first,second),(left,right)=book(graph,ends);wing=left+right;actual=reorder(graph,wing)
            for anchors in combinations(range(5),2):
                for opposite in combinations(sites(actual[anchors[0]]&actual[anchors[1]]),2):
                    for leftpin in sites(actual[anchors[0]]&~bitset(opposite)):
                        for rightpin in sites(actual[opposite[0]]&~bitset(anchors)):
                            points=[*anchors,*opposite,leftpin,rightpin]
                            if actual[anchors[1]]>>leftpin&1 or actual[opposite[1]]>>rightpin&1:continue
                            rows,sides=abstract([actual[site].bit_count() for site in points],actual[leftpin]>>rightpin&1);outer=set(range(22))-set(wing)-{hub,first,second};word=lambda point:bitset(bit for bit,site in enumerate(points) if graph[point]>>wing[site]&1);outer=sorted(outer,key=lambda site:(word(site),graph[hub]>>site&1));form=construct(rows,sides,list(map(word,outer)),6,False);truth=reorder(graph,[*[wing[site] for site in points],*outer,hub]);pins=[form.edge(lhs,rhs,False)*(1 if truth[lhs]>>rhs&1 else -1) for lhs,rhs in combinations(range(form.n),2)];
                            with Cadical195(bootstrap_with=form.clauses) as solver:assert solver.solve(assumptions=pins) and not separate(form,SIDE,set(solver.get_model()),7)
                            count+=1
    print('literal 6-site C22 square+2 flaps plants',count);return count

if __name__=='__main__':
    if sys.argv[1]=='roster':roster()
    elif sys.argv[1]=='cal':calibrate()
    else:sys.exit(discover(sys.argv[1]))
