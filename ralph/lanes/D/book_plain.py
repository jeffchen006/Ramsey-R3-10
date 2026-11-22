"""Second terminal encoding: direct graph axioms, unpruned Konig covers, no seed table."""
import argparse,json
from itertools import combinations
from pathlib import Path
from time import process_time
from pysat.solvers import Cadical195
from book_controls import book,sites,bitset
from book_counter import Countermodel
from book_reroot import catalogue,add
from book_packing import subsets
from book_seedpack import upper
from kernel_cnf import Cnf,neg


def ordinary(frame,record):
    fixed,*rows=frame;order=len(rows);degree=rows[0].bit_count();pins={}
    for left,right in combinations(range(order),2):
        if record['lo'][left]>>right&1:pins[left,right]=True
        elif record['ban'][left]>>right&1:pins[left,right]=False
    form=Cnf(order,pins)
    for point in range(order):form.cardinality([form.edge(point,other) for other in range(order) if other!=point],degree,degree)
    for left,right in combinations(range(order),2):
        edge=form.edge(left,right);common=[form.conjunction(form.edge(left,site),form.edge(right,site)) for site in range(order) if site not in (left,right)]
        for path in common:form.add(neg(edge),neg(path))
        sizes=form.thresholds(common,4);form.add(edge,sizes[0]);form.add(neg(sizes[3]))
    return form


def build(frame,record,lib,quota,projected=False,accept=None):
    system=Countermodel(frame,quota,'general',record)
    if not projected:
        old=system.form;new=ordinary(frame,record)
        for table in system.tables:
            for first,second,edge in table:assert edge==new.edge(first,second) and type(edge)==type(new.edge(first,second))
        system.form=new
    if lib is not None:add(system,lib)
    if accept is None:accept=subsets(system.shared)
    for choice in accept:system.block(choice)
    return system


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);parser.add_argument('--key',type=int,required=True);parser.add_argument('--projected',action='store_true');parser.add_argument('--local',action='store_true');parser.add_argument('--dump',type=Path);parser.add_argument('--cap',type=int,default=15000);args=parser.parse_args();folder=args.folder;frames={key:f for key,f,_ in map(json.loads,(folder/'hard-four.in').read_text().splitlines())};lib=None if args.local else catalogue((frames[k][1:],(0,1),(2,3)) for k in (119,179));start=process_time();record=next(row for row in map(json.loads,(folder/'mate-cases.jsonl').read_text().splitlines()) if row['id']==args.key)
    system=build(frames[args.key],record,lib,4,args.projected);form=system.form;print('encode',form.nvars,len(form.clauses),process_time()-start,flush=True)
    if args.dump:form.write(args.dump)
    solver=Cadical195(bootstrap_with=form.clauses);solver.conf_budget(args.cap);answer=solver.solve_limited();print('result',args.key,answer,solver.accum_stats()['conflicts'],process_time()-start);solver.delete()
