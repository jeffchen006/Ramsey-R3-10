from itertools import combinations,islice,product
from pathlib import Path
import sys
from pysat.solvers import Minisat22
from cyclic_proof import Formula
from exception_sign import parameters,matrix
from orbit_extend import to_graph6,independent_sets
from relift_audit import encode

def count(tag,limit):
    if tag=='core34':
        target=10; board=[[int(left==right or 6<=abs(left-right)<=12) for right in range(17)] for left in range(17)]
    else:
        size,edges,occupied,doubled,target=parameters(tag);assert not doubled;board=matrix(size,edges,occupied,doubled)
    formula=Formula(encode(board),target);stop='iteration_cap';signings=set()
    with Minisat22(bootstrap_with=formula.clauses) as engine,open(tag+'.signs','w') as listing:
        for iteration in range(15000):
            engine.conf_budget(150000);status=engine.solve_limited()
            if status is None:stop='conflict_cap';break
            if not status:stop='complete';break
            model=engine.get_model();graph=formula.lift(model)
            pool=set(islice(formula.subsets(graph),80))
            if pool:
                before=len(formula.clauses)
                for support in sorted(pool,key=lambda item:(len(formula.cycles(*item)),item))[:10]:formula.add(*support)
                assert before<len(formula.clauses)
                for item in formula.clauses[before:]:engine.add_clause(item)
            else:
                positive=set(model);signs=sum(1<<(symbol-1) for symbol in formula.ident.values() if symbol in positive)
                assert signs not in signings;signings.add(signs);print(signs,to_graph6(graph),file=listing,flush=True)
                engine.add_clause([-symbol if symbol in positive else symbol for symbol in formula.ident.values()])
                if len(signings)>=limit:stop='model_cap';break
    if tag=='plainpos':
        reference=set()
        for values in product((False,True),repeat=len(formula.ident)):
            positive={index+1 for index,flag in enumerate(values) if flag}
            if any(int(entry.split()[1]) in positive for entry in formula.trace if entry.startswith('forest ')):continue
            graph=formula.lift(positive)
            if any(graph[left]&graph[right] for left,right in combinations(range(len(graph)),2) if graph[left]>>right&1):continue
            if next(independent_sets(graph,(1<<len(graph))-1,target),None) is None:reference.add(sum(1<<(item-1) for item in positive))
        assert stop=='complete' and signings==reference
    formula.serialize(Path(tag));print(tag,stop,'signings',len(signings),'iterations',iteration,'supports',len(formula.supports),flush=True)

if __name__=='__main__':count(sys.argv[1],int(sys.argv[2]))
