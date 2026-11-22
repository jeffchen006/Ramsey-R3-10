"""If NO marked pair permits the quota, every other disjoint pair must have a surviving profile."""
from collections import Counter,defaultdict
from itertools import combinations,product
from pathlib import Path
from time import process_time
import argparse,json
from pysat.solvers import Cadical195
from book_controls import bitset,book,graph_masks,flags,sites
from book_counter import Countermodel
from book_obstructions import prepare
from kernel_cnf import ROOT,neg


def views(rows,first,second):
    for swap,flip,rev in product(range(2),repeat=3):
        lhs,rhs=(second,first) if swap else (first,second);yield (lhs[::-1] if flip else lhs)+(rhs[::-1] if rev else rhs)


def profile(rows,points):
    anchor,new,other,last=points
    inside=tuple((rows[lhs]>>rhs)&1 for lhs,rhs in combinations(points,2));counts=[0]*8;neighbors=[0]*8
    for site in range(len(rows)):
        if site in points:continue
        cell=((rows[anchor]>>site)&1)|(((rows[other]>>site)&1)<<1)|(((rows[last]>>site)&1)<<2);counts[cell]+=1;neighbors[cell]+=(rows[new]>>site)&1
    return (inside,tuple(counts)),tuple(neighbors)


def catalogue(frames):
    result=defaultdict(set)
    for rows,first,second in frames:
        for order in views(rows,first,second):
            key,value=profile(rows,order);result[key].add(value)
    return result


def c22frames():
    for line in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        rows=graph_masks(line)
        if any(row.bit_count()!=6 for row in rows) or max((left&right).bit_count() for left,right in combinations(rows,2))>3:continue
        for first,second in combinations(flags(rows),2):
            if not(set(book(rows,first)[0])&set(book(rows,second)[0])):yield rows,first,second


def add(system,library):
    fixed,*rows=system.frame;form=system.form;stats=Counter()
    for anchor in range(4):
        other,last=(2,3) if anchor<2 else (0,1);central,=sites(rows[other]&rows[last]);path={other,last,central}
        for new in range(len(rows)):
            if new==anchor or new in path or rows[anchor]>>new&1:continue
            order=(anchor,new,other,last);key,_=profile(rows,order);alts=library.get(key,());hood=list(sites(rows[anchor]));common=form.thresholds([form.edge(new,point) for point in hood],4);form.add(common[0]);form.add(neg(common[3]));anycase=[common[1]]+[form.edge(new,point) for point in path if point in hood]
            bins=[[]for _ in range(8)]
            for site in range(len(rows)):
                if site in order:continue
                mask=((rows[anchor]>>site)&1)|(((rows[other]>>site)&1)<<1)|(((rows[last]>>site)&1)<<2);bins[mask].append(form.edge(new,site))
            if alts:
                sizes=[form.thresholds(entries,1+max(option[idx] for option in alts)) for idx,entries in enumerate(bins)]
                for variant in sorted(alts):
                    choice=form.new();anycase.append(choice)
                    for need,bounds in zip(variant,sizes):
                        if need:form.add(-choice,bounds[need-1])
                        form.add(-choice,neg(bounds[need]))
            form.add(*anycase);stats[len(alts)]+=1
    return dict(stats)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);parser.add_argument('--cal',action='store_true');parser.add_argument('--key',type=int);parser.add_argument('--no-covers',action='store_true');parser.add_argument('--cap',type=int,default=30000);parser.add_argument('--dump',type=Path);args=parser.parse_args();folder=args.folder
    if args.cal:
        library=catalogue(c22frames());statuses=Counter()
        for key,frame,truth in map(json.loads,(folder/'cal.in').read_text().splitlines()):
            for name,lib in [('real',library),('empty',{})]:
                sys=Countermodel(frame,2);add(sys,lib);form=sys.form;solver=Cadical195(bootstrap_with=form.clauses);res=solver.solve(assumptions=[form.edge(left,right,False)*(1 if truth[left]>>right&1 else -1) for left,right in combinations(range(len(truth)),2)]);solver.delete();statuses[name,res]+=1
                if name=='real':assert res
        print('C22 planted explicit complete graphs',statuses);assert statuses['empty',False];return
    start=process_time();frames={key:f for key,f,_ in map(json.loads,(folder/'hard-four.in').read_text().splitlines())};library=catalogue((frames[k][1:],(0,1),(2,3)) for k in (119,179));record=next(row for row in map(json.loads,(folder/'mate-cases.jsonl').read_text().splitlines()) if row['id']==args.key)
    sys=Countermodel(frames[args.key],4,'general',record) if args.no_covers else prepare(frames[args.key],record,4,'general')[0];stats=add(sys,library);form=sys.form
    if args.dump:form.write(args.dump)
    print('encoded',stats,form.nvars,len(form.clauses),process_time()-start,flush=True);solver=Cadical195(bootstrap_with=form.clauses);solver.conf_budget(args.cap);res=solver.solve_limited();row=dict(key=args.key,result=str(res),conflicts=solver.accum_stats()['conflicts'],cpu=process_time()-start)
    if res:
        positive=set(solver.get_model());row['adj']=[bitset(other for other in range(len(frames[args.key])-1) if point!=other and form.edge(point,other,False) in positive) for point in range(len(frames[args.key])-1)]
    print(json.dumps(row));solver.delete()


if __name__=='__main__':main()
