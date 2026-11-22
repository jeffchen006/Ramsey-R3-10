"""All signing variables, all allowed verticals, unrestricted exterior vertices."""
from collections import deque
from itertools import combinations, islice
from pathlib import Path
import gzip
import json
import subprocess
import sys
from pysat.solvers import Cadical195
from cyclic_proof import proof
from exception_sign import matrix,parameters
from orbit_extend import ROOT,independent_sets,parse_graph6,to_graph6

def problem(tag):
    if tag.startswith('control'):
        sites=[1,3,4,2]; mat=[[int((a+a)%13 in (1,5,8,12)) if a==b else sum((dest-a)%13 in (1,5,8,12) for dest in (b,-b)) for b in sites] for a in sites]
        return mat,4 if tag=='controlneg' else 5
    size,edges,occ,full,target=parameters(tag);return matrix(size,edges,occ,full),target

def labels(mat,extra):
    size=len(mat);order=2*size+extra; variables={}; physical={}; forest=[]; components=[{site} for site in range(size)]
    def symbol(key):
        if key not in variables:variables[key]=1+len(variables)
        return variables[key]
    for left,right in combinations(range(order),2):
        src,dest=left//2,right//2
        if right>=2*size:literal=symbol(('p',left,right))
        elif src==dest:literal=symbol(('v',src)) if mat[src][src] else False
        elif mat[src][dest]==1:
            literal=symbol(('s',src,dest))*(1 if (left^right)&1 else -1)
            if components[src] is not components[dest]:
                united=components[src]|components[dest];forest.append(-abs(literal))
                for site in united:components[site]=united
        else:literal=bool(mat[src][dest])
        physical[left,right]=literal
    return order,physical,forest

def clause(physical,group,positive):
    literals=set()
    for pair in combinations(group,2):
        literal=physical[pair]
        if type(literal) is bool:
            if literal==positive:return None
        else:
            signed=literal if positive else -literal
            if -signed in literals:return None
            literals.add(signed)
    return tuple(sorted(literals,key=abs))

def mate(mask,core):
    low=((1<<(2*core))-1)//3
    return ((mask&low)<<1)|((mask>>1)&low)|(mask&~((1<<(2*core))-1))

def vertices(mask):return tuple(bit for bit in range(mask.bit_length()) if mask>>bit&1)

def run(tag,extra,limit):
    mat,target=problem(tag);core=len(mat); order,physical,forest=labels(mat,extra);universe=(1<<order)-1
    clauses=[(literal,) for literal in forest]; seen=set(); receipts=[]
    for group in combinations(range(order),3):
        item=clause(physical,group,False)
        if item is not None and item not in seen:seen.add(item);clauses.append(item)
    stem=Path(f'{tag}-p{extra}'); count=max(abs(symbol) for symbol in physical.values() if type(symbol) is int)
    def witness(mask):
        group=vertices(mask);assert len(group)==target
        item=clause(physical,group,True)
        if item is not None and item not in seen:seen.add(item);clauses.append(item);receipts.append(mask)
    if tag[0].isdigit():
        startgraph=parse_graph6(Path('../'+tag+'.g6').read_text().strip());allcore=(1<<(2*core))-1
        for sub in independent_sets(startgraph,allcore,target-1):
            for pole in range(2*core,order):witness(sub|(1<<pole))
    with Cadical195(bootstrap_with=clauses) as solver:
        for iteration in range(limit):
            solver.conf_budget(100000);status=solver.solve_limited()
            if status is None:outcome='conflict_cap';break
            if not status:
                outcome='unsigned_proof'; break
            model=set(solver.get_model() or []);graph=[0]*order
            for (left,right),literal in physical.items():
                present=literal if type(literal) is bool else literal in model
                if present:graph[left]|=1<<right;graph[right]|=1<<left
            assert not any(graph[left]&graph[right] for left,right in physical if graph[left]>>right&1)
            before=len(clauses)
            for ns in range(1<<extra):
                selected=[2*core+idx for idx in range(extra) if ns>>idx&1]
                if len(selected)>target:continue
                if any(graph[a]>>b&1 for a,b in combinations(selected,2)):continue
                allowed=(1<<(2*core))-1
                for vertex in selected:allowed&=~graph[vertex]
                for sub in islice(independent_sets(graph,allowed,target-len(selected)),120):
                    mask=sub|(ns<<(2*core));witness(mask);witness(mate(mask,core))
            if before==len(clauses):
                stem.with_suffix('.g6').write_text(to_graph6(graph)+'\n')
                args=[sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',stem.with_suffix('.g6'),str(order),str(target)]
                result=subprocess.run(args,capture_output=True,text=True,check=True);assert json.loads(result.stdout)['graphs'][0]['ok'];stem.with_suffix('.gate').write_text(result.stdout)
                outcome='card';break
            for item in clauses[before:]:solver.add_clause(item)
        else:outcome='iteration_cap'
    if outcome=='unsigned_proof':
        stem.with_suffix('.deck').write_text(''.join(str(mask)+'\n' for mask in receipts))
        if () in clauses:
            count+=1; clauses=[item for item in clauses if item]+[(count,),(-count,)]
        stem.with_suffix('.cnf').write_text(f'p cnf {count} {len(clauses)}\n'+''.join(' '.join(map(str,(*item,0)))+'\n' for item in clauses))
        outcome=proof(stem)
    stats=(tag,extra,outcome,iteration,len(receipts),len(clauses));stem.with_suffix('.status').write_text(' '.join(map(str,stats))+'\n');print(*stats,flush=True)

if __name__=='__main__':run(sys.argv[1],int(sys.argv[2]),int(sys.argv[3]))
