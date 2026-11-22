"""Counterexample search for two disjoint matched books, only on edges of their two rectangles."""
from collections import Counter
from itertools import combinations,product
from pathlib import Path
from time import process_time
import argparse
import json
from pysat.solvers import Cadical195

from book_controls import bitset,book,sites
from book_seedpack import upper
from book_packing import subsets
from kernel_cnf import Cnf,neg


def isets(graph,order,limit):
    def visit(chosen,live,need):
        if need==1:
            for point in sites(live):yield chosen|1<<point
            return
        while live.bit_count()>=need:
            site=live&-live;live^=site;point=site.bit_length()-1
            yield from visit(chosen|site,live&~graph[point],need-1)
    yield from visit(0,(1<<order)-1,limit)


class Countermodel:
    def __init__(self,frame,quota,kind='general',extra=None):
        self.frame=frame;fixed,*rows=frame;self.degree=degree=rows[0].bit_count();self.size=order=len(rows);self.quota=quota
        may=upper(frame);base_rows=rows
        if extra:
            rows=extra['lo'];may=[word&~forbidden for word,forbidden in zip(may,extra['ban'])]
        form=self.form=Cnf(order,{(left,right):bool(rows[left]>>right&1) for left,right in combinations(range(order),2) if rows[left]>>right&1 or not(may[left]>>right&1)})
        self.books=[book(base_rows,ends) for ends in ((0,1),(2,3))];marked=bitset(point for path,_ in self.books for point in path);assert marked.bit_count()==6
        self.pools=[bitset((*left,*right))&~marked for _,(left,right) in self.books];self.shared=self.pools[0]&self.pools[1]
        links=[0]*order;optional=set();self.tables=[]
        for _,(left,right) in self.books:
            table=[]
            for first,second in product(left,right):
                edge=form.edge(first,second)
                if edge is False:continue
                table.append((first,second,edge))
                if type(edge)is int:
                    links[first]|=1<<second;links[second]|=1<<first;optional.add(tuple(sorted((first,second))))
            self.tables.append(table)
        self.optional=sorted(optional);self.counts=Counter();blank=[may[point]&~links[point] for point in range(order)]
        for selection in isets(blank,order,degree+1):
            form.add(*(form.edge(a,b) for a,b in combinations(sites(selection),2) if links[a]>>b&1));self.counts['I']+=1
        for point in range(order):
            lits=[form.edge(point,other) for other in sites(links[point])];base=rows[point].bit_count();unrepresented=(may[point]&~(rows[point]|links[point])).bit_count();form.cardinality(lits,max(0,degree-base-unrepresented),degree-base)
        for lhs,rhs in combinations(range(order),2):
            edge=form.edge(lhs,rhs);potential=may[lhs]&may[rhs];common=[];unrepresented=0
            for other in sites(potential):
                literals=[form.edge(lhs,other),form.edge(rhs,other)]
                if (type(literals[0])is int and not links[lhs]>>other&1) or (type(literals[1])is int and not links[rhs]>>other&1):unrepresented+=1;continue
                both=form.conjunction(*literals);common.append(both)
                if edge is True or (type(edge)is int and links[lhs]>>rhs&1):form.add(neg(edge),neg(both))
            low=1 if kind=='general' or (lhs,rhs) in ((0,1),(2,3)) else 2
            cap=1 if (lhs,rhs) in ((0,1),(2,3)) else 3
            form.cardinality(common,max(0,low-unrepresented) if edge is False else 0,cap)
        self.base=len(form.clauses)

    def matching(self,table,pool,positive):
        adj={}
        for first,second,edge in table:
            if pool>>first&1 and pool>>second&1 and (edge is True or edge in positive):adj.setdefault(first,[]).append(second)
        owner={}
        def aug(first,seen):
            for second in adj[first]:
                if second in seen:continue
                seen.add(second)
                if second not in owner or aug(owner[second],seen):owner[second]=first;return True
            return False
        for first in adj:
            if aug(first,set()) and len(owner)>=self.quota:return True
        return False

    def partitions(self,positive):
        for choice in subsets(self.shared):
            left=self.pools[0]&~(self.shared^choice);right=self.pools[1]&~choice
            if self.matching(self.tables[0],left,positive) and self.matching(self.tables[1],right,positive):yield choice

    def block(self,choice):
        form=self.form;guard=form.new();before=len(form.clauses)
        for side,(pool,flag) in enumerate(((self.pools[0]&~(self.shared^choice),guard),(self.pools[1]&~choice,-guard))):
            select={point:form.new() for point in sites(pool)};form.cardinality(list(select.values()),0,self.quota-1)
            for first,second,edge in self.tables[side]:
                if first in select and second in select:form.add(-flag,neg(edge),select[first],select[second])
        return form.clauses[before:]

    def solve(self,cap,batch,truth=None):
        start=process_time();form=self.form;solver=Cadical195(bootstrap_with=form.clauses);seen=set();rounds=0;status='cap';ans={}
        if truth is not None:
            for pair in self.optional:
                left,right=pair;form.add(form.edge(*pair) if truth[left]>>right&1 else neg(form.edge(*pair)));solver.add_clause(form.clauses[-1])
        while (available:=cap-solver.accum_stats()['conflicts'])>0:
            rounds+=1;solver.conf_budget(available);res=solver.solve_limited()
            if res is None:break
            if not res:status='forces';break
            positive={lit for lit in solver.get_model() if lit>0};added=0
            for choice in self.partitions(positive):
                assert choice not in seen;seen.add(choice);added+=1
                for clause in self.block(choice):solver.add_clause(clause)
                if added>=batch:break
            if not added:
                status='counterdiagram';ans.update(edges=[pair for pair in self.optional if form.edge(*pair)in positive]);break
        ans.update(status=status,rounds=rounds,splits=sorted(seen),conflicts=solver.accum_stats()['conflicts'],solve_cpu=process_time()-start,clauses=len(form.clauses),base=form.nvars,independent=self.counts['I']);solver.delete();return ans


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('input',type=Path);parser.add_argument('quota',type=int);parser.add_argument('--batch',type=int,default=6);parser.add_argument('--cap',type=int,default=4000);parser.add_argument('--kind',default='general');parser.add_argument('--limit',type=int,default=0);parser.add_argument('--cnf',type=Path);args=parser.parse_args()
    for idx,(key,frame,truth) in enumerate(map(json.loads,args.input.read_text().splitlines())):
        if args.limit and idx>=args.limit:break
        start=process_time();system=Countermodel(frame,args.quota,args.kind);answer=system.solve(args.cap,args.batch,truth);answer.update(id=key,totalcpu=process_time()-start)
        if args.cnf and answer['status']=='forces':system.form.write(args.cnf/('r'+str(key)+'.cnf'))
        print(json.dumps(answer,separators=(',',':')),flush=True)
