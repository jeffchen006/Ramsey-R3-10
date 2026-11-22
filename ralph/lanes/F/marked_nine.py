"""Extract a local nine-site transversal identity without any exterior or exceptional vertex."""
from functools import reduce
from itertools import combinations
from pathlib import Path
import sys

from column_audit import insert,normal
from cyclic_check import check
from cyclic_proof import Formula, proof
from orbit_extend import vertices
from relift_audit import encode


def rows(size,allowed,triangles):
    edges={edge:2<<idx for idx,edge in enumerate(combinations(range(size),2)) if 6<=abs(edge[0]-edge[1])<=12}
    basis={}
    if triangles:
        for triple in combinations(range(size),3):
            sides=list(combinations(triple,2))
            if all(edge in edges for edge in sides):insert(basis,sum(edges[edge] for edge in sides))
    cycles={}
    for mask in allowed:
        lift={}
        for left,right in combinations(vertices(mask),2):
            if (left,right) in edges:insert(lift,(1<<(256+left))^(1<<(256+right))^edges[left,right])
        cycles[mask]=[row for pivot,row in lift.items() if pivot<1<<256]
    return basis,cycles


def refutes(basis,cycles,masks):
    space=basis.copy(); used=[]
    for _ in range(len(masks)+1):
        length=len(space)
        for mask in masks:
            reduced={}
            for form in cycles[mask]:insert(reduced,normal(space,form))
            if not reduced:return used+[mask]
            if len(reduced)==1 and 1 not in reduced:
                insert(space,next(iter(reduced.values()))^1);used.append(mask)
        if len(space)==length:break
    return []


def extract():
    supports=[int(row.split()[3]) for row in Path('pilot0.trace').read_text().splitlines() if row.startswith('0_0 step 1 ')]
    assert len(supports)==21 and all(mask.bit_count()==9 and mask<1<<14 for mask in supports)
    for size,triangles in ((14,False),(14,True),(17,True)):
        basis,cycles=rows(size,supports,triangles);used=refutes(basis,cycles,supports)
        if not used:continue
        masks=list(dict.fromkeys(used))
        for mask in reversed(masks.copy()):
            trial=[other for other in masks if other!=mask]
            if refutes(basis,cycles,trial):masks=trial
        print('localized',size,'triangles needed in this run',triangles,'masks',masks,'union',list(vertices(reduce(int.__or__,masks))),'cycle ranks',[len(cycles[mask]) for mask in masks]);break
    else:raise AssertionError('no local implication')
    Path('local9.txt').write_text(' '.join(map(str,[size,int(triangles),*masks]))+'\n')


def certificate():
    size,triangles,*masks=(14,1,4351,8447,16322)
    if Path('local9.txt').exists():assert list(map(int,Path('local9.txt').read_text().split()))==[size,triangles,*masks]
    basis,cycles=rows(size,masks,triangles);assert refutes(basis,cycles,masks)
    text=encode([[int(left==right or 6<=abs(left-right)<=12) for right in range(size)] for left in range(size)]);formula=Formula(text,9)
    for mask in masks:formula.add((),tuple(vertices(mask)))
    stem=Path('marked9');formula.serialize(stem);assert proof(stem)=='dual' and check(text,9,stem)==len(masks)
    print('physical CNF and dual LRAT',size,len(masks),formula.variables,len(formula.clauses),'triangle-free premise in certificate')


if __name__=='__main__':{'extract':extract,'cert':certificate}[sys.argv[1]]()
