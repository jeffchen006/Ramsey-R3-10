"""Edge projection on the exterior after fixing C6 contacts and all seven hub neighbors."""
from itertools import combinations
from time import process_time
import json,sys
from pysat.solvers import Cadical195
from book_controls import graph_masks,book,flags,reorder,bitset,sites
from book_strata import independent_sets
from hex_fibers import DEST,masks
from kernel_cnf import ROOT,Cnf,neg


def make(wing,words,shores,seven,degree,count,low,debit,strong=True):
    size=len(words);dim=len(wing);seven=set(seven);pairs=list(combinations(range(size),2));fixed={(left,right):False for left,right in pairs if words[left]&words[right] or left in seven and right in seven};form=Cnf(size,fixed);deficits=[]
    edges=[form.edge(left,right) for left,right in pairs];form.cardinality(edges,count,count)
    for point in range(size):
        around=[form.edge(point,other) for other in range(size) if other!=point];centre=int(point in seven);form.cardinality(around,degree-6+centre,degree-2*low+centre)
        if not centre:form.cardinality([form.edge(point,other) for other in seven],low,3)
        for site,hood in enumerate(wing):
            if words[point]>>site&1:continue
            used=(hood&words[point]).bit_count();pool=[form.edge(point,other) for other in range(size) if point!=other and words[other]>>site&1];form.cardinality(pool,1-used,3-used)
            if low==2 and used<2:
                miss=form.new();form.cardinality(pool+[miss],2-used,len(pool)+1);deficits.append(miss)
    if low==2:form.cardinality(deficits,0,debit)
    for left,right in pairs:
        edge=form.edge(left,right);shared=[]
        for other in range(size):
            if other==left or other==right:continue
            pair=(form.edge(left,other),form.edge(right,other));form.add(neg(edge),neg(pair[0]),neg(pair[1]));shared.append(form.conjunction(*pair))
        used=(words[left]&words[right]).bit_count()+int(left in seven and right in seven);form.cardinality(shared,0,3-used)
    if strong:
        core=3+dim;boundary=[0]*core
        def inside(left,right):boundary[left]|=1<<right;boundary[right]|=1<<left
        inside(0,1);inside(0,2)
        for idx,word in enumerate(wing):
            inside(shores[idx],3+idx)
            for other in sites(word):
                if other<idx:inside(3+other,3+idx)
        contacts=[(word<<3)|int(idx in seven) for idx,word in enumerate(words)];limits={}
        for seed in independent_sets(boundary):
            blind=tuple(idx for idx,term in enumerate(contacts) if not term&seed);bound=degree-seed.bit_count();limits[blind]=min(limits.get(blind,degree),bound)
        form.seeds=sorted(limits.items(),key=lambda rule:(rule[1],rule[0]));form.seed_clauses=[]
    return form


def forbidden(form,truth):
    found=set()
    for blind,bound in form.seeds:
        if len(blind)<=bound:continue
        def search(pool,word,need):
            if need<=0:return word
            while pool.bit_count()>=need:
                spot=pool&-pool;pool^=spot;point=spot.bit_length()-1;out=search(pool&~truth[point],word|spot,need-1)
                if out:return out
        bad=search(bitset(blind),0,bound+1)
        if bad:found.add(bad)
    return sorted(found)


def calibration():
    total=0;positive=0
    for text in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=graph_masks(text)
        if {word.bit_count() for word in graph}!={6} or max((left&right).bit_count() for left,right in combinations(graph,2))>3:continue
        for ends in flags(graph):
            (hub,*_),(left,right)=book(graph,ends);wing=left+right;outer=sorted(set(range(22))-set(wing)-set(ends)-{hub});rows=reorder(graph,wing);words=[bitset(idx for idx,slot in enumerate(wing) if graph[point]>>slot&1) for point in outer];seven=[idx for idx,slot in enumerate(outer) if graph[hub]>>slot&1];truth=reorder(graph,outer);edges=sum(word.bit_count() for word in truth)//2;form=make(rows,words,[1]*5+[2]*5,seven,6,edges,1,0);assert not forbidden(form,truth);sat=Cadical195(bootstrap_with=form.clauses);pins=[form.edge(lhs,rhs,simplify=False)*(1 if truth[lhs]>>rhs&1 else -1) for lhs,rhs in combinations(range(len(outer)),2)];assert sat.solve(assumptions=pins);sat.delete();total+=1
            if total==1:
                sat=Cadical195(bootstrap_with=form.clauses);pins[0]*=-1;assert not sat.solve(assumptions=pins);sat.delete();positive+=1
    print('PASS all C22 labelled projected Q graphs including conditioned degree/cap/independent rows',total,'wrong edge rejected',positive)


def encode(idx):
    record=json.loads((DEST/'hex-seven.jsonl').read_text().splitlines()[idx]);rows=[(1<<((site+1)%6))|(1<<((site-1)%6)) for site in range(6)];return make(rows,masks(),[1,2]*3,record['seven'],9,43,2,1)


def solve(idx,cap,rounds):
    start=process_time();form=encode(idx);sat=Cadical195(bootstrap_with=form.clauses);result=None;generated=[];iterations=0;truth=None
    for iteration in range(rounds):
        iterations+=1;sat.conf_budget(max(1,cap-sat.accum_stats()['conflicts']));result=sat.solve_limited()
        if not result:break
        positive=set(sat.get_model());truth=[bitset(other for other in range(21) if other!=point and form.edge(point,other,simplify=False) in positive) for point in range(21)];cuts=forbidden(form,truth)
        if not cuts:break
        result=None;truth=None
        for mask in cuts:
            clause=[form.edge(left,right) for left,right in combinations(sites(mask),2) if form.edge(left,right) is not False];form.add(*clause);sat.add_clause(clause);generated.append(mask)
        if sat.accum_stats()['conflicts']>=cap:break
    out=dict(id=idx,status=str(result),conf=sat.accum_stats()['conflicts'],cuts=generated,iterations=iterations,cpu=process_time()-start);sat.delete()
    if result is False:form.write(DEST/f'hex-edge-{idx}.cnf')
    if result is True:out['Q']=truth
    return out


if __name__=='__main__':
    if sys.argv[1]=='cal':calibration()
    else:
        cap,rounds=map(int,sys.argv[1:3]);ids=list(map(int,sys.argv[3:]))
        for idx in ids:print(json.dumps(solve(idx,cap,rounds)),flush=True)
