import csv
import fcntl
import hashlib
import json
import os
import resource
import subprocess
import sys
import time
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SCOUT = ROOT / 'scratch/ideas/r021_R'
STORE = ROOT / 'scratch/D/closure22'
DECK = SCOUT / 'freeord.404..cnf.cards'
sys.path.insert(0, str(SCOUT))
from rebind import board
from shadow import Board, bits, Cadical195


def records():
    with (ROOT / 'scratch/D/wing21/counts.tsv').open() as stream:
        rows = [row for row in csv.DictReader(stream, delimiter='\t') if int(row['identity']) and row['row'] != '404']
    assert (len(rows),sum(int(row['identity']) for row in rows),sum(int(row['orbits']) for row in rows)) == (149,427324,250440)
    return {int(row['row']): row for row in rows}


def discover(host, head):
    row = records()[host]
    pairs = [1<<left | 1<<right for left,right in combinations(range(7),2)]
    support = [int(row['triple'])]+[mask for mask,multi in zip(pairs,row['word']) for _ in range(int(multi))]
    engine = Board(7,support,head+[-1]*(8-len(head)),9,3,(2,3),(2,3),15,17,ranks=[2]*5+[1]*3,poledegrees=[1]+[2]*6,ordered=True)
    return separate(engine,map(int,DECK.read_text().splitlines()))


def separate(engine,deck):
    engine.cert_cards = {}
    for mask in deck:
        cells = [engine.edge(left,right) for left,right in combinations(bits(mask),2)]
        if any(entry is True for entry in cells): continue
        clause = tuple(entry for entry in cells if type(entry) is int)
        if clause not in engine.cert_cards:
            engine.cert_cards[clause] = mask
            engine.cnf.append(clause)
    seed = len(engine.cert_cards)
    with Cadical195(bootstrap_with=engine.cnf) as solver:
        rounds = 0
        while True:
            solver.conf_budget(3000000-solver.accum_stats()['conflicts'])
            status = solver.solve_limited()
            if status is False: break
            if status is None or solver.accum_stats()['conflicts']>=3000000: return 3
            cuts = engine.blockers(set(solver.get_model()))
            if not cuts:
                print('RELAXED_MODEL',rounds,flush=True); return 10
            for clause in sorted(cuts): solver.add_clause(clause)
            rounds+=1
    cards = sorted(set(engine.cert_cards.values()))
    Path('cards').write_text(''.join(f'{mask}\n' for mask in cards))
    print('UNSAT_HINT',seed,len(cards),rounds,flush=True)
    return 0


def digest(path):
    checksum=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):checksum.update(block)
    return checksum.hexdigest()


def stage(name,command,cap,limit,code=0,marker=None):
    def bounds():
        resource.setrlimit(resource.RLIMIT_CPU,(cap,cap+1))
        resource.setrlimit(resource.RLIMIT_FSIZE,(limit,limit))
    start=os.times(); wall=time.monotonic(); output=Path(name+'.log')
    with output.open('w') as stream:
        result=subprocess.run(['timeout','-k','8',str(3*cap+25),*map(str,command)],stdout=stream,stderr=subprocess.STDOUT,preexec_fn=bounds)
    end=os.times(); ok=result.returncode==code and (not marker or marker in output.read_text(errors='replace').splitlines())
    return dict(stage=name,ok=ok,rc=result.returncode,cpu=round(end.children_user+end.children_system-start.children_user-start.children_system,3),wall=round(time.monotonic()-wall,3))


def task(host,head,discovery=120,rawcap=260000000,base=STORE,program=__file__,budget=15500000000,trim=None):
    sub=base/(str(host)+''.join(f'-{mask}' for mask in head)); sub.mkdir(); os.chdir(sub)
    log=[]; status='open'; manifest={}; slot=(max(2*rawcap,rawcap+134217728)+30000000) if trim else rawcap+136000000+10000000
    def put():
        Path('progress.json.tmp').write_text(json.dumps(dict(host=host,head=head,status=status,log=log,files=manifest),sort_keys=True)+'\n');os.replace('progress.json.tmp','progress.json')
    with (base/'staging.lock').open('a') as lock:
        fcntl.flock(lock,fcntl.LOCK_EX)
        if trim:
            saved=int((base/'accounted.bytes').read_text());pending=sum(int(path.read_text()) for path in base.glob('reserve.*'))
        else:
            saved=sum(path.stat().st_size for path in base.glob('*/proof.zst'));pending=sum(int(path.read_text()) for path in base.glob('*/reserved'))
        if saved+pending+slot>budget: status='staging_guard';put();return
        reserve=base/('reserve.'+str(host)) if trim else Path('reserved');reserve.write_text(str(slot))
    try:
        for name,command,cap,limit,rc,marker in [
            ('discover',[sys.executable,'-B',program,'discover',host,*head],discovery,12000000,0,None),
            ('bind',[sys.executable,'-B',program,'bind',host,*head],30,24000000,0,None),
            ('solve',[ROOT/'opt/bin/cadical','--lrat','--no-binary','input.cnf','proof.lrat'],180,rawcap,20,'s UNSATISFIABLE'),
            *([('trim',[trim,'-a','input.cnf','proof.lrat','trim.lrat'],100,rawcap,20,'s VERIFIED')] if trim else []),
            ('check',[ROOT/'opt/bin/lrat-check','input.cnf','proof.lrat'],120,4000000,0,'c VERIFIED'),
            ('cake',[ROOT/'opt/bin/cake_lpr','--CML_HEAP_SIZE=256','--CML_STACK_SIZE=32','input.cnf','proof.lrat'],160,4000000,0,'s VERIFIED UNSAT'),
            ('compress',['zstd','--single-thread','-4','-q','proof.lrat','-o','proof.zst'],90,134217728,0,None),
            ('roundtrip',['zstd','-tq','proof.zst'],45,4000000,0,None)]:
            result=stage(name,command,cap,limit,rc,marker);log.append(result)
            if not result['ok']: status=f"{name}:{result['rc']}";break
            if name=='trim':os.replace('trim.lrat','proof.lrat')
            put()
        else:
            manifest={file:{'sha256':digest(file),'size':Path(file).stat().st_size} for file in ['cards','input.cnf','proof.lrat','proof.zst']};status='dual_checked'
    finally:
        if status!='dual_checked': Path('proof.zst').unlink(missing_ok=True)
        Path('proof.lrat').unlink(missing_ok=True);Path('trim.lrat').unlink(missing_ok=True);Path('input.cnf').unlink(missing_ok=True); put()
        with (base/'staging.lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX)
            if trim:
                total=base/'accounted.bytes';total.write_text(str(int(total.read_text())+sum(path.stat().st_size for path in sub.iterdir() if path.is_file())))
            reserve.unlink(missing_ok=True)
        print(json.dumps([host,head,status,log]),flush=True)


if __name__=='__main__':
    action=sys.argv[1]
    if action=='manifest':
        allrows=records();ordered=sorted(allrows,key=lambda host: (hashlib.sha256(str(host).encode()).hexdigest(),host));ordered.remove(896);ordered.insert(0,896)
        for index,host in enumerate(ordered):print(index%24,host,allrows[host]['triple'],allrows[host]['identity'],allrows[host]['orbits'],sep='\t')
    elif action=='bind':
        formula,count=board(int(sys.argv[2]),list(map(int,sys.argv[3:])),Path('cards'));formula.to_file('input.cnf');print('rebound',count,formula.nv,len(formula.clauses))
    elif action=='discover':sys.exit(discover(int(sys.argv[2]),list(map(int,sys.argv[3:]))))
    elif action=='task':task(int(sys.argv[2]),list(map(int,sys.argv[3:])))
    elif action=='worker':
        index=int(sys.argv[2]);jobs=[int(line.split()[1]) for line in (STORE/'manifest.tsv').read_text().splitlines() if int(line.split()[0])==index]
        for host in jobs:
            if not (STORE/str(host)).exists():task(host,[])
