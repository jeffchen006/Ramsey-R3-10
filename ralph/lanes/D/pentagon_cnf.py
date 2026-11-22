"""Certify five-star obstructions with ordinary graph clauses and sparse ten-sets."""
from itertools import combinations
from pathlib import Path
import sys
from kernel_cnf import Cnf,neg


def form_for(frame,degree,limit):
    fixed,*graph=map(int,frame.split());order=len(graph);pins={};room=[0]*order;must=[0]*order
    for left,right in combinations(range(order),2):
        if fixed&(1<<left|1<<right):pins[left,right]=bool(graph[left]>>right&1)
        elif graph[left]&graph[right]&fixed:pins[left,right]=False
        value=pins.get((left,right));
        if value is not False:room[left]|=1<<right;room[right]|=1<<left
        if value is True:must[left]|=1<<right;must[right]|=1<<left
    form=Cnf(order,pins)
    for point in range(order):form.cardinality([form.edge(point,other) for other in range(order) if other!=point],degree,degree)
    for left,right in combinations(range(order),2):
        edge=form.edge(left,right);common=[form.conjunction(form.edge(left,other),form.edge(right,other)) for other in range(order) if other not in (left,right)]
        for site in common:form.add(neg(edge),neg(site))
        bounds=form.thresholds(common,4);form.add(edge,bounds[0]);form.add(neg(bounds[3]))
    short=[0]*(limit+1)
    def gen(chosen,available,spare):
        need=degree+1-len(chosen)
        if not need:
            short[limit-spare]+=1;form.add(*(form.edge(left,right) for left,right in combinations(chosen,2)));return
        while available.bit_count()>=need:
            site=available&-available;available^=site;point=site.bit_length()-1
            extra=sum((room[point]>>other)&1 for other in chosen)
            if extra>spare:continue
            later=available&~must[point]
            if extra==spare:
                for vertex in [*chosen,point]:later&=~room[vertex]
            gen([*chosen,point],later,spare-extra)
    gen([],(1<<order)-1,limit)
    return form,short


if __name__=='__main__':
    directory=Path(sys.argv[1]);degree=int(sys.argv[2]);idx=int(sys.argv[3]);limit=int(sys.argv[4]);name=f'{degree}-{idx}-{limit}';order=40 if degree==9 else 22
    formula,short=form_for((directory/f'c{order}.in').read_text().splitlines()[idx],degree,limit);formula.write(directory/(name+'.cnf'));print(name,short,formula.nvars,len(formula.clauses))
