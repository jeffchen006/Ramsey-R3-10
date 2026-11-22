"""Calibrate the new, independently constructed row-CNF on real C22 marks."""

from collections import Counter,defaultdict
from pysat.solvers import Cadical195
from graft_audit import both_sides,initial,star_formula
from joint_deck import marks


def calibration():
    records=list(marks())
    library=[]
    for profile,_,_,_ in records:
        if profile not in library:
            library.append(profile)
        flipped = Counter({sum(1<<pos for pos,old in enumerate((4,6,5,7,0,2,1,3)) if mask >> old & 1):size for mask,size in profile.items()})
        if flipped not in library:
            library.append(flipped)
    checks=0
    for profile,_,planted,width in records:
        if width != 4:
            continue
        graph=initial(profile)
        marked=set(range(8))
        cores=list(both_sides(graph))
        for pivot in range(8,22):
            actual={vertex for vertex in range(22) if planted[pivot]>>vertex & 1}
            canonical=actual & marked
            cells=defaultdict(list)
            for vertex in sorted(set(range(22))-marked-{pivot}):
                cells[tuple(sorted(graph[vertex]))].append(vertex)
            for group in cells.values():
                canonical.update(group[:len(actual & set(group))])
            formula=star_formula(graph,marked,pivot,library,cores,6)
            with Cadical195(bootstrap_with=formula.clauses) as solver:
                assert solver.solve(assumptions=[(vertex+1)*(1 if vertex in canonical else -1) for vertex in range(22)])
            checks+=1
    assert checks==672
    print('PASS independent audit formula, 672/672 actual canonical C22 rows across all 48 marks')


if __name__=='__main__':
    calibration()
