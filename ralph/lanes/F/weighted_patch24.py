from itertools import combinations
from pathlib import Path
import json,sys
from pysat.solvers import Minisat22
from paid_patch24 import raw,clause,instance
from cyclic_proof import proof
from exception_cover import verify_lrat
from cards24 import DIR

def fixed_clauses(size,features,minimum):
    rows=[];flags=[]
    for idx,(kind,points,weight) in enumerate(features):
        assert weight>0 and len(set(points))==len(points) and all(0<=vertex<size for vertex in points)
        if kind=='degree':assert len(points)==1;flags.append(points[0]+1)
        else:
            assert kind=='miss' and len(points) in (7,8);flags.append(size+idx+1);rows.append([vertex+1 for vertex in points]+[flags[-1]])
    for width in range(1,len(flags)+1):
        for chosen in combinations(range(len(flags)),width):
            total=sum(features[idx][2] for idx in chosen)
            if total>=minimum and all(total-features[idx][2]<minimum for idx in chosen):rows.append([-flags[idx] for idx in chosen])
    return rows
def replay(name):
    item=json.loads(Path(name+'.weighted').read_text());present={tuple(pair) for pair in item['present']};absent={tuple(pair) for pair in item['absent']};assert not present&absent and all(0<=left<right<32 for left,right in present|absent);features=item['features'];minimum=item['minimum'];assert minimum>0;cost=0;rows=fixed_clauses(32,features,minimum)
    for kind,points,weight in features:
        if kind=='degree':cap=9-sum(points[0] in pair for pair in present);assert cap>=0
        else:assert set(combinations(points,2))<=absent;cap=2 if len(points)==8 else 5
        cost+=cap*weight
    for kind,points in item['terms']:
        if kind=='iset':assert len(set(points))==9 and set(combinations(points,2))<=absent
        elif kind=='edge':assert tuple(points) in present
        else:assert kind=='full' and len(points)==1 and sum(points[0] in pair for pair in present)>=9
        rows.append(clause(kind,points))
    assert cost==item['cost'] and 0<minimum and cost<8*minimum;cnf=f'p cnf {32+len(features)} {len(rows)}\n'+''.join(' '.join(map(str,row))+' 0\n' for row in rows);return cnf,cost//minimum,len(present),len(absent)
def create(name):
    adj,_=instance(name);dual=json.loads((DIR.parent/'capacity'/(name+'.dual')).read_text());features=[(kind,[point for point in range(32) if word>>point&1],weight) for kind,word,weight in dual['rows']];assert len(features)<=10;minimum=dual['min'];base=fixed_clauses(32,features,minimum);terms=raw(adj,10);offset=32+len(features)+1
    def select(terms):
        guarded=base+[clause(kind,points)+[-offset-index] for index,(kind,points) in enumerate(terms)];
        with Minisat22(bootstrap_with=guarded) as solver:
            if solver.solve(assumptions=list(range(offset,offset+len(terms)))):return None
            keep=set(solver.get_core());
            for selector in sorted(keep.copy()):
                if selector in keep and not solver.solve(assumptions=sorted(keep-{selector})):keep&=set(solver.get_core())
            return [terms[idx-offset] for idx in sorted(keep)]
    used=select(terms)
    if used is None:used=select(terms+[('full',[vertex]) for vertex in range(32) if adj[vertex].bit_count()==9])
    assert used is not None;present=set();absent=set();stars=set()
    for kind,points,wt in features:
        if kind=='degree':stars.update(points)
        else:absent.update(combinations(points,2))
    for kind,points in used:
        if kind=='edge':present.add(tuple(points))
        elif kind=='iset':absent.update(combinations(points,2))
        else:stars.update(points)
    for vertex in stars:
        for old in range(32):
            if adj[vertex]>>old&1:present.add(tuple(sorted((old,vertex))))
    assert not present&absent and all(adj[left]>>right&1 for left,right in present) and all(not adj[left]>>right&1 for left,right in absent);Path(name+'.weighted').write_text(json.dumps(dict(features=features,minimum=minimum,cost=dual['cost'],terms=used,present=sorted(present),absent=sorted(absent))));cnf,*_=replay(name);Path(name+'.cnf').write_text(cnf);assert proof(Path(name))=='dual'
def main(name):
    cnf,bound,yes,no=replay(name);assert cnf==Path(name+'.cnf').read_text();verify_lrat(Path(name));print(name,'weighted physical patch: outside <=',bound,'required edges',yes,'required nonedges',no,'free old pairs',496-yes-no,flush=True)
if __name__=='__main__':
    for name in sys.argv[2:]:
        if sys.argv[1]=='create':create(name)
        main(name)
