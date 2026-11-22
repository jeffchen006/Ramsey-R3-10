"""One incidence variable per possible physical exterior mask/copy, not per Q label."""
from collections import Counter
from itertools import combinations
from time import process_time
import json,sys
import numpy as np
from pysat.solvers import Cadical195
from kernel_cnf import Cnf
from book_strata import DEST,standard,independent_sets
from book_controls import sites
from wing_population import system
from wing_plateau import restrict


def encode(rows,masks,degree,order,edge_mode):
    graph=standard(rows);width=len(graph);pop=order-width;slots=[];masks=sorted(set(map(int,masks)));seeds=independent_sets(graph);avoid=np.zeros(1<<width,dtype=np.bool_)
    for word in seeds:
        if word.bit_count()==degree-1:avoid[word]=True
    for site in range(width):
        step=1<<site;layer=avoid.reshape(-1,2*step);layer[:,step:]|=layer[:,:step]
    full=(1<<width)-1;form=Cnf(0,{});copy=[]
    for mask in masks:
        limit=pop
        if mask.bit_count()>=4 or mask and avoid[full^mask]:limit=1
        for site in sites(mask):limit=min(limit,degree-graph[site].bit_count())
        for first,second in combinations(sites(mask),2):limit=min(limit,3-(graph[first]&graph[second]).bit_count())
        for rank in range(limit):
            var=form.new();slots.append(mask);copy.append(var)
            if rank:form.add(-var,var-1)
    form.cardinality(copy,pop,pop)
    for site,word in enumerate(graph):
        number=degree-word.bit_count();form.cardinality([var for var,mask in zip(copy,slots) if mask>>site&1],number,number)
    for first,second in combinations(range(width),2):
        if graph[first]>>second&1:continue
        used=(graph[first]&graph[second]).bit_count();form.cardinality([var for var,mask in zip(copy,slots) if mask>>first&1 and mask>>second&1],max(0,1-used),(1 if (first,second)==(1,2) else 3)-used)
    allowed=[[] for _ in slots];required=[[] for _ in slots];edges={}
    for first,second in combinations(range(len(slots)),2):
        lhs,rhs=slots[first],slots[second];share=lhs&rhs;forced=bool(avoid[full^(lhs|rhs)])
        if share.bit_count()>3 or (share and forced):form.add(-copy[first],-copy[second]);continue
        if share:continue
        if edge_mode==2:
            edge=form.new();edges[first,second]=edge;form.add(-edge,copy[first]);form.add(-edge,copy[second]);
            if forced:form.add(-copy[first],-copy[second],edge)
            allowed[first].append(edge);allowed[second].append(edge)
        elif edge_mode==1:
            allowed[first].append(copy[second]);allowed[second].append(copy[first]);
            if forced:required[first].append(copy[second]);required[second].append(copy[first])
    if edge_mode:
        for pos,mask in enumerate(slots):
            need=degree-mask.bit_count();start=len(form.clauses);form.cardinality(allowed[pos],need,need if edge_mode==2 else len(allowed[pos]));form.cardinality(required[pos],0,need)
            for row in form.clauses[start:]:row.append(-copy[pos])
    return form,slots,copy,edges


def cal():
    count=0
    for rec in map(json.loads,(DEST/'wing-cal.jsonl').read_text().splitlines()):
        if count>=25:break
        rows=rec['rows'];truth=Counter((mask<<3)|1 for mask in rec['y']);truth.update(mask<<3 for mask in rec['z']);_,_,masks,_=system(rows,22,'basic');scope=set(truth)|set(masks[::7]);
        for mode in (0,1,2):
            form,slots,copy,edges=encode(rows,scope,6,22,mode);used=Counter();pins=[]
            for mask,var in zip(slots,copy):used[mask]+=1;pins.append(var if used[mask]<=truth[mask] else -var)
            assert all(used[mask]>=qty for mask,qty in truth.items());engine=Cadical195(bootstrap_with=form.clauses);assert engine.solve(assumptions=pins);pins[0]*=-1;assert not engine.solve(assumptions=pins);engine.delete()
        count+=1
    print('PASS planted unlabelled-mask, edge-support and exact degree-edge selectors / mutants',3*count)


def run(rec,mode,cap):
    start=process_time();rows=rec['rows'];_,_,allmasks,_=system(rows,40,'basic');masks=[allmasks[idx] for idx in restrict(allmasks,rows)];form,slots,copy,edges=encode(rows,masks,9,40,mode);engine=Cadical195(bootstrap_with=form.clauses);engine.conf_budget(cap);ans=engine.solve_limited();out=dict(id=rec['id'],mode=mode,status=str(ans),count=len(slots),edges=len(edges),clauses=len(form.clauses),vars=form.nvars,conflicts=engine.accum_stats()['conflicts'],cpu=process_time()-start)
    if ans:
        model=set(engine.get_model());out['selected']=[word for word,var in zip(slots,copy) if var in model]
    engine.delete()
    if ans is False:form.write(DEST/f"plateau-slots-{rec['id']}-{mode}.cnf")
    return out


if __name__=='__main__':
    if sys.argv[1]=='cal':cal()
    else:
        mode,cap,shard,mod=map(int,sys.argv[1:5]);records=[row for row in map(json.loads,(DEST/'plat.jsonl').read_text().splitlines()) if row['status']=='fractional']
        for rec in records[shard::mod]:print(json.dumps(run(rec,mode,cap),separators=(',',':')),flush=True)
