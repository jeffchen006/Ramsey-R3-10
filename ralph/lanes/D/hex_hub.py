"""Unsplit physical hub arm with an explicit budget of additional weak pairs."""
from itertools import combinations
from time import process_time
import json,sys
from pysat.solvers import Cadical195
from hex_fibers import masks
from equal_roles import DEST
from kernel_cnf import Cnf,ROOT,neg
from book_controls import book,flags,graph_masks,bitset,reorder


def build(wing,words,degree,debit,edges,upper,markers,protect=False):
    size=len(words);hub=size;fixed={(lhs,rhs):False for lhs,rhs in combinations(range(size),2) if words[lhs]&words[rhs]};form=Cnf(size+1,fixed);leaks=[];ys=[form.edge(hub,point) for point in range(size)]
    def lower(terms,floor,guard=False,strict=False):
        if floor<=0:return
        leak=False if strict else form.new();flags=form.thresholds(terms,floor);form.add(guard,flags[floor-1],leak);form.add(guard,flags[floor-2] if floor>=2 else True);leaks.append(leak)
    form.cardinality(ys,degree-2,degree-2)
    for site in range(len(wing)):
        terms=[var for point,var in enumerate(ys) if words[point]>>site&1];form.cardinality(terms,0,2);lower(terms,1,strict=protect)
    for point,word in enumerate(words):
        star=[form.edge(point,other) for other in range(size) if point!=other];adjusted=star+[neg(ys[point])];form.cardinality(adjusted,degree-5,degree-3 if protect else degree-1)
        if markers:
            # Two excess units above d-3 in (d_Q + 1 - y) require that many weak endpoint-Q pairs.
            levels=form.thresholds(adjusted,degree-1)
            for limit in (degree-3,degree-2):leaks.append(levels[limit])
        shared=[form.conjunction(form.edge(point,other),ys[other]) for other in range(size) if point!=other];form.cardinality(shared,0,3);lower(shared,2,ys[point],protect);
        for other in range(size):
            if point!=other:form.add(neg(ys[point]),neg(ys[other]),neg(form.edge(point,other)))
        for site,hood in enumerate(wing):
            if word>>site&1:continue
            used=(word&hood).bit_count();terms=[form.edge(point,other) for other in range(size) if point!=other and words[other]>>site&1];form.cardinality(terms,0,3-used);lower(terms,2-used)
    form.cardinality(leaks,0,debit)
    if edges:form.cardinality([form.edge(lhs,rhs) for lhs,rhs in combinations(range(size),2)],edges,edges)
    if upper:
        for lhs,rhs in combinations(range(size),2):
            shared=[form.conjunction(form.edge(lhs,other),form.edge(rhs,other)) for other in range(size+1) if other not in (lhs,rhs)];form.cardinality(shared,0,3-(words[lhs]&words[rhs]).bit_count())
            for other in range(lhs):form.add(neg(form.edge(lhs,rhs)),neg(form.edge(lhs,other)),neg(form.edge(rhs,other)))
    return form


def calibrate():
    count=0
    for text in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=graph_masks(text)
        if {word.bit_count() for word in graph}!={6} or max((one&two).bit_count() for one,two in combinations(graph,2))>3:continue
        for ends in flags(graph):
            frame,(left,right)=book(graph,ends);wing=left+right;outer=sorted(set(range(22))-set(frame+wing));words=[bitset(idx for idx,site in enumerate(wing) if graph[point]>>site&1) for point in outer];edges=sum(word.bit_count() for word in reorder(graph,outer))//2;truth=reorder(graph,outer+[frame[0]]);pairs=set((min(lhs,rhs),max(lhs,rhs)) for lhs in outer for rhs in (*wing,*frame));pairs.update((min(frame[0],rhs),max(frame[0],rhs)) for rhs in wing);debit=sum((graph[lhs]&graph[rhs]).bit_count()==1 for lhs,rhs in pairs);form=build(reorder(graph,wing),words,6,debit,edges,True,True);sat=Cadical195(bootstrap_with=form.clauses);pins=[form.edge(lhs,rhs,False)*(1 if truth[lhs]>>rhs&1 else -1) for lhs,rhs in combinations(range(len(truth)),2)];assert sat.solve(assumptions=pins);sat.delete();count+=1
    print('PASS independent physical weak-pair counts and unsplit hub-Q matrices on C22',count)


def make(debit,edges,upper,markers):return build([(1<<((site+1)%6))|(1<<((site-1)%6)) for site in range(6)],masks(),9,debit,edges,upper,markers==1,markers==2)


if __name__=='__main__':
    if sys.argv[1]=='cal':calibrate()
    else:
        debit,edges,upper,markers,cap=map(int,sys.argv[1:]);start=process_time();form=make(debit,edges,upper,markers);sat=Cadical195(bootstrap_with=form.clauses);sat.conf_budget(cap);result=sat.solve_limited();tag=f'hub-{debit}-{edges}-{upper}-{markers}';print(json.dumps(dict(tag=tag,status=str(result),conf=sat.accum_stats()['conflicts'],cpu=process_time()-start)));sat.delete()
        if result is False:form.write(DEST/f'{tag}.cnf')
