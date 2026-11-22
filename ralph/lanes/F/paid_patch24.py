from itertools import combinations
from pathlib import Path
from random import Random
import json,sys
from pysat.solvers import Minisat22
from capacity24 import instance,verify_lrat,proof
from cards24 import gate,independent_sets,to_graph6,parse_graph6

def raw(adj,target):
    return [('edge',[left,right]) for left,right in combinations(range(len(adj)),2) if adj[left]>>right&1]+[('iset',[vertex for vertex in range(len(adj)) if witness>>vertex&1]) for witness in independent_sets(adj,(1<<len(adj))-1,target-1)]
def clause(kind,points):return [point+1 if kind=='iset' else -point-1 for point in points]
def clauses(adj,terms,paid):return [[-vertex-1] for vertex in paid]+[clause(kind,points) for kind,points in terms]
def cnf(adj,terms,paid):
    rows=clauses(adj,terms,paid);return f'p cnf {len(adj)} {len(rows)}\n'+''.join(' '.join(map(str,row))+' 0\n' for row in rows)
def bounds(adj,target,paid,terms):
    size=len(adj);present=set();absent=set();degrees=set(paid)
    for kind,points in terms:
        assert points==sorted(set(points)) and 0<=min(points)<=max(points)<size
        if kind=='edge':assert len(points)==2 and adj[points[0]]>>points[1]&1;present.add(tuple(points))
        elif kind=='iset':assert len(points)==target-1 and all(not adj[left]>>right&1 for left,right in combinations(points,2));absent.update(combinations(points,2))
        else:assert kind=='full' and len(points)==1 and adj[points[0]].bit_count()==target-1;degrees.update(points)
    for vertex in degrees:
        for old in range(size):
            if adj[vertex]>>old&1:present.add(tuple(sorted((vertex,old))))
    assert not present&absent;return present,absent,sum(target-1-adj[vertex].bit_count() for vertex in paid)
def check(tag):
    if tag=='small':adj,target=[0,0],3
    else:adj,target=instance(tag)
    data=json.loads(Path(tag+'.patch').read_text());paid=data['paid'];terms=data['terms'];present,absent,upper=bounds(adj,target,paid,terms);assert upper==data['maximum_outside'] and list(map(list,sorted(present)))==data['present'] and list(map(list,sorted(absent)))==data['absent'];assert cnf(adj,terms,paid)==Path(tag+'.cnf').read_text();verify_lrat(Path(tag));return adj,target,present,absent,upper
def create(tag,paid):
    if tag=='small':adj,target=[0,0],3
    else:adj,target=instance(tag)
    size=len(adj);terms=raw(adj,target)
    with Minisat22(bootstrap_with=clauses(adj,terms,paid)) as plain:needsfull=plain.solve()
    if needsfull:terms += [('full',[vertex]) for vertex in range(size) if adj[vertex].bit_count()==target-1]
    units=[-vertex-1 for vertex in paid];gated=[[literal] for literal in units]+[clause(kind,points)+[-size-1-index] for index,(kind,points) in enumerate(terms)]
    with Minisat22(bootstrap_with=gated) as solver:
        enabled=[size+1+idx for idx in range(len(terms))];assert not solver.solve(assumptions=enabled);keep=set(solver.get_core());
        for selector in sorted(keep.copy()):
            if selector in keep and not solver.solve(assumptions=sorted(keep-{selector})):keep &=set(solver.get_core())
    used=[terms[selector-size-1] for selector in sorted(keep)];present,absent,upper=bounds(adj,target,paid,used);record=dict(paid=paid,terms=used,present=sorted(present),absent=sorted(absent),maximum_outside=upper);Path(tag+'.patch').write_text(json.dumps(record));Path(tag+'.cnf').write_text(cnf(adj,used,paid));assert proof(Path(tag))=='dual';check(tag);print(tag,'paid',paid,'remaining outside <=',upper,'scoped old present',len(present),'absent',len(absent),'unrestricted pairs',size*(size-1)//2-len(present)-len(absent),'SAT terms',len(used),flush=True)
    if tag=='small':
        with Minisat22(bootstrap_with=clauses([2,1],raw([2,1],3),paid)) as positive:assert positive.solve()
        return
    random=Random(240032+int(tag));choices=list(combinations(range(size),2));best=-1;extremes=None
    for draw in range(8):
        lower=adj.copy();higher=adj.copy();random.shuffle(choices)
        for left,right in choices:
            pair=(left,right)
            if adj[left]>>right&1:
                if pair in present:continue
                lower[left]^=1<<right;lower[right]^=1<<left
                if next(independent_sets(lower,(1<<size)-1,target),None) is not None:lower[left]^=1<<right;lower[right]^=1<<left
            elif pair not in absent and not higher[left]&higher[right] and higher[left].bit_count()<target-1 and higher[right].bit_count()<target-1:higher[left]|=1<<right;higher[right]|=1<<left
        width=sum((old^new).bit_count() for old,new in zip(lower,higher))//2
        if width>best:best=width;extremes=lower,higher
    lower,higher=extremes;assert all(not low&~high for low,high in zip(lower,higher)) and all(lower[left]>>right&1 for left,right in present) and all(not higher[left]>>right&1 for left,right in absent);gate(lower,target,Path(tag+'.low.g6'));gate(higher,target,Path(tag+'.high.g6'));print(tag,'fully strict monotone old-card cube width',best,'labelled cards',1<<best,'both endpoints gated, all share checked patch',flush=True)
if __name__=='__main__':
    if sys.argv[1]=='create':
        for tag in sys.argv[2:]:create(tag,{'small':[0,1],'391':[7,20,27],'128':[15,22,25,31]}[tag])
    else:
        for tag in sys.argv[2:]:print(tag,'rebound',check(tag)[-1])
