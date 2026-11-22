"""At b, classify neighbours in H=G-N[b] by their codegree against b."""
from collections import Counter
from itertools import combinations
from time import process_time
import json,sys
from pysat.solvers import Cadical195
from book_strata import DEST,independent_sets
from book_controls import graph_masks,bitset
from kernel_cnf import ROOT,Cnf,neg


def projection(rows,two,degree,limit,plant=None):
    width=len(rows);low=[max(0,3*(degree-1)-limit-2*row.bit_count()) for row in rows];ceiling=[degree-1-row.bit_count() for row in rows];alpha=max(word.bit_count() for word in independent_sets(rows));
    if max(low)>two or any(a>b for a,b in zip(low,ceiling)) or sum(low)>two*min(degree-2,alpha):return 'mass',None
    if any((a&b&c).bit_count()>=3 for a,b,c in combinations(rows,3)) or any((a&b).bit_count()>3 for a,b in combinations(rows,2)):return 'biclique',None
    form=Cnf(width+two,{});cell=[[form.edge(i,width+j) for j in range(two)] for i in range(width)];
    for point in range(width):form.cardinality(cell[point],low[point],ceiling[point]);
    for j in range(two):
        form.cardinality([row[j] for row in cell],0,degree-2)
        for a,b in combinations(range(width),2):
            if rows[a]>>b&1:form.add(-cell[a][j],-cell[b][j])
        for a in range(width):form.cardinality([cell[b][j] for b in range(width) if rows[a]>>b&1],0,3)
    for a,b in combinations(range(width),2):form.cardinality([form.conjunction(cell[a][j],cell[b][j]) for j in range(two)],0,3-(rows[a]&rows[b]).bit_count())
    for i,j in combinations(range(two),2):form.cardinality([form.conjunction(row[i],row[j]) for row in cell],0,3)
    for i,j in zip(range(two),range(1,two)):
        prefix=True
        for row in cell:
            left,right=row[i],row[j];form.add(neg(prefix),left,-right);nextp=form.new();form.add(neg(prefix),-left,-right,nextp);form.add(neg(prefix),left,right,nextp);prefix=nextp
    engine=Cadical195(bootstrap_with=form.clauses);pins=[]
    if plant is not None:
        ordered=sorted(plant,key=lambda word:tuple(-(word>>p&1) for p in range(width)))
        for j,word in enumerate(ordered):pins.extend(cell[p][j]*(1 if word>>p&1 else -1) for p in range(width))
    engine.conf_budget(15000);res=engine.solve_limited(assumptions=pins);other=None
    if res:
        sol=set(engine.get_model());other=[bitset(p for p in range(width) if cell[p][j] in sol) for j in range(two)]
    engine.delete();return ('possible' if res else 'unsat' if res is False else 'cap'),other


def cal():
    count=0
    for text in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=graph_masks(text)
        if {row.bit_count() for row in graph}!={6} or max((a&b).bit_count() for a,b in combinations(graph,2))>3:continue
        for point,hood in enumerate(graph):
            single=[i for i,row in enumerate(graph) if i!=point and (row&hood).bit_count()==1];two=[i for i,row in enumerate(graph) if i!=point and (row&hood).bit_count()==2];
            if not single:continue
            assert len(two)==15-2*len(single);rows=[bitset(j for j,v in enumerate(single) if graph[u]>>v&1) for u in single];upper=max(sum((graph[v]&hood).bit_count() for v in range(22) if graph[u]>>v&1) for u in single);plant=[bitset(j for j,site in enumerate(single) if graph[v]>>site&1) for v in two];status,_=projection(rows,len(two),6,upper,plant);assert status=='possible';count+=1
    print('PASS all active b in planted cubic-codegree-capped regular C22 controls:',count)


if __name__=='__main__':
    if sys.argv[1]=='cal':cal()
    else:
        for limit in map(int,sys.argv[1:]):
            for size in range(1,10):
                for idx,text in enumerate((DEST/f's{size}.g6').read_text().splitlines()):
                    rows=graph_masks(text);start=process_time();status,witness=projection(rows,18-2*size,9,limit);print(json.dumps(dict(limit=limit,k=size,id=idx,rows=rows,status=status,masks=witness,cpu=process_time()-start),separators=(',',':')))
