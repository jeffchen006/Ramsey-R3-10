"""Rebind scout R's ordinary DIMACS from named star neighborhoods and Hall cuts."""
from collections import Counter
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
import sys
from pysat.card import CardEnc, EncType
from pysat.formula import IDPool
from pysat.solvers import Cadical195
from middle16_roster import ROOT, PAIRS

TRUE=10**9

def physical(word):
    copies=[]
    for index, endpoints in enumerate(PAIRS):
        times=sum((part>>index)&1 for part in word)
        copies.extend([endpoints]*times)
    degree=Counter(pole for pair in copies for pole in pair)
    assert len(copies)==6 and max(degree.values())<=2
    masks=[sum(1<<pole for pole in pair) for pair in copies]
    return sorted(masks+[1<<pole for pole in range(7) for _ in range(2-degree[pole])])

@lru_cache(None)
def hall(links,poles):
    candidates=set()
    for region in range(1<<poles):
        inside=[idx for idx,mask in enumerate(links) if not mask&~region]
        for subset in combinations(inside,region.bit_count()+1):candidates.add(sum(1<<idx for idx in subset))
    circuits=[]
    for subset in sorted(candidates,key=int.bit_count):
        if not any(prior&subset==prior for prior in circuits):circuits.append(subset)
    return sorted(circuits)

def compile_graph(poles,blocks,degree,wing_total,y_total,budget,broad=False):
    y_masks,left_masks,right_masks=blocks
    neighborhoods=[{1,2,*range(3,3+poles)},set(),set()]+[{0} for _ in range(poles)]
    width=len(neighborhoods);cells=[];contacts=[]
    for role,masks in enumerate(blocks):
        cell=list(range(width+len(contacts),width+len(contacts)+len(masks)));cells.append(cell)
        for vertex,mask in zip(cell,masks):
            fixed={pole+3 for pole in range(poles) if mask&(1<<pole)}
            if role: fixed.add(role)
            for fixed_vertex in fixed: neighborhoods[fixed_vertex].add(vertex)
            contacts.append(fixed)
    neighborhoods[1].add(0);neighborhoods[2].add(0)
    y_sites,left,right=cells;vertices=range(width+len(contacts));pairs=list(combinations(vertices,2))
    pool=IDPool();edges=[[ -TRUE for _ in vertices] for _ in vertices]
    for lo,hi in pairs:
        if lo<width: value=TRUE if hi in neighborhoods[lo] else -TRUE
        elif contacts[lo-width]&contacts[hi-width]: value=-TRUE
        else: value=pool.id()
        edges[lo][hi]=edges[hi][lo]=value
    clauses=[]
    def include(row):
        if TRUE not in row: clauses.append([literal for literal in row if literal!=-TRUE])
    def upper(literals,threshold,guard=-TRUE):
        threshold-=literals.count(TRUE); variables=[lit for lit in literals if abs(lit)!=TRUE]
        if threshold<0: include([guard])
        elif threshold<len(variables):
            constraints=CardEnc.atmost(variables,bound=threshold,vpool=pool,encoding=EncType.seqcounter).clauses
            clauses.extend(constraints if guard==-TRUE else [[guard]+clause for clause in constraints])
    def lower(literals,threshold,guard=-TRUE):upper([-lit for lit in literals],len(literals)-threshold,guard)
    def exact(literals,threshold):upper(literals,threshold);lower(literals,threshold)
    for vertex in vertices:exact(edges[vertex],degree)
    exact([edges[lo][hi] for lo,hi in combinations(y_sites,2)],y_total)
    exact([edges[lo][hi] for lo,hi in product(left,right)],wing_total)
    for first,second,third in combinations(vertices,3):include([-edges[first][second],-edges[second][third],-edges[first][third]])
    debits=[]
    for lo,hi in pairs:
        if lo>=width or edges[lo][hi]==TRUE:continue
        common=[edges[hi][site] for site in sorted(neighborhoods[lo])]; upper(common,3)
        if (lo,hi)==(1,2):continue
        debit=-TRUE
        if broad or (3<=lo and hi>=width):debit=pool.id();debits.append(debit)
        lower(common,2,debit);lower(common,1)
    upper(debits,budget)
    for subset in hall(tuple(y_masks),poles):
        points=[vertex for index,vertex in enumerate(y_sites) if subset&(1<<index)]
        include([edges[lo][hi] for lo,hi in combinations(points,2)])
    for lo,hi in combinations(range(width,len(vertices)),2):
        fixed=len(contacts[lo-width]&contacts[hi-width]);
        if fixed<2:continue
        candidates=[(edges[lo][via],edges[hi][via]) for via in range(width,len(vertices)) if max(abs(edges[lo][via]),abs(edges[hi][via]))<TRUE]
        for walks in combinations(candidates,4-fixed):include([-lit for walk in walks for lit in walk])
    return pool.top,clauses,edges

def target(rec,path):
    blocks=(rec['Y'],physical(rec['word'][:2]),physical(rec['word'][2:]))
    size,clauses,_=compile_graph(7,blocks,9,17,16,1)
    with path.open('w') as output:
        print('p cnf',size,len(clauses),file=output)
        output.writelines(' '.join(map(str,row+[0]))+'\n' for row in clauses)

def calibration():
    import networkx as nx
    count=Counter()
    for line in (ROOT/'gluing/val/r3_7_22.g6').read_bytes().splitlines():
        graph=nx.from_graph6_bytes(line);stars=[set(graph[site]) for site in graph]
        if any(len(star)!=6 for star in stars):continue
        count['regular']+=1;codegrees=[len(stars[l]&stars[r]) for l,r in combinations(graph,2)]
        if max(codegrees)>3:continue
        count['hosts']+=1
        for left,right in combinations(graph,2):
            common=stars[left]&stars[right]
            if len(common)!=1:continue
            middle,=common;poles=sorted(stars[middle]-{left,right});wings=[sorted(stars[tip]-{middle}) for tip in (left,right)]
            untouched=sorted(set(graph)-{middle,left,right,*poles,*wings[0],*wings[1]});blocks=[untouched,*wings]
            masks=[[sum(1<<index for index,pole in enumerate(poles) if pole in stars[site]) for site in cell] for cell in blocks]
            order=[middle,left,right,*poles,*untouched,*wings[0],*wings[1]]
            _,clauses,table=compile_graph(len(poles),masks,6,sum(graph.has_edge(*pair) for pair in product(*wings)),graph.subgraph(untouched).number_of_edges(),codegrees.count(1)-1,broad=True)
            pins=[]
            for lo,hi in combinations(range(len(order)),2):
                literal=table[lo][hi]*(1 if graph.has_edge(order[lo],order[hi]) else -1)
                assert literal!=-TRUE
                if literal!=TRUE:pins.append(literal)
            with Cadical195(bootstrap_with=clauses) as solver:
                assert solver.solve(assumptions=pins);count['planted']+=1
                assert not solver.solve(assumptions=[-pins[0]]+pins[1:]);count['mutated_rejected']+=1
    print(dict(count)); assert count==dict(regular=10,hosts=3,planted=125,mutated_rejected=125)

if __name__=='__main__':calibration()
