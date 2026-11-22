"""Price C8 component population profiles; physical Q labels, no edge symmetry clauses."""
from itertools import combinations
from time import process_time
import json,sys
from pysat.solvers import Cadical195
from equal_roles import DEST
from hex_unsplit import model
from hex_hub import build


def populations():
    rows=[]
    for idx,line in enumerate((DEST/'c8.pop').read_text().splitlines()):
        words=tuple(map(int,line.split()));debit=0
        for left,right in combinations(range(8),2):
            dist=min(right-left,8-right+left)
            if dist==1:continue
            common=int(not(dist%2))+int(dist==2)+sum(word>>left&word>>right&1 for word in words);assert common in (1,2,3);debit+=common==1
        if debit==0:rows.append((idx,words))
    return rows


def make(words,mode):
    cycle=[1<<((site+1)%8)|1<<((site-1)%8) for site in range(8)]
    if mode in ('upper','base'):return model(cycle,words,0,43,mode)
    return build(cycle,words,9,0,43,True,False,True)


def solve(idx,words,mode,cap):
    from hex_oneproof import seeds,cuts,literal
    from book_controls import bitset
    start=process_time();form=make(words,mode);sat=Cadical195(bootstrap_with=form.clauses);generated=[]
    while True:
        sat.conf_budget(max(1,cap-sat.accum_stats()['conflicts']));result=sat.solve_limited()
        if not result or mode!='seed':break
        positive=set(sat.get_model());truth=[bitset(other for other in range(21) if other!=point and form.edge(point,other,False) in positive) for point in range(21)];hub=bitset(point for point in range(21) if form.edge(21,point) in positive);fresh=cuts(truth,hub,seeds(8)[1],words)
        if not fresh:break
        for seed,subset in fresh:
            clause=literal(form,seed,subset);form.add(*clause);sat.add_clause(clause);generated.append((seed,subset))
        if sat.accum_stats()['conflicts']>=cap:result=None;break
    out=dict(id=idx,mode=mode,status=str(result),conf=sat.accum_stats()['conflicts'],cpu=process_time()-start,cuts=generated);sat.delete()
    if result is False:form.write(DEST/f'oct-{idx}-{mode}.cnf')
    return out


if __name__=='__main__':
    mode=sys.argv[1];cap,shard,mod=map(int,sys.argv[2:5]);rows=populations();selected=rows[shard::mod] if len(sys.argv)==5 else [rows[idx] for idx in map(int,sys.argv[5:])]
    for idx,words in selected:print(json.dumps(solve(idx,words,mode,cap)),flush=True)
