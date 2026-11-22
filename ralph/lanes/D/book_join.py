"""Exact finite joined-book relaxation. SAT means a partial interface, not a graph."""
from collections import Counter
from itertools import combinations, product
from functools import lru_cache
from pathlib import Path
from time import process_time
import argparse
import hashlib
import json

from book_controls import bitset, book, sites, squares
from kernel_cnf import Cnf, neg, ROOT
from pysat.solvers import Cadical195


def matrix_images(key):
    for swap, flip, reverse in product(range(2),repeat=3):
        rows=[0]*5
        for left,row in enumerate(key):
            for right in sites(row):
                first,second=(right,left) if swap else (left,right)
                rows[-first%5 if flip else first] |= 1<<(-second%5 if reverse else second)
        yield sum(mask<<(5*idx) for idx,mask in enumerate(rows))


@lru_cache(None)
def allowed(kind):
    folder=ROOT/'scratch/D/flag12';blocked=set()
    if kind in ('two','square'):
        blocked.update(row['index'] for row in map(json.loads,(folder/'margins.jsonl').read_text().splitlines()) if row['status']=='excluded')
    if kind=='square':
        blocked.update(row['index'] for row in (json.loads(line) for line in (folder/'square-full.jsonl').read_text().splitlines() if line.startswith('{')) if row['status']=='exact-separation')
    result=set()
    for idx,line in enumerate((folder/'interfaces.tsv').read_text().splitlines()):
        *key,size,occupied=map(int,line.split())
        if idx in blocked or (kind=='c22' and not occupied):continue
        images=set(matrix_images(key));assert len(images)==size;result.update(images)
    return result


@lru_cache(None)
def bitcolumns(kind):
    words=sorted(allowed(kind));size=(len(words)+7)//8;packed=[bytearray(size) for _ in range(25)]
    for idx,word in enumerate(words):
        for point in sites(word):packed[point][idx//8] |= 1<<(idx%8)
    return (1<<len(words))-1,[int.from_bytes(row,'little') for row in packed]


@lru_cache(20000)
def explain(kind,word):
    universe,columns=bitcolumns(kind);values=[columns[idx] if word>>idx&1 else universe^columns[idx] for idx in range(25)]
    suffix=[universe]*26
    for idx in reversed(range(25)):suffix[idx]=suffix[idx+1]&values[idx]
    assert not suffix[0];keep=[];prefix=universe
    for idx,cell in enumerate(values):
        if prefix&suffix[idx+1]:keep.append(idx);prefix &= cell
    assert not prefix
    return keep


def same_line(frame):
    return hashlib.sha256(' '.join(map(str,frame)).encode()).hexdigest()


class System:
    def __init__(self,frame,mode,kind,design=0,truth=None,quota=None):
        self.fixed,*self.rows=frame;rows=self.rows;fixed=self.fixed;order=len(rows);degree=rows[0].bit_count()
        self.order=order; self.degree=degree; self.kind=kind; self.mode=mode
        pins={}
        for left,right in combinations(range(order),2):
            if fixed&(1<<left|1<<right):pins[left,right]=bool(rows[left]>>right&1)
            elif rows[left]&rows[right]&fixed:pins[left,right]=False
        self.cnf=form=Cnf(order,pins);self.books=[];self.edge_groups=[];self.selection={};self.tables=[]
        for side,ends in enumerate(((0,1),(2,3))):
            path,(leftwing,rightwing)=book(rows,ends)
            self.books.append((path,leftwing,rightwing));edges={}
            for first,second in product(leftwing,rightwing):
                variable=form.edge(first,second)
                if variable is False:continue
                pick=form.new();form.add(-pick,variable);edges[first,second]=pick
            self.edge_groups.append(edges)
            if mode=='one':form.cardinality(list(edges.values()),1,1)
            else:
                for left in leftwing:form.cardinality([pick for (first,_),pick in edges.items() if first==left],1,1)
                for right in rightwing:form.cardinality([pick for (_,second),pick in edges.items() if second==right],1,1)
            self.tables.append([(edge,pick,(path[0],path[1],*edge,path[2]),bitset((*path,*edge))) for edge,pick in edges.items()])
        self.interfaces=[]
        for edge0,pick0,cycle0,mask0 in self.tables[0]:
            for edge1,pick1,cycle1,mask1 in self.tables[1]:
                if mask0&mask1:
                    if mode=='one':form.add(-pick0,-pick1)
                    continue
                self.interfaces.append((pick0,pick1,edge0,edge1,cycle0,cycle1))
        self.bouquets=[]
        if mode=='allpack':
            if quota is None:quota=4 if order==40 else 2
            core=bitset(site for path,_,_ in self.books for site in path);loads=[[] for _ in range(order)]
            for table in self.edge_groups:
                group={}
                for first,second in table:
                    if core&(1<<first|1<<second):continue
                    variable=form.new();form.add(-variable,form.edge(first,second));group[first,second]=variable;loads[first].append(variable);loads[second].append(variable)
                form.cardinality(list(group.values()),quota,quota);self.bouquets.append(group)
            for load in loads:form.cardinality(load,0,1)
        if design:self.design(design,truth)

    def design(self,level,truth):
        form=self.cnf;rows=self.rows;order=self.order;degree=self.degree;anchors=list(sites(self.fixed));known=self.kind in ('square','two') or truth is not None
        exact=self.kind=='square' or truth is not None
        def weak(left,right):
            return (truth[left]&truth[right]).bit_count()==1 if truth is not None else {left,right} in ({0,1},{2,3})
        def quota(left,right):
            return squares(truth,left,right) if truth is not None else 12+2*({left,right} in ({0,3},{1,2}))
        for root in anchors:
            hood=list(sites(rows[root]));signatures={}
            for other in range(order):
                if other==root or other in hood:continue
                lits=[form.edge(point,other) for point in hood]
                lower=1 if not known or weak(root,other) else 2
                upper=1 if known and weak(root,other) else 3
                bounds=form.thresholds(lits,4)
                form.add(bounds[lower-1]);form.add(neg(bounds[upper]));signatures[other]=bounds
            if level>=2 and exact:
                for point in hood:
                    triples=[form.conjunction(form.edge(point,other),bounds[2]) for other,bounds in signatures.items()]
                    singles=sum(1 for other in signatures if weak(root,other) and ((truth[point]>>other&1) if truth is not None else rows[root]&rows[other]==1<<point))
                    if truth is None:
                        assert all(not weak(root,other) or other<4 for other in signatures)
                    required=quota(root,point)-(degree-1)+singles
                    form.cardinality(triples,required,required)
        if level>=2 and exact:
            for left,right in combinations(anchors,2):
                if not rows[left]>>right&1:continue
                values=[form.edge(first,second) for first in sites(rows[left]&~(1<<right)) for second in sites(rows[right]&~(1<<left))];q=quota(left,right);form.cardinality(values,q,q)
        if level>=3:
            for point in range(order):form.cardinality([form.edge(point,other) for other in range(order) if point!=other],degree,degree)
            for left,middle,right in combinations(range(order),3):form.add(neg(form.edge(left,middle)),neg(form.edge(middle,right)),neg(form.edge(left,right)))

    def bad(self,positive):
        form=self.cnf; allowed_set=allowed(self.kind);count=0;bad=[]
        def val(lit):return lit is True or (type(lit) is int and lit in positive)
        for pick0,pick1,edge0,edge1,cycle0,cycle1 in self.interfaces:
            activation=(form.edge(*edge0),form.edge(*edge1)) if self.mode in ('all','allpack') else (pick0,pick1)
            if not all(val(lit) for lit in activation):continue
            cross=[form.edge(first,second) for first in cycle0 for second in cycle1];mask=sum(1<<idx for idx,lit in enumerate(cross) if val(lit));count+=1
            if mask not in allowed_set:
                clause=[neg(lit) for lit in activation]+[neg(cross[idx]) if val(cross[idx]) else cross[idx] for idx in explain(self.kind,mask)]
                bad.append(sorted(set(lit for lit in clause if type(lit)is int)))
        return count,bad

    def solve(self,conflicts,rounds,planted=None):
        started=process_time();form=self.cnf;cuts=0;result={};solver=Cadical195(bootstrap_with=form.clauses)
        assumptions=[]
        if planted is not None:
            assumptions=[form.edge(left,right,False)*(1 if planted[left]>>right&1 else -1) for left,right in combinations(range(self.order),2)]
        for iteration in range(rounds):
            available=conflicts-solver.accum_stats()['conflicts']
            if available<1:break
            solver.conf_budget(available);status=solver.solve_limited(assumptions=assumptions)
            if status is None:break
            if not status:result['status']='empty';break
            positive={lit for lit in solver.get_model() if lit>0};count,bad=self.bad(positive)
            if not bad:
                result.update(status='compatible',interfaces=count,adj=[bitset(other for other in range(self.order) if other!=point and form.edge(point,other,False) in positive) for point in range(self.order)],picks=[[edge for edge,pick in edges.items() if pick in positive] for edges in self.edge_groups]);
                if self.bouquets:result['bouquet']=[[edge for edge,pick in group.items() if pick in positive] for group in self.bouquets]
                break
            for clause in bad:solver.add_clause(clause)
            cuts+=len(bad)
        result.setdefault('status','cap');result.update(rounds=iteration+1,cuts=cuts,conflicts=solver.accum_stats()['conflicts'],cpu=process_time()-started,vars=form.nvars,clauses=len(form.clauses));solver.delete();return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('input',type=Path);parser.add_argument('kind',choices=('general','two','square','c22'));parser.add_argument('mode',choices=('one','match','all','allpack'));parser.add_argument('--quota',type=int);parser.add_argument('--design',type=int,default=0);parser.add_argument('--cap',type=int,default=2000);parser.add_argument('--rounds',type=int,default=100);parser.add_argument('--start',type=int,default=0);parser.add_argument('--step',type=int,default=1);parser.add_argument('--limit',type=int,default=0);parser.add_argument('--plant',action='store_true');args=parser.parse_args();emitted=0
    for idx,line in enumerate(args.input.read_text().splitlines()):
        if idx<args.start or (idx-args.start)%args.step:continue
        key,frame,truth=json.loads(line);t0=process_time();system=System(frame,args.mode,args.kind,args.design,truth,args.quota);res=system.solve(args.cap,args.rounds,truth if args.plant else None);res.update(id=key,sha=same_line(frame),totalcpu=process_time()-t0);print(json.dumps(res,separators=(',',':')),flush=True);emitted+=1
        if args.limit and emitted>=args.limit:break


if __name__=='__main__':main()
