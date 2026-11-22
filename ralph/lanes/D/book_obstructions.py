"""Use all viable three-site vertex covers, respecting independent sets padded by known stars."""
from itertools import combinations
from pathlib import Path
from time import process_time
import argparse,json
from book_counter import Countermodel
from book_controls import bitset,sites
from book_multicover import seeds
from book_packing import subsets
from book_seedpack import upper
from kernel_cnf import neg
from pysat.solvers import Cadical195


def prepare(frame,record,quota,kind):
    system=Countermodel(frame,quota,kind,record);form=system.form;degree=system.degree
    may=[word&~ban for word,ban in zip(upper(frame),record['ban'])];lo=record['lo'];roster=seeds(may);cache=[{},{}];pre=0
    def options(side,pool):
        if pool in cache[side]:return cache[side][pool]
        options=set();table=system.tables[side];constraints={}
        for seed,allowed in roster:
            mask=allowed&pool;bound=degree-seed.bit_count()
            if bound<mask.bit_count():constraints[mask]=min(bound,constraints.get(mask,bound))
        for cover in combinations(sites(pool),min(quota-1,pool.bit_count())):
            independent=pool^bitset(cover)
            if any((mask&independent).bit_count()>bound for mask,bound in constraints.items()):continue
            absent=[]
            for first,second,edge in table:
                if independent>>first&1 and independent>>second&1:
                    if edge is True:break
                    absent.append(edge)
            else:options.add(tuple(sorted(absent)))
        if not options:out=False
        elif () in options:out=True
        else:
            out=form.new();choices=[]
            for key in options:
                pick=form.new();choices.append(pick)
                for edge in key:form.add(-pick,-edge)
            form.add(-out,*choices)
        cache[side][pool]=out;return out
    for choice in subsets(system.shared):
        left=system.pools[0]&~(system.shared^choice);right=system.pools[1]&~choice
        lhs=options(0,left);rhs=options(1,right);form.add(lhs,rhs);pre+=lhs is False and rhs is False
        if pre:break
    return system,pre


def main():
    parser=argparse.ArgumentParser();parser.add_argument('folder',type=Path);parser.add_argument('--cap',type=int,default=10000);parser.add_argument('--kind',default='general');parser.add_argument('--key',type=int,required=True);parser.add_argument('--dump',type=Path);args=parser.parse_args();folder=args.folder;frames={key:f for key,f,_ in map(json.loads,(folder/'hard-four.in').read_text().splitlines())};record=next(row for row in map(json.loads,(folder/'mate-cases.jsonl').read_text().splitlines()) if row['id']==args.key);start=process_time();sys,pre=prepare(frames[args.key],record,4,args.kind);form=sys.form
    if args.dump:form.write(args.dump)
    print('encoded',args.key,pre,form.nvars,len(form.clauses),'cpu',process_time()-start,flush=True);sat=Cadical195(bootstrap_with=form.clauses);sat.conf_budget(args.cap);result=sat.solve_limited();row=dict(key=args.key,result=str(result),conflicts=sat.accum_stats()['conflicts'],cpu=process_time()-start)
    if result:
        positive={lit for lit in sat.get_model() if lit>0};assert next(iter(sys.partitions(positive)),None) is None
        row['edges']=[pair for pair in sys.optional if form.edge(*pair)in positive]
    print(json.dumps(row));sat.delete()


if __name__=='__main__':main()
