"""Test a root cover by allowing new singleton paths only at compatible physical sites."""
import argparse,json
from collections import defaultdict
from itertools import combinations
from pathlib import Path
from time import process_time
from pysat.solvers import Cadical195
from book_controls import bitset,sites
from book_reroot import views,c22frames,catalogue,add
from book_seedpack import upper
from kernel_cnf import Cnf,neg


def allowed_templates(frames):
    table=defaultdict(set)
    for rows,first,second in frames:
        for left,right,anchor,other in views(rows,first,second):
            own,=sites(rows[left]&rows[right]);opp,=sites(rows[anchor]&rows[other]);pairs=[(left,anchor),(left,other),(right,anchor),(right,other)]
            signature=tuple((rows[lhs]>>rhs)&1 for lhs,rhs in pairs);centre=((rows[own]>>anchor)&1)+2*((rows[own]>>other)&1)
            pattern=tuple((rows[opp]>>point)&1 for point in (left,right))+tuple((rows[lhs]&rows[rhs]).bit_count() for lhs,rhs in pairs);table[signature,centre].add(pattern)
    return table


class Formula:
    def __init__(self,frame,table,library):
        self.frame=frame;fixed,*rows=frame;order=len(rows);degree=rows[0].bit_count();may=upper(frame);self.form=form=Cnf(order,{(left,right):bool(rows[left]>>right&1) for left,right in combinations(range(order),2) if rows[left]>>right&1 or not may[left]>>right&1})
        for point in range(order):form.cardinality([form.edge(point,other) for other in range(order) if other!=point],degree,degree)
        code={};two={}
        for left,right in combinations(range(order),2):
            edge=form.edge(left,right);walks={point:form.conjunction(form.edge(point,left),form.edge(point,right)) for point in sites(may[left]&may[right])};bounds=form.thresholds(list(walks.values()),4);form.add(edge,bounds[0]);form.add(neg(bounds[3]));code[left,right]=bounds;two[left,right]=walks
            for walk in walks.values():form.add(neg(edge),neg(walk))
        for anchor,other in [(0,1),(2,3)]:
            centre,=sites(rows[anchor]&rows[other]);path={anchor,other,centre}
            for left,right in combinations(sorted(set(range(order))-path),2):
                if form.edge(left,right) is True:continue
                pairs=[(left,anchor),(left,other),(right,anchor),(right,other)];signature=tuple((rows[lhs]>>rhs)&1 for lhs,rhs in pairs);lookup={}
                for own,walk in two[left,right].items():
                    if own in path or walk is False:continue
                    cell=((rows[own]>>anchor)&1)+2*((rows[own]>>other)&1)
                    if cell not in lookup:
                        choices=[]
                        for pattern in sorted(table.get((signature,cell),())):
                            required=[form.edge(centre,point) if bit else neg(form.edge(centre,point)) for point,bit in zip((left,right),pattern[:2])]
                            for pair,want in zip(pairs,pattern[2:]):
                                bounds=code[tuple(sorted(pair))]
                                if want:required.append(bounds[want-1])
                                required.append(neg(bounds[want]))
                            if any(lit is False for lit in required):continue
                            pending=[lit for lit in required if type(lit)is int]
                            if not pending:choices=[True];break
                            select=form.new();choices.append(select)
                            for lit in pending:form.add(-select,lit)
                        lookup[cell]=choices
                    form.add(code[left,right][1],neg(walk),*lookup[cell])
        add(self,library)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);parser.add_argument('--family',default='179');parser.add_argument('--key',type=int);parser.add_argument('--cap',type=int,default=8000);parser.add_argument('--cal',action='store_true');parser.add_argument('--dump',type=Path);args=parser.parse_args();folder=args.folder;start=process_time()
    if args.cal:
        frames=list(c22frames());deck=list(map(json.loads,(folder/'cal.in').read_text().splitlines()))
    else:
        lookup={key:fr for key,fr,_ in map(json.loads,(folder/'roots.in').read_text().splitlines())};family=list(map(int,args.family.split(',')));assert args.key in family;frames=[(lookup[key][1:],(0,1),(2,3)) for key in family];deck=[(args.key,lookup[args.key],None)]
    table=allowed_templates(frames);library=catalogue(frames)
    for key,frame,truth in deck:
        sys=Formula(frame,table,library);form=sys.form;solver=Cadical195(bootstrap_with=form.clauses);solver.conf_budget(args.cap);res=solver.solve_limited(assumptions=[form.edge(left,right,False)*(1 if truth[left]>>right&1 else -1) for left,right in combinations(range(len(truth)),2)] if truth else [])
        if truth:assert res
        if args.dump:form.write(args.dump)
        print(json.dumps(dict(id=key,result=str(res),conf=solver.accum_stats()['conflicts'],vars=form.nvars,clauses=len(form.clauses),cpu=process_time()-start)),flush=True);solver.delete()


if __name__=='__main__':main()
