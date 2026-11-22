"""Paired contact-only and actual-exterior-edge relaxations on a labelled boundary."""
from itertools import combinations
from time import process_time
import json,sys
from pysat.solvers import Cadical195
from book_edge_margins import targets
from book_strata import DEST,plants,independent_sets
from book_controls import sites,reorder
from kernel_cnf import Cnf,neg


def encode(rows,n,degree,weak,edges,full=False):
    width=len(rows);inner=range(width);outer=range(width,n);fixed={(a,b):bool(rows[a]>>b&1) for a,b in combinations(inner,2)};form=Cnf(n,fixed);edge=form.edge
    order=sorted(inner,key=lambda site:(0 if full and site==0 else 1,-rows[site].bit_count(),site));top=degree
    if full:
        count=degree-rows[0].bit_count()
        for idx,point in enumerate(outer):form.add(edge(0,point) if idx<count else -edge(0,point))
    for left,right in zip(outer,outer[1:]):
        prefix=True
        for site in order:
            first,second=edge(site,left),edge(site,right);form.add(neg(prefix),first,-second);nextprefix=form.new();form.add(neg(prefix),-first,-second,nextprefix);form.add(neg(prefix),first,second,nextprefix);prefix=nextprefix
    for site,row in enumerate(rows):
        rest=degree-row.bit_count();form.cardinality([edge(site,q) for q in outer],rest,rest)
    for a,b in combinations(inner,2):
        if rows[a]>>b&1:
            for q in outer:form.add(-edge(a,q),-edge(b,q))
        else:
            common=(rows[a]&rows[b]).bit_count();low=max(0,1-common);high=(1 if (a,b) in weak else 3)-common
            if high==0:
                for q in outer:form.add(-edge(a,q),-edge(b,q))
            else:form.cardinality([form.conjunction(edge(a,q),edge(b,q)) for q in outer],low,high)
    independent=independent_sets(rows)
    for word in independent:
        if word.bit_count()>top:form.add();break
        if word.bit_count()!=top:continue
        for q in outer:form.add(*(edge(site,q) for site in sites(word)))
    for q in outer:
        for row in rows:
            if row.bit_count()>3:
                for four in combinations(sites(row),4):form.add(*(-edge(site,q) for site in four))
        if edges:form.cardinality([edge(q,x) for x in range(n) if x!=q],degree,degree)
        else:form.cardinality([edge(q,x) for x in inner],0,degree)
    if edges:
        target=(sum(row.bit_count() for row in rows)+degree*(n-2*width))//2;form.cardinality([edge(q,r) for q,r in combinations(outer,2)],target,target)
        for q,r in combinations(outer,2):
            for site in inner:form.add(-edge(q,r),-edge(q,site),-edge(r,site))
        for q,r,s in combinations(outer,3):form.add(-edge(q,r),-edge(q,s),-edge(r,s))
        for word in independent:
            if word.bit_count()!=degree-1:continue
            avoid=[]
            for q in outer:
                blind=form.new();form.add(*(edge(site,q) for site in sites(word)),blind);avoid.append(blind)
            for i,j in combinations(range(len(outer)),2):form.add(-avoid[i],-avoid[j],edge(outer[i],outer[j]))
    if full:
        assert edges
        for first,second in combinations(range(n),2):
            if second<width:continue
            witnesses=[form.conjunction(edge(first,other),edge(second,other)) for other in range(n) if other not in (first,second)];form.cardinality(witnesses,0,3);form.add(edge(first,second),*witnesses)
    return form,order


def calibration():
    done=0
    for key,truth,width in plants():
        mask=(1<<width)-1;graph=[row&mask for row in truth[:width]];n=len(truth);outside=range(width,n)
        for edges,full in ((False,False),(True,False),(True,True)):
            form,order=encode(graph,n,6,{(1,2),(8,9)},edges,full);perm=sorted(outside,key=lambda point:tuple(-(truth[point]>>site&1) for site in order));labelled=reorder(truth,[*range(width),*perm]);pins=[form.edge(a,b,simplify=False)*(1 if labelled[a]>>b&1 else -1) for a,b in combinations(range(n),2) if b>=width and (edges or a<width)];sat=Cadical195(bootstrap_with=form.clauses);assert sat.solve(assumptions=pins);pins[0]*=-1;assert not sat.solve(assumptions=pins);sat.delete();done+=1
    print('PASS planted contact and edge CNFs with their exact permuted labelled models and single-edge mutants',done)


def run(key,graph,weak,edges,cap,output):
    start=process_time();form,_=encode(graph,40,9,weak,edges);sat=Cadical195(bootstrap_with=form.clauses);sat.conf_budget(cap);result=sat.solve_limited();metrics=dict(id=key,edges=edges,status=str(result),clauses=len(form.clauses),vars=form.nvars,conf=sat.accum_stats()['conflicts']);
    if result:
        positive=set(sat.get_model());metrics['Q']=[sum(1<<other for other in range(40) if other!=site and form.edge(site,other,simplify=False) in positive) for site in range(22,40)]
    sat.delete();metrics['cpu']=process_time()-start
    if result is False and output:form.write(DEST/('sat-'+'-'.join(map(str,key))+('-edge' if edges else '-mask')+'.cnf'))
    return metrics


if __name__=='__main__':
    if sys.argv[1]=='cal':calibration()
    else:
        cap,shard,mod=map(int,sys.argv[1:4]);
        for idx,(key,graph,weak) in enumerate(targets()):
            if idx%mod==shard:
                for edges in (False,True):print(json.dumps(run(key,graph,weak,edges,cap,True),separators=(',',':')),flush=True)
