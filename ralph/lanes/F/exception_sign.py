"""Signed 36-card separation; no rotations of a marked support are inferred."""
from itertools import combinations, islice
from pathlib import Path
import json
import subprocess
import sys
import time

from pysat.solvers import Minisat22
from cyclic_proof import Formula, proof
from cyclic_check import check
from one_double_pilot import ROOT, to_graph6, tri_free
from orbit_extend import independent_sets
from relift_audit import encode


def matrix(size, edges, occupied, doubled):
    assert doubled & occupied == doubled and occupied < 1 << size
    mat = [[0]*(size+1) for _ in range(size+1)]
    for left, right in edges:
        mat[left][right] = mat[right][left] = 1
        assert not ((doubled>>left & occupied>>right | doubled>>right & occupied>>left) & 1)
    for site in range(size):
        mat[site][site] = 1-(doubled>>site & 1)
        mat[site][size] = mat[size][site] = (occupied>>site & 1) + (doubled>>site & 1)
    mat[size][size] = int(not doubled)
    return mat


def parameters(tag):
    if tag == 'neg': return 4, list(combinations(range(4),2)), 1, 1, 5
    if tag == 'pos': return 3, [(0,1)], 6, 6, 5
    if tag == 'plainpos':return 3,[(0,1),(1,2)],5,0,4
    if tag == 'plainneg':return 3,list(combinations(range(3),2)),0,0,4
    occupied,doubled = map(int,tag.split('_'))
    return 17, [(left,right) for left,right in combinations(range(17),2) if 6<=right-left<=12], occupied,doubled,10


def run(tag, limit=400):
    size,edges,occupied,doubled,target = parameters(tag)
    stem = Path(tag); sizebit = 1<<size
    text = encode(matrix(size,edges,occupied,doubled)); form = Formula(text,target)
    stem.with_suffix('.q').write_text(text+'\n')
    outside = [site for site in range(size) if not occupied>>site&1]
    initial = sorted((len(form.cycles((size,),sites)),sites) for sites in combinations(outside,target-2))[:12] if doubled else []
    for _,sites in initial: form.add((size,),sites)
    assert all(not occupied&sum(1<<site for site in sites) for _,sites in initial)
    physical = (1<<(2*size+2))-1
    started = time.monotonic()
    with Minisat22(bootstrap_with=form.clauses) as solver:
        for iteration in range(limit):
            solver.conf_budget(100000); result=solver.solve_limited()
            if result is False:
                form.serialize(stem); status=proof(stem); assert status=='dual',status
                assert check(text,target,stem)==len(form.supports)
                status='cert'; break
            if result is None: status='conflict_cap';break
            graph=form.lift(solver.get_model());assert tri_free(graph)
            support=set()
            for pad in ((3<<(2*size),0) if doubled else (0,)):
                allowed=physical if not pad else physical&~(pad|graph[-1]|graph[-2])
                count=target-pad.bit_count()
                for mask in islice(independent_sets(graph,allowed,count),80):
                    mask|=pad
                    full=tuple(site for site in range(size+1) if (mask>>(2*site)&3)==3)
                    single=tuple(site for site in range(size+1) if (mask>>(2*site)&3) in (1,2))
                    assert (full,single) not in form.supports
                    support.add((full,single))
            if not support:
                stem.with_suffix('.g6').write_text(to_graph6(graph)+'\n')
                proc=subprocess.run([sys.executable,'-I',ROOT/'.hmz/flows/r310_ralph/gate.py',ROOT,'check',stem.with_suffix('.g6'),str(2*size+2),str(target)],capture_output=True,text=True,check=True)
                assert json.loads(proc.stdout)['graphs'][0]['ok'];stem.with_suffix('.gate').write_text(proc.stdout)
                status='card';break
            start=len(form.clauses)
            for full,single in sorted(support,key=lambda pair:(len(form.cycles(*pair)),pair))[:12]:form.add(full,single)
            for clause in form.clauses[start:]:solver.add_clause(clause)
        else:status='iteration_cap'
    stats=(tag,status,iteration,len(form.supports),sum(size in full for full,single in form.supports),len(form.clauses),round(time.monotonic()-started,3))
    stem.with_suffix('.status').write_text(' '.join(map(str,stats))+'\n');print(*stats,flush=True)


if __name__=='__main__':run(sys.argv[1])
