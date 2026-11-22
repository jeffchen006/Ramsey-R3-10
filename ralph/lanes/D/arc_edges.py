"""Physical Q edges and partial/full wing-to-Q edges conditioned on six consecutive columns."""
from itertools import combinations
from time import process_time
import json,sys
from pysat.solvers import Cadical195
from equal_roles import DEST
from kernel_cnf import Cnf,ROOT,neg
from book_controls import bitset,sites,flags,book,graph_masks,reorder


def build(wing,side,selected,pinned,words,qedges,degree,target):
    span=len(selected);outer=len(words);hub=span+outer;fixed={};blocks=range(span,hub);known={site:idx for idx,site in enumerate(pinned)};width=len(wing)
    for pos,site in enumerate(selected):
        fixed[pos,hub]=False
        for prior in range(pos):fixed[prior,pos]=bool(wing[site]>>selected[prior]&1)
        if site in known:
            for idx,word in enumerate(words):fixed[pos,span+idx]=bool(word>>known[site]&1)
    for lhs,rhs in combinations(range(outer),2):
        if words[lhs]&words[rhs]:fixed[span+lhs,span+rhs]=False
    form=Cnf(hub+1,fixed);leaks=[];low=2 if target else 1;protected=set(selected[:8]) if target else set();frame=set(selected);full=len(selected)==width;posof={site:pos for pos,site in enumerate(selected)}
    def cap_low(terms,lower,guard=False,soft=False):
        if lower<=0:return
        outs=form.thresholds(terms,lower);flag=form.new() if soft else False;form.add(guard,flag,outs[lower-1]);
        if soft:
            leaks.append(flag)
            if lower>1:form.add(guard,outs[lower-2])
    form.cardinality([form.edge(hub,point) for point in blocks],degree-2,degree-2)
    form.cardinality([form.edge(lhs,rhs) for lhs,rhs in combinations(blocks,2)],qedges,qedges)
    for lhs,rhs,third in combinations(range(hub+1),3):form.add(neg(form.edge(lhs,rhs)),neg(form.edge(lhs,third)),neg(form.edge(rhs,third)))
    def shared(lhs,rhs,points):return [form.conjunction(form.edge(lhs,point),form.edge(rhs,point)) for point in points if point not in (lhs,rhs)]
    for pos,site in enumerate(selected):
        residual=degree-1-wing[site].bit_count();form.cardinality([form.edge(pos,point) for point in blocks],residual,residual)
        form.cardinality(shared(pos,hub,blocks),low-1,2)
        for prev,other in enumerate(selected[:pos]):
            if wing[site]>>other&1:continue
            used=(wing[site]&wing[other]).bit_count()+int(side[site]==side[other]);terms=shared(pos,prev,blocks);form.cardinality(terms,0,3-used);cap_low(terms,low-used,soft=target and not({site,other}&protected))
    for point in blocks:
        y=form.edge(hub,point);around=[form.edge(point,other) for other in blocks if point!=other];form.cardinality(around+[neg(y)],degree-5,degree+1-2*low);terms=shared(hub,point,blocks);form.cardinality(terms,0,3);cap_low(terms,low,y)
        for shore in (0,1):
            terms=[y,*[form.edge(pos,point) for pos,site in enumerate(selected) if side[site]==shore]];form.cardinality(terms,low if full else 0,3)
        if full:form.cardinality([y,*around,*[form.edge(pos,point) for pos in range(span)]],degree,degree)
        for pos,site in enumerate(selected):
            neighbors=set(sites(wing[site]));missing=len(neighbors-frame);terms=shared(pos,point,blocks)+[form.edge(posof[other],point) for other in sorted(neighbors&frame)];form.cardinality(terms,0,3);cap_low(terms,low-missing,form.edge(pos,point),target and site not in protected)
    for lhs,rhs in combinations(blocks,2):
        terms=shared(lhs,rhs,range(hub+1));form.cardinality(terms,0,3)
        if full:cap_low(terms,low,form.edge(lhs,rhs),target)
    if target:form.cardinality(leaks,0,1)
    return form


def calibration():
    count=0
    for text in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=graph_masks(text)
        if {word.bit_count() for word in graph}!={6} or max((one&two).bit_count() for one,two in combinations(graph,2))>3:continue
        for ends in flags(graph):
            frame,(left,right)=book(graph,ends);wing=left+right;outer=sorted(set(range(22))-set(frame+wing));pinned=[0,5,1,6,2,7];words=[bitset(idx for idx,site in enumerate(pinned) if graph[point]>>wing[site]&1) for point in outer];edges=sum(word.bit_count() for word in reorder(graph,outer))//2
            for selected in ([3,*pinned,8],list(range(10))):
                form=build(reorder(graph,wing),[0]*5+[1]*5,selected,pinned,words,edges,6,False);truth=reorder(graph,[wing[idx] for idx in selected]+outer+[frame[0]]);sat=Cadical195(bootstrap_with=form.clauses);pins=[form.edge(lhs,rhs,False)*(1 if truth[lhs]>>rhs&1 else -1) for lhs,rhs in combinations(range(len(truth)),2)];assert sat.solve(assumptions=pins);sat.delete();count+=1
            if count==30:print('PASS 30 planted full/partial C22 Q matrices, including both unseen flank contacts');return


def profiles():
    all_rows=[]
    for idx,line in enumerate((DEST/'p6.in').read_text().splitlines()):
        words=tuple(map(int,line.split()));clean=True
        for lhs,rhs in combinations(range(6),2):
            dist=rhs-lhs
            if dist==1:continue
            common=int(not(dist%2))+int(dist==2)+sum(word>>lhs&word>>rhs&1 for word in words);clean&=common>=2
        if not clean:continue
        flip=sorted(bitset(5-site for site in sites(word)) for word in words)
        if tuple(flip)<words:continue
        all_rows.append((idx,words))
    return all_rows


def make(words,span):
    wing=[(1<<((site+1)%16))|(1<<((site-1)%16)) for site in range(16)];return build(wing,[site%2 for site in range(16)],list(range(span)),list(range(1,7)),words,43,9,True)


def run(idx,words,span,cap):
    start=process_time();form=make(words,span);sat=Cadical195(bootstrap_with=form.clauses);sat.conf_budget(cap);result=sat.solve_limited();out=dict(id=idx,span=span,status=str(result),conf=sat.accum_stats()['conflicts'],cpu=process_time()-start);sat.delete()
    if result is False:form.write(DEST/f'arc-{idx}-{span}.cnf')
    return out


if __name__=='__main__':
    if sys.argv[1]=='cal':calibration()
    else:
        span,cap,shard,mod=map(int,sys.argv[1:5]);rows=profiles();selected=rows[shard::mod] if len(sys.argv)==5 else [rows[idx] for idx in map(int,sys.argv[5:])]
        for idx,words in selected:print(json.dumps(run(idx,words,span,cap)),flush=True)
