from itertools import combinations
from time import process_time
import json,sys
from pysat.solvers import Cadical195
from book_edge_sat import encode
from book_strata import DEST,standard
from book_controls import graph_masks,book,reorder,sites
from kernel_cnf import ROOT
from wing_plateau import restrict


def bind(form,width,n,rows,demands):
    left=next(3+i for i,word in enumerate(rows) if word.bit_count()==1);right=next(3+width+i for i in range(width) if sum(word>>i&1 for word in rows)==1);graph=standard(rows);outer=range(len(graph),n)
    for q,(first,second) in zip(outer,demands,strict=True):
        for anchor,partner,value in ((1,right,first),(2,left,second)):
            form.cardinality([form.edge(q,point) for point in (*sites(graph[anchor]),partner)],value,value)


def cal():
    db=(ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines();count=exact=positive=0
    for record in map(json.loads,(DEST/'wing-cal.jsonl').read_text().splitlines()):
        rows=record['rows'];width=len(rows);cols=[sum(row>>i&1 for row in rows) for i in range(width)];
        if [row.bit_count() for row in rows].count(1)!=1 or cols.count(1)!=1:continue
        original=graph_masks(db[record['host']]);ends=record['ends'];path,(lhs,rhs)=book(original,ends);core=[*path,*lhs,*rhs];new=reorder(original,core+sorted(set(range(22))-set(core)));graph=standard(rows);boundary=len(core);assert graph==[word&((1<<boundary)-1) for word in new[:boundary]];left=3+next(i for i,row in enumerate(rows) if row.bit_count()==1);right=3+width+cols.index(1);form,order=encode(graph,22,6,{(1,2)},True,True);permutation=sorted(range(boundary,22),key=lambda site:tuple(-(new[site]>>point&1) for point in order));truth=reorder(new,list(range(boundary))+permutation);demands=[((truth[q]&truth[1]).bit_count()+(truth[q]>>right&1),(truth[q]&truth[2]).bit_count()+(truth[q]>>left&1)) for q in range(boundary,22)];words=[truth[q]&((1<<boundary)-1) for q in range(boundary,22)];assert restrict(words,rows)==[idx for idx,pair in enumerate(demands) if pair==(3,3)];bind(form,width,22,rows,demands);pins=[(1 if truth[a]>>b&1 else -1)*form.edge(a,b,simplify=False) for a,b in combinations(range(22),2) if b>=boundary];engine=Cadical195(bootstrap_with=form.clauses);assert engine.solve(assumptions=pins);engine.delete();count+=1;exact+=len(demands);positive+=demands.count((3,3))
    assert count==27 and positive;print('PASS ordinary labelled planted edge and literal plateau-contact CNFs',count,'selected actual Q-mask tests',exact,'satisfying both unmodified target RHSs',positive)


def solve(record,full,cap,dump):
    start=process_time();rows=record['rows'];graph=standard(rows);form,_=encode(graph,40,9,{(1,2)},True,full);bind(form,8,40,rows,[(3,3)]*21);sat=Cadical195(bootstrap_with=form.clauses);sat.conf_budget(cap);verdict=sat.solve_limited();row=dict(id=record['id'],full=full,status=str(verdict),conf=sat.accum_stats()['conflicts'],cpu=process_time()-start);sat.delete()
    if dump or verdict is False:form.write(DEST/f"plateau-{record['id']}-{'full' if full else 'edge'}.cnf")
    return row


if __name__=='__main__':
    if sys.argv[1]=='cal':cal()
    else:
        full=bool(int(sys.argv[1]));cap,part,mod=map(int,sys.argv[2:5]);rows=[r for r in map(json.loads,(DEST/'plat.jsonl').read_text().splitlines()) if r['status']=='fractional']
        for record in rows[part::mod]:print(json.dumps(solve(record,full,cap,False)),flush=True)
