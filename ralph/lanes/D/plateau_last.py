from itertools import combinations
from time import process_time
import json,sys
from pysat.solvers import Cadical195
from book_edge_sat import encode
from book_strata import DEST,standard,plants
from book_controls import sites,reorder
from kernel_cnf import neg


def install(form,graph,root,partners,n,actual=None):
    for other in range(n):
        if other==root or other<len(graph) and graph[root]>>other&1:continue
        witnesses=[form.conjunction(form.edge(root,middle),form.edge(other,middle)) for middle in range(n) if middle not in (root,other)];guard=form.edge(root,other)
        if other in partners:form.add(neg(guard));target=1 if actual is None else (actual[root]&actual[other]).bit_count();form.cardinality(witnesses,target,target);continue
        extra=[form.edge(who,other) for who in partners];start=len(form.clauses);target=3 if actual is None else (actual[root]&actual[other]).bit_count()+sum(actual[who]>>other&1 for who in partners);form.cardinality(witnesses+extra,target,target)
        if guard is not False:
            for row in form.clauses[start:]:row.append(guard)


def calibrate():
    reports=0
    for key,truth,width in plants():
        graph=[row&((1<<width)-1) for row in truth[:width]];form,order=encode(graph,22,6,{(1,2),(8,9)},True,True);outer=sorted(range(width,22),key=lambda site:tuple(-(truth[site]>>p&1) for p in order));labelled=reorder(truth,[*range(width),*outer]);
        for root in (1,2):
            partners=next((a,b) for a,b in combinations(range(width),2) if a!=root and b!=root and not(graph[root]&(1<<a|1<<b)) and graph[a]>>b&1);install(form,graph,root,partners,22,labelled)
        pins=[(1 if labelled[a]>>b&1 else -1)*form.edge(a,b,simplify=False) for a,b in combinations(range(22),2) if b>=width];sat=Cadical195(bootstrap_with=form.clauses);assert sat.solve(assumptions=pins);pins[0]*=-1;assert not sat.solve(assumptions=pins);sat.delete();reports+=1
    print('PASS installed guarded codegree rows, literal labelled RHS and 18 C22 mutated edge tests',reports)


def solve(record,family,cap,dump):
    start=process_time();rows=family[record['id']];graph=standard(rows);form,_=encode(graph,40,9,{(1,2)},True,False);left=3+next(i for i,row in enumerate(rows) if row.bit_count()==1);right=11+next(i for i in range(8) if sum(row>>i&1 for row in rows)==1);first,second=record['second']
    for root,pair in ((1,(2,right)),(2,(1,left)),(left,(2,first)),(right,(1,second))):install(form,graph,root,pair,40)
    sat=Cadical195(bootstrap_with=form.clauses);sat.conf_budget(cap);ans=sat.solve_limited();out=dict(id=record['id'],second=record['second'],status=str(ans),conf=sat.accum_stats()['conflicts'],cpu=process_time()-start);sat.delete()
    if dump or ans is False:form.write(DEST/f"walk-{record['id']}-{first}-{second}.cnf")
    return out


if __name__=='__main__':
    if sys.argv[1]=='cal':calibrate()
    else:
        cap,part,mod=map(int,sys.argv[1:4]);records=[row for row in map(json.loads,(DEST/'walk-both.jsonl').read_text().splitlines()) if row['status']=='fractional'];family={r['id']:r['rows'] for r in map(json.loads,(DEST/'plat.jsonl').read_text().splitlines())};
        for rec in records[part::mod]:print(json.dumps(solve(rec,family,cap,True)),flush=True)
