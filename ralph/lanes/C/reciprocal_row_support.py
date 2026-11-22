import argparse
from collections import Counter
from itertools import combinations, islice
from pathlib import Path
from time import process_time

from pysat.solvers import Cadical195

from reciprocal_audit import SOURCE22, decode, host_masks, merge, vertices
from reciprocal_census import PILOTS
from reciprocal_census_proofs import HEADER
from reciprocal_proof_r11 import proof


def base(lower, left, right, degree, cap):
    split = left+right
    assert all(row.bit_count() == degree for row in lower[split:])
    variables = {(src,dst): 1+src*right+dst-left for src in range(left) for dst in range(left,split)}
    clauses = []
    envelope = list(lower)
    for (src,dst), var in variables.items():
        if lower[src] & lower[dst]:
            clauses.append((-var,))
        else:
            envelope[src] |= 1 << dst
            envelope[dst] |= 1 << src
    for root in range(split):
        opposing = ((1 << split)-(1 << left)) if root < left else (1 << left)-1
        candidates = envelope[root] & opposing
        deficit = degree-lower[root].bit_count()
        neighbors = {vertex: variables[min(vertex,root),max(vertex,root)] for vertex in vertices(candidates)}
        fixed = tuple(lower[vertex] for vertex in range(split,len(lower)))
        hits = tuple(lower[vertex] & candidates for vertex in range(split,len(lower))
                     if not (lower[vertex] >> root & 1 or lower[root] & lower[vertex]))
        selectors = []
        if deficit >= 0:
            for selected in combinations(neighbors,deficit):
                mask = sum(1 << vertex for vertex in selected)
                if any(mask & lower[vertex] for vertex in selected) or any(not (mask & hit) for hit in hits):
                    continue
                if any(((lower[root]|mask) & row).bit_count() > cap for row in fixed):
                    continue
                selector = len(variables)+1
                variables[('row',root,mask)] = selector
                selectors.append((selector,mask))
                for vertex,var in neighbors.items():
                    clauses.append((-selector,var if mask >> vertex & 1 else -var))
        clauses.append(tuple(selector for selector,_ in selectors))
        for vertex,var in neighbors.items():
            for present in (False,True):
                clauses.append(((-var if present else var),*(selector for selector,mask in selectors
                                 if (mask >> vertex & 1) == present)))
    return variables,clauses


def cutsets(graph, lower_left, lower_right, degree, variables):
    left = (1 << lower_left)-1
    right = (1 << (lower_left+lower_right))-1-left

    def find(picked, available, needed):
        if not needed:
            yield picked
            return
        while available.bit_count() >= needed:
            bit = available & -available
            available ^= bit
            yield from find(picked|bit,available & ~graph[bit.bit_length()-1],needed-1)

    for picked in find(0,(1 << len(graph))-1,degree+1):
        yield tuple(variables[src,dst] for src in vertices(picked&left) for dst in vertices(picked&right))


def formula(lower, left, right, degree, thin=False, control_pins=False):
    assert not thin
    variables,clauses = base(lower,left,right,degree,6 if control_pins else 5)
    if () in clauses:
        return variables,clauses
    edge_vars = [(source,dest,var) for key,var in variables.items()
                 if len(key) == 2 for source,dest in (key,)]
    additions = set()
    with Cadical195(bootstrap_with=clauses) as solver:
        for _ in range(128):
            if not solver.solve():
                return variables,clauses+sorted(additions)
            model = set(solver.get_model())
            proposed = list(lower)
            for src,dst,var in edge_vars:
                if var in model:
                    proposed[src] |= 1 << dst
                    proposed[dst] |= 1 << src
            cuts = set(islice(cutsets(proposed,left,right,degree,variables),16))
            if not cuts:
                assert control_pins, ('completion candidate for independent checking',proposed)
                return variables,clauses+sorted(additions)+[(lit,) for lit in sorted(model)]
            assert not cuts & additions
            additions |= cuts
            for clause in sorted(cuts):
                solver.add_clause(clause)
    raise RuntimeError('128-model support CNF generation limit; no verdict')


def calibrate():
    left,right = ([host_masks(decode(row)) for row in Path(f'cal-{n}.g6').read_text().splitlines()] for n in (10,11))
    folder = Path('proof-support-cal')
    folder.mkdir(exist_ok=True)
    controls = [tuple(map(int,row.split())) for row in Path('cal-planted.tsv').read_text().splitlines()]
    for control in (0,95,175,394):
        key = controls[control]
        proof(f'control-{control}',key,6,left[key[0]],right[key[5]],2,True,folder,False,build=formula)
    checked = 0
    for key in controls:
        lower,ll,rr = merge(left[key[0]],right[key[5]],key,2)
        variables,clauses = formula(lower,ll,rr,6,control_pins=True)
        with Cadical195(bootstrap_with=clauses) as solver:
            assert solver.solve()
            model = set(solver.get_model())
            assert all(any(literal in model for literal in clause) for clause in clauses)
        checked += 1
    assert checked == 395
    print('395 smaller planted positives retain SAT models; four also pass the standalone model checker')


def replay(quartile):
    lo,hi = PILOTS[quartile]
    shard = Path(f'{lo:07d}-{hi:07d}')
    left,right = ([host_masks(decode(row)) for row in path.read_text().splitlines()]
                  for path in (SOURCE22,shard/'hosts.g6'))
    output = Path(f'proof-stage-{quartile}')
    folder = output/'support'
    folder.mkdir(exist_ok=True)
    counts = Counter()
    started = process_time()
    with (folder/'receipts.tsv').open('w') as log:
        print(HEADER,file=log)
        for row in (output/'queue.tsv').read_text().splitlines():
            label,*fields = row.split()
            key = tuple(map(int,fields))
            assert lo <= key[5] < hi
            receipt = proof(label,key,9,left[key[0]],right[key[5]-lo],3,False,folder,False,build=formula)
            print(*receipt,sep='\t',file=log,flush=True)
            counts[receipt[1]] += 1
    print(dict(counts), 'driver CPU seconds',round(process_time()-started,6))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode',choices=['cal','replay'])
    parser.add_argument('quartile',type=int,nargs='?')
    args = parser.parse_args()
    calibrate() if args.mode == 'cal' else replay(args.quartile)
