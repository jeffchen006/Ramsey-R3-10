from time import process_time
import json,sys
from pysat.solvers import Cadical195
from book_strata import DEST,standard
from book_edge_sat import encode
from wing_population import separate
from wing_atlas import labelled


def inputs(low,high):
    done={}
    for path in DEST.glob('pop*.jsonl'):
        for line in path.read_text().splitlines():
            record=json.loads(line)
            if low<=record['edges']<=high and record['status']=='fractional' and record['mode']=='basic':done[record['id']]=record
    return [done[key] for key in sorted(done)]


def probe(record,edges,cap,full=False):
    start=process_time();graph=standard(record['rows']);form,_=encode(graph,40,9,{(1,2)},edges,full);engine=Cadical195(bootstrap_with=form.clauses);engine.conf_budget(cap);sat=engine.solve_limited();result=dict(id=record['id'],edges=edges,full=full,status=str(sat),conf=engine.accum_stats()['conflicts'],cpu=process_time()-start);engine.delete()
    if sat is False:form.write(DEST/('wing-'+str(record['id'])+('-full' if full else '-edge' if edges else '-mask')+'.cnf'))
    return result


if __name__=='__main__':
    stage=sys.argv[1];low,high,shard,mod=map(int,sys.argv[2:6]);cap=int(sys.argv[6]) if len(sys.argv)>6 else 1500
    for idx,record in enumerate(inputs(low,high)):
        if idx%mod!=shard:continue
        if stage=='ramsey':print(json.dumps(separate(record['id'],labelled(record['rows']),stage),separators=(',',':')),flush=True)
        else:
            for edges in ((True,) if stage=='full' else (False,True)):print(json.dumps(probe(record,edges,cap,stage=='full'),separators=(',',':')),flush=True)
