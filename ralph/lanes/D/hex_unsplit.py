"""Unsplit labelled projection, keeping only return paths from each exterior site to the hexagon."""
from itertools import combinations
from time import process_time
import json,sys
from pysat.solvers import Cadical195
from book_controls import book,flags,graph_masks,bitset,reorder
from hex_fibers import masks
from equal_roles import DEST
from kernel_cnf import Cnf,ROOT,neg


def model(cycle,words,debit,edgecap,mode):
    size=len(words);fixed={(left,right):False for left,right in combinations(range(size),2) if words[left]&words[right]};form=Cnf(size,fixed);leaks=[]
    for point,word in enumerate(words):
        for site,hood in enumerate(cycle):
            if word>>site&1:continue
            used=(word&hood).bit_count();common=[form.edge(point,other) for other in range(size) if other!=point and words[other]>>site&1];form.cardinality(common,1-used,3-used)
            if used<2:
                leak=form.new();form.cardinality(common+[leak],2-used,len(common)+1);leaks.append(leak)
    form.cardinality(leaks,0,debit)
    if edgecap:form.cardinality([form.edge(left,right) for left,right in combinations(range(size),2)],0,edgecap)
    if mode in ('triangle','upper'):
        for left,mid,right in combinations(range(size),3):form.add(neg(form.edge(left,mid)),neg(form.edge(mid,right)),neg(form.edge(left,right)))
    if mode=='upper':
        for left,right in combinations(range(size),2):
            common=[form.conjunction(form.edge(left,other),form.edge(right,other)) for other in range(size) if other not in (left,right)];form.cardinality(common,0,3-(words[left]&words[right]).bit_count())
    return form


def calibrate():
    total=0
    for text in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=graph_masks(text)
        if {word.bit_count() for word in graph}!={6} or max((one&two).bit_count() for one,two in combinations(graph,2))>3:continue
        for ends in flags(graph):
            frame,(left,right)=book(graph,ends);wing=left+right;outer=sorted(set(range(22))-set(frame+wing));truth=reorder(graph,outer);words=[bitset(idx for idx,site in enumerate(wing) if graph[point]>>site&1) for point in outer];debit=sum((graph[point]&graph[site]).bit_count()==1 for point in outer for site in wing);form=model(reorder(graph,wing),words,debit,sum(word.bit_count() for word in truth)//2,'upper');sat=Cadical195(bootstrap_with=form.clauses);pins=[(1 if truth[lhs]>>rhs&1 else -1)*form.edge(lhs,rhs,False) for lhs,rhs in combinations(range(len(outer)),2)];assert sat.solve(assumptions=pins);sat.delete();total+=1
    print('PASS actual cross-weak debit, Q edge total, and all Q/wing returns on C22',total)


def make(debit,cap,mode):return model([(1<<((site+1)%6))|(1<<((site-1)%6)) for site in range(6)],masks(),debit,cap,mode)


if __name__=='__main__':
    if sys.argv[1]=='cal':calibrate()
    else:
        debit,cap=map(int,sys.argv[1:3]);mode=sys.argv[3];budget=int(sys.argv[4]);start=process_time();form=make(debit,cap,mode);sat=Cadical195(bootstrap_with=form.clauses);sat.conf_budget(budget);result=sat.solve_limited();tag=f'hex-{debit}-{cap}-{mode}';print(json.dumps(dict(tag=tag,status=str(result),conf=sat.accum_stats()['conflicts'],cpu=process_time()-start)))
        if result is False:form.write(DEST/f'{tag}.cnf')
        sat.delete()
