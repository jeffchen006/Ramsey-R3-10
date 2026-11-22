from itertools import combinations
from time import process_time
import sys,json
from pysat.solvers import Cadical195
from book_strata import DEST,independent_sets
from book_controls import sites
from kernel_cnf import Cnf,neg


def build(width,alpha,parts):
    n=width*3;groups=[list(range(idx*width,(idx+1)*width)) for idx in range(3)];rows=[0]*(2*width);pos=0
    for length in parts:
        for slot in range(length):
            left=pos+slot;right=width+left;nextpoint=pos+(slot+1)%length
            for point in (left,nextpoint):rows[point]|=1<<right;rows[right]|=1<<point
        pos+=length
    assert pos==width;fixed={}
    for first,second in combinations(range(n),2):
        if second<2*width:fixed[first,second]=bool(rows[first]>>second&1)
        elif first>=2*width:fixed[first,second]=False
    form=Cnf(n,fixed)
    for group in groups[:2]:
        for site in group:form.cardinality([form.edge(site,q) for q in groups[2]],2,2)
        for q in groups[2]:form.cardinality([form.edge(site,q) for site in group],2,2)
    for left,right in combinations(range(2*width),2):
        if rows[left]>>right&1:
            for q in groups[2]:form.add(-form.edge(left,q),-form.edge(right,q))
    for left,right in zip(groups[2],groups[2][1:]):
        prefix=True
        for site in range(2*width):
            a,b=form.edge(site,left),form.edge(site,right);form.add(neg(prefix),a,-b);out=form.new();form.add(neg(prefix),-a,-b,out);form.add(neg(prefix),a,b,out);prefix=out
    for seed in independent_sets(rows):
        size=seed.bit_count();need=alpha+1-size
        if need>width:continue
        if need<=0:form.add();continue
        avoid=[]
        for point in groups[2]:
            var=form.new();form.add(var,*(form.edge(site,point) for site in sites(seed)));avoid.append(var)
        for subset in combinations(avoid,need):form.add(*(-var for var in subset))
    return form


if __name__=='__main__':
    width,alpha,cap=map(int,sys.argv[1:4]);parts=list(map(int,sys.argv[4:]));start=process_time();form=build(width,alpha,parts);sat=Cadical195(bootstrap_with=form.clauses);sat.conf_budget(cap);result=sat.solve_limited();tag='triad-'+str(width)+'-'+str(alpha)+'-'+''.join(map(str,parts));form.write(DEST/(tag+'.cnf'));print(json.dumps(dict(tag=tag,status=str(result),conflicts=sat.accum_stats()['conflicts'],cpu=process_time()-start,clauses=len(form.clauses))));sat.delete()
