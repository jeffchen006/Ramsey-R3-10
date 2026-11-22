"""Labelled graph-only CNF, with optional exceptional codegree-one pair budget."""

import argparse
from itertools import combinations
from pathlib import Path

from kernel_cnf import Cnf, neg
from path_growth import bits, fixed_graph, read_profiles


def build(graph, frozen, degree, cap, mincode, exceptions=0):
    order=len(graph)
    fixed={}
    for first, second in combinations(range(order),2):
        if first in frozen or second in frozen:
            fixed[first,second]=bool(graph[first]>>second&1)
        elif graph[first]&graph[second]:
            fixed[first,second]=False
    form=Cnf(order,fixed)
    for point in range(order):
        form.cardinality([form.edge(point,second) for second in range(order) if point!=second],degree,degree)
    defects=[]
    for first,second in combinations(range(order),2):
        edge=form.edge(first,second)
        common=[form.conjunction(form.edge(point,first),form.edge(point,second)) for point in range(order) if point not in (first,second)]
        for witness in common:
            form.add(neg(edge),neg(witness))
        thresholds=form.thresholds(common,cap+1)
        form.add(neg(thresholds[cap]))
        if exceptions:
            weak=form.conjunction(neg(edge),neg(thresholds[mincode-1]));defects.append(weak)
            form.add(edge,thresholds[0])
        else:
            form.add(edge,thresholds[mincode-1])
    if exceptions:
        form.cardinality(defects,0,exceptions)
    return form


def small():
    from pysat.solvers import Solver
    for order,degree,mincode,high,graph in [(13,4,1,2,[sum(1<<((point+step)%13) for step in (1,-1,5,-5)) for point in range(13)]),(16,5,2,3,[sum(1<<(point^step) for step in (1,2,4,8,15)) for point in range(16)])]:
        frozen=set(range(0,order,3)); masks=[row if point in frozen else sum(1<<anchor for anchor in frozen if row>>anchor&1) for point,row in enumerate(graph)]
        form=build(masks,frozen,degree,high,mincode)
        full=[form.edge(first,second,False)*(1 if graph[first]>>second&1 else -1) for first,second in combinations(range(order),2)]
        with Solver(name='cadical195',bootstrap_with=form.clauses) as solver:assert solver.solve(assumptions=full)
        form=build(masks,frozen,degree,high,mincode+1)
        with Solver(name='cadical195',bootstrap_with=form.clauses) as solver:assert not solver.solve(assumptions=full)
        print('PASS labelled SAT truth at order',order,'; strict minimum rejects planting')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--source',type=Path);parser.add_argument('--index',type=int);parser.add_argument('--out',type=Path);parser.add_argument('--exceptions',type=int,default=0);args=parser.parse_args()
    if args.source:
        graph=fixed_graph(next(row for i,row in enumerate(read_profiles(args.source)) if i==args.index)); form=build(graph,set(range(8)),9,3,2,args.exceptions);form.write(args.out)
    else:small()
