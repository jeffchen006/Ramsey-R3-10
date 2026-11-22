"""Audit odd-cycle-space obstruction packings on original, ungauged sign variables."""

from argparse import ArgumentParser
from collections import Counter
from itertools import combinations,product
from pathlib import Path
from cyclic_check import read_base
from relift_audit import explicit_lift,pairs,independent,walk_score


def eliminate(form,basis):
    for pivot in sorted(basis,reverse=True):
        if form&(1<<pivot):form^=basis[pivot]
    return form


AFFINE=1<<200


def verify(text,order,tokens,conditions=()):
    graph=read_base(text);size=len(graph);edges={}
    for right in range(size):
        for left in range(right):
            if graph[left][right]==1:edges[left,right]=1<<len(edges)
    triangle={}
    for triple in combinations(range(size),3):
        terms=list(combinations(triple,2))
        if all(edge in edges for edge in terms):
            form=eliminate(sum(edges[edge] for edge in terms),triangle)
            if form:triangle[form.bit_length()-1]=form
    for linear,constant in conditions:
        assert 0<linear<1<<len(edges) and constant in (0,1)
        form=eliminate(linear^(AFFINE*constant),triangle);variables=form&~AFFINE;assert variables
        triangle[variables.bit_length()-1]=form
    capacities={};forms={};spent=Counter();total=0
    def interpret(support):
        if support in capacities:return
        full,single=map(int,support.split(','));assert support==f'{full},{single}' and 0<=(full|single)<1<<size and not(full&single) and 2*full.bit_count()+single.bit_count()==order
        active=[vertex for vertex in range(size) if single&(1<<vertex)]
        for left in range(size):
            if full&(1<<left):assert all(graph[left][right]==0 for right in range(size) if (full|single)&(1<<right))
        assert all(graph[left][right]!=2 for left,right in combinations(active,2))
        potential={};components=0
        for root in active:
            if root in potential:continue
            components+=1;potential[root]=0;todo=[root]
            for left in todo:
                for right in active:
                    edge=tuple(sorted((left,right)))
                    if right not in potential and edge in edges:
                        potential[right]=potential[left]^edges[edge];todo.append(right)
        cycles={eliminate(potential[left]^potential[right]^edges[left,right],triangle) for left,right in combinations(active,2) if (left,right) in edges}-{0}
        assert len(cycles)<=1 and AFFINE not in cycles
        capacities[support]=1<<components;forms[support]=next(iter(cycles),0)
    for token in tokens:
        header,*supports=token.split(':');amount=int(header[1:]);assert amount>0 and supports and len(set(supports))==len(supports)
        parity=0
        for support in supports:
            interpret(support);spent[support]+=amount;assert spent[support]<=capacities[support];parity^=forms[support]
        if header.startswith('U'):assert len(supports)==1 and parity==0
        else:assert header.startswith('C') and all(forms[support]!=0 for support in supports) and parity==(0 if len(supports)%2 else AFFINE)
        total+=amount
    return total


def check(source,order,prefix,oracle=False):
    rows=Path(source).read_text().splitlines();certs=Path(prefix+'.odd').read_text().splitlines();logs=Path(prefix+'.out').read_text().splitlines();assert len(rows)==len(logs)==len(certs)
    totals=[];distinct=0
    for index,(text,cert,log) in enumerate(zip(rows,certs,logs)):
        ident,*tokens=cert.split();num,bound,baseline,packs,_=map(int,log.split());assert int(ident)==num==index
        assert verify(text,order,tokens)==bound and sum(token[0]=='C' for token in tokens)==packs and sum(int(token.split(':')[0][1:]) for token in tokens if token[0]=='U')==baseline
        if oracle:
            matrix=read_base(text);singles=sum(left!=right and matrix[left][right]==1 for left,right in pairs(len(matrix)));minimum=1<<60
            for signs in product(range(2),repeat=singles):
                graph=explicit_lift(matrix,iter(signs))
                if all(independent(row,graph) for row in graph):minimum=min(minimum,walk_score(graph,order))
            assert minimum>=(bound) and minimum<1<<60;distinct+=minimum==bound
        totals.append(bound)
    print(prefix,'rows',len(rows),'positive',sum(bool(value) for value in totals),'at least 25',sum(value>=25 for value in totals),'min',min(totals),'oracle exact',distinct if oracle else '-',flush=True)


if __name__=='__main__':
    parser=ArgumentParser(description=__doc__);parser.add_argument('source');parser.add_argument('order',type=int);parser.add_argument('prefix');parser.add_argument('--oracle',action='store_true');args=parser.parse_args();assert __debug__;check(args.source,args.order,args.prefix,args.oracle)
