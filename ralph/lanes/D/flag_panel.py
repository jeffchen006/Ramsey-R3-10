"""Labelled edge-only SAT projection against all frozen endpoint neighborhoods."""
from itertools import combinations
from pathlib import Path
import sys
from kernel_cnf import Cnf


def build(text,order,degree):
    fixed,*data=map(int,text.split());graph=data[:order];defect=data[order:];assert len(defect)==order
    pins={}
    for left,right in combinations(range(order),2):
        if fixed & (1<<left|1<<right):pins[left,right]=bool(graph[left]>>right&1)
        elif graph[left]&graph[right]&fixed:pins[left,right]=False
    form=Cnf(order,pins)
    for point in range(order):
        form.cardinality([form.edge(point,other) for other in range(order) if other!=point],degree,degree)
        for anchor,star in enumerate(graph):
            if point==anchor or not fixed>>anchor&1 or star>>point&1:continue
            weak=bool(defect[point]>>anchor&1)
            form.cardinality([form.edge(point,other) for other in range(order) if star>>other&1],1 if weak else 2,1 if weak else 3)
    return form


def control(folder):
    from pysat.solvers import Solver
    for name,degree in [('c5',2),('cleb',5),('c22',6)]:
        rows=(folder/(name+'.in')).read_text().splitlines();graph=list(map(int,rows[-1].split()[1:]));order=len(graph)
        low=[sum(1<<other for other in range(order) if (graph[other]&row).bit_count()==1) for row in graph]
        for text in rows:
            form=build(text+' '+' '.join(map(str,low)),order,degree)
            assumptions=[form.edge(left,right,False)*(1 if graph[left]>>right&1 else -1) for left,right in combinations(range(order),2)]
            with Solver(name='cadical195',bootstrap_with=form.clauses)as sat:assert sat.solve(assumptions=assumptions)
        if any(low):
            form=build(rows[-1]+' '+' '.join(['0']*order),order,degree)
            with Solver(name='cadical195',bootstrap_with=form.clauses)as sat:assert not sat.solve()
        print(name,'planted frames accepted',len(rows),'adverse exact relation rejected' if any(low) else 'no defects')


if __name__=='__main__':
    folder=Path(sys.argv[1]);control(folder);target=folder/'panels';target.mkdir(exist_ok=True)
    for idx,text in enumerate((folder/'nonstar.in').read_text().splitlines()):build(text,40,9).write(target/f'{idx}.cnf')
