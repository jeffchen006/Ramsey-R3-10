"""Reconcile orbit IDs, independently bound formulas, markers and storage prices."""
import json,sys,statistics
from pathlib import Path
from middle16_roster import SCOUT,ROOT

def rows(path):return list(map(json.loads,path.read_text().splitlines()))

def holdout():
    from middle16_price import fixedstars
    controls=rows(SCOUT/'hold.jsonl'); supports=(SCOUT/'pure.txt').read_text().splitlines();count=0
    for line,control in zip((SCOUT/'hold.tsv').read_text().splitlines(),controls,strict=True):
        host,ordinal,*word=map(int,line.split());assert (host,ordinal)==(control['id'],control['ordinal'])
        result=fixedstars.run([list(map(int,supports[host].split())),fixedstars.fromprofile(*word[:2]),fixedstars.fromprofile(*word[2:])],7,17,9,16,1,cap=3200,rules=1)
        assert result['status']==control['status']=='False' and result['clauses']==control['clauses'];count+=1
    assert count==48;print('48/48 old holdouts UNSAT, no proof claimed')

def summarize(source,clean):
    inventory=rows(source/'roster.jsonl');pilot=rows(source/'pilot.jsonl');original=rows(source/'primary.jsonl');replayed=rows(clean/'replay.jsonl')
    samples={row['tag']:row for row in original};assert len(samples)==157
    assert len(pilot)==len(original)==len(replayed) and len({(row['host'],row['id']) for row in pilot})==len(pilot)
    for row in pilot:
        checked=samples[f"{row['kind']}-{row['host']}-{row['id']}"];assert checked['weight']==row['weight']
    for row,again in zip(original,replayed,strict=True):
        for field in ('tag','kind','weight','cnf_sha','cnf_bytes','proof_sha','gzip_bytes','proof_bytes'):assert row[field]==again[field]
        for root in (source/'primary',clean/'archives'):
            for checker,marker in [('cake_lpr','s VERIFIED UNSAT'),('lrat-check','c VERIFIED')]:
                assert marker in (root/f"{row['tag']}.{checker}.log").read_text().splitlines()
        assert row['total']<10 and again['total']<10
        if row['kind']=='tail':assert row['matches_old_lrat'] and again['matches_old_lrat']
    fresh=[row for row in original if row['kind']=='new'];old=[row for row in original if row['kind']=='tail']
    print('host size pilot orbit_weight cpu_mean cpu_max lrat_mean lrat_max')
    costs={field:0 for field in ('total','rebind','proof_bytes','cnf_bytes','cnf_gzip','gzip_bytes','replay')}
    for host in sorted({row['host'] for row in fresh}):
        sample=[row for row in fresh if row['host']==host]; full=sum(row['host']==host for row in inventory)
        print(host,full,len(sample),sum(row['weight'] for row in sample),f"{statistics.mean(row['total'] for row in sample):.4f}",f"{max(row['total'] for row in sample):.4f}", round(statistics.mean(row['proof_bytes'] for row in sample)), max(row['proof_bytes'] for row in sample))
        for field in costs:
            if field=='replay':population=[row['total'] for row in replayed if row['kind']=='new' and row['host']==host]
            else:population=[row[field] for row in sample]
            costs[field]+=full*statistics.mean(population)
    print('full stratum-weighted estimates',costs)
    for label,group in [('fresh',fresh),('tails',old),('all',original),('clean',replayed)]:
        print(label,'weights',sum(row['weight'] for row in group),'max cpu',max(row['total'] for row in group),'aggregate', {field:round(sum(row.get(field,0) for row in group),5) for field in ['total','rebind','produce','cake_lpr','lrat-check','proof_bytes','gzip_bytes','cnf_bytes','cnf_gzip']})
    print('PASS 155 new + two previous tails; independent census and byte bindings; two verifiers twice per ordinary LRAT')

if __name__=='__main__':
    if sys.argv[1]=='holdout':holdout()
    else:summarize(*(Path(arg) for arg in sys.argv[1:]))
