"""Fixed signing: necessary one-pole mask cover and physical nonadjacent-pair test."""
from itertools import combinations,combinations_with_replacement
from pathlib import Path
import sys
from pysat.solvers import Minisat22
from cyclic_proof import proof
from orbit_extend import independent_sets,parse_graph6,ROOT,to_graph6

def maskbits(mask):return [vertex for vertex in range(mask.bit_length()) if mask>>vertex&1]

def case(tag,index):
    sign,text=Path(tag+'.signs').read_text().splitlines()[index].split();graph=parse_graph6(text);n=len(graph);target=4 if tag=='plainpos' else 5 if tag=='fixedpos' else 10
    return int(sign),graph,n,target

def attach(graph,neighborhoods,outer_edges=()):
    size=len(graph);result=graph[:]+[0]*len(neighborhoods)
    for serial,neighbors in enumerate(neighborhoods):
        extra=size+serial;result[extra]=neighbors
        for old in maskbits(neighbors):
            result[old]|=1<<extra
            if neighbors>>(old^1)&1:result[old]&=~(1<<(old^1))
    for first,second in outer_edges:result[size+first]|=1<<(size+second);result[size+second]|=1<<(size+first)
    return result

def barriers(graph,target):
    size=len(graph);all_old=(1<<size)-1
    conflicts=[[-first-1,-second-1] for first,second in combinations(range(size),2) if second!=(first^1) and graph[first]>>second&1]
    sets=sorted(independent_sets(graph,all_old,target-1));return conflicts+[[vertex+1 for vertex in maskbits(mask)] for mask in sets]

def block(size,neighbors):return [-vertex-1 if neighbors>>vertex&1 else vertex+1 for vertex in range(size)]

def write_cnf(stem,size,clauses):
    stem.with_suffix('.cnf').write_text(f'p cnf {size} {len(clauses)}\n'+''.join(' '.join(map(str,(*clause,0)))+'\n' for clause in clauses))

def run(tag,index):
    sign,graph,size,target=case(tag,index);stem=Path(f'{tag}-s{index}');clauses=barriers(graph,target);masks=[]
    with Minisat22(bootstrap_with=clauses) as solver:
        while solver.solve():
            positive=solver.get_model();neighbors=sum(1<<(literal-1) for literal in positive if literal>0);masks.append(neighbors)
            if len(masks)>2000:print(tag,index,'contact_cap',len(masks));return
            solver.add_clause(block(size,neighbors))
    masks.sort();stem.with_suffix('.masks').write_text(''.join(f'{mask}\n' for mask in masks))
    write_cnf(stem,size,clauses+[block(size,mask) for mask in masks]);assert proof(stem)=='dual'
    good=0;tested=0
    with stem.with_suffix('.pairs').open('w') as out:
        for first,second in combinations_with_replacement(masks,2):
            full=attach(graph,(first,second));witness=next(independent_sets(full,(1<<(size+2))-1,target),0)
            print(first,second,witness,file=out);good+=not witness;tested+=1
            if tested==100000:print(tag,index,'pair_cap',len(masks));return
    status='closed' if not good else 'open';stem.with_suffix('.result').write_text(f'{tag} {index} {sign} {status} {len(masks)} {tested} {good}\n');print(stem.with_suffix('.result').read_text(),end='',flush=True)

if __name__=='__main__':run(sys.argv[1],int(sys.argv[2]))
