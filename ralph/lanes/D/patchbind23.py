from itertools import combinations
from kernel_cnf import Cnf,neg
from book_controls import sites

def build(wing,side,selected,pinned,words,qedges,degree,target,clean=(),variable_residual=None):
    span=len(selected);outer=len(words);hub=span+outer;fixed={};blocks=range(span,hub);known={site:idx for idx,site in enumerate(pinned)};width=len(wing)
    for pos,site in enumerate(selected):
        fixed[pos,hub]=False
        for prior in range(pos):fixed[prior,pos]=bool(wing[site]>>selected[prior]&1)
        if site in known:
            for idx,word in enumerate(words):fixed[pos,span+idx]=bool(word>>known[site]&1)
    for lhs,rhs in combinations(range(outer),2):
        if words[lhs]&words[rhs]:fixed[span+lhs,span+rhs]=False
    form=Cnf(hub+1,fixed);leaks=[];low=2 if target else 1;protected=set(clean) if target else set();frame=set(selected);full=len(selected)==width;posof={site:pos for pos,site in enumerate(selected)}
    def cap_low(terms,lower,guard=False,soft=False):
        if lower<=0:return
        outs=form.thresholds(terms,lower);flag=form.new() if soft else False;form.add(guard,flag,outs[lower-1]);
        if soft:
            leaks.append(flag)
            if lower>1:form.add(guard,outs[lower-2])
    form.cardinality([form.edge(hub,point) for point in blocks],degree-2,degree-2)
    if qedges is not None:form.cardinality([form.edge(lhs,rhs) for lhs,rhs in combinations(blocks,2)],qedges,qedges)
    for lhs,rhs,third in combinations(range(hub+1),3):form.add(neg(form.edge(lhs,rhs)),neg(form.edge(lhs,third)),neg(form.edge(rhs,third)))
    def shared(lhs,rhs,points):return [form.conjunction(form.edge(lhs,point),form.edge(rhs,point)) for point in points if point not in (lhs,rhs)]
    for pos,site in enumerate(selected):
        residual=degree-1-wing[site].bit_count();form.cardinality([form.edge(pos,point) for point in blocks],*(variable_residual or {}).get(site,(residual,residual)))
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

