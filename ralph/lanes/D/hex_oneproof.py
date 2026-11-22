"""Lazy labelled Ramsey clauses on the unsplit hub projection; every cut has a literal independent seed."""
from itertools import combinations
from time import process_time
import json,sys
from pysat.solvers import Cadical195
from equal_roles import DEST
from hex_hub import make
from hex_fibers import masks
from book_controls import graph_masks,reorder,sites,bitset
from book_strata import independent_sets


def seeds(width=6):
    pairs=[(0,1),(0,2),*[(1+site%2,3+site) for site in range(width)],*[(3+site,3+(site+1)%width) for site in range(width)]];rows=[0]*(width+3)
    for left,right in pairs:rows[left]|=1<<right;rows[right]|=1<<left
    return rows,independent_sets(rows)


def literal(form,seed,subset):
    return [form.edge(left,right) for left,right in combinations(sites(subset),2) if form.edge(left,right) is not False]+([form.edge(21,point) for point in sites(subset)] if seed&1 else [])


def cuts(truth,hub,records,words=None):
    if words is None:words=masks()
    found={}
    for seed in records:
        pool=bitset(point for point,word in enumerate(words) if not((word<<3)&seed) and not(seed&1 and hub>>point&1));need=10-seed.bit_count()
        def walk(pool,used,need):
            if need==0:return used
            while pool.bit_count()>=need:
                bit=pool&-pool;pool^=bit;idx=bit.bit_length()-1;result=walk(pool&~truth[idx],used|bit,need-1)
                if result:return result
        subset=walk(pool,0,need)
        if subset:found[(subset,seed&1)]=seed
    return [(seed,subset) for (subset,_),seed in sorted(found.items())]


def run(debit,edges,upper,markers,cap,limit):
    form=make(debit,edges,upper,markers);sat=Cadical195(bootstrap_with=form.clauses);graph,records=seeds();used=[];start=process_time();result=None
    for iteration in range(limit):
        sat.conf_budget(max(1,cap-sat.accum_stats()['conflicts']));result=sat.solve_limited()
        if not result:break
        positive=set(sat.get_model());truth=[bitset(other for other in range(21) if other!=point and form.edge(point,other,False) in positive) for point in range(21)];hub=bitset(point for point in range(21) if form.edge(21,point) in positive);fresh=cuts(truth,hub,records)
        if not fresh:break
        for seed,subset in fresh:
            clause=literal(form,seed,subset);form.add(*clause);sat.add_clause(clause);used.append((seed,subset))
        result=None
        if sat.accum_stats()['conflicts']>=cap:break
    tag=f'hexone-{debit}-{edges}-{upper}-{markers}';out=dict(tag=tag,status=str(result),conf=sat.accum_stats()['conflicts'],rounds=iteration+1,cuts=used,cpu=process_time()-start);sat.delete()
    if result is False:form.write(DEST/f'{tag}.cnf')
    print(json.dumps(out))


if __name__=='__main__':run(*map(int,sys.argv[1:]))
