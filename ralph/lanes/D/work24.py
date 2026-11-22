from collections import Counter
from datetime import datetime
from pathlib import Path
import fcntl
import json
import os
import sys
import time

from closure22 import ROOT,digest,stage
from patch23 import OLD
from wing24 import OUT,formula

SLOT=110_000_000
LIMIT=5_550_000_000

def timestamp():return datetime.now().astimezone().isoformat(timespec='seconds')

def task(key,small=False):
    dest=OUT/key;log=[];files={};status='open';os.chdir(dest)
    try:
        for name,cmd,cap,limit,rc,marker in [
            *([('discover',[sys.executable,'-B',Path(__file__).with_name('generic24.py'),key],65,2000000,0,None)] if key.startswith('v') else []),
            ('bind',[sys.executable,'-B',Path(__file__).resolve(),'bind',key],55,12_000_000 if small else 19_000_000,0,None),
            ('solve',[ROOT/'opt/bin/cadical','--binary','--lrat','input.cnf','base.bin'],100,14_000_000 if small else 32_000_000,20,'s UNSATISFIABLE'),
            ('trim',[OLD/'lrat-trim','-a','input.cnf','base.bin','proof.lrat'],90,27_000_000 if small else 55_000_000,20,'s VERIFIED'),
            *([('thin',[sys.executable,'-B',Path(__file__).with_name('bank24.py'),'compact','proof.lrat'],65,55_000_000,0,None)] if key.startswith(('h21_','h20_','h19_','b')) else []),
            ('check',[ROOT/'opt/bin/lrat-check','input.cnf','proof.lrat'],110,2_000_000,0,'c VERIFIED'),
            ('cake',[ROOT/'opt/bin/cake_lpr','--CML_HEAP_SIZE=256','--CML_STACK_SIZE=32','input.cnf','proof.lrat'],120,2_000_000,0,'s VERIFIED UNSAT'),
            ('compress',['zstd','--single-thread','-7','-q','proof.lrat','-o','proof.zst'],70,15_000_000 if small else 25_000_000,0,None),
            ('integrity',['zstd','-tq','proof.zst'],45,2_000_000,0,None)]:
            result=stage(name,cmd,cap,limit,rc,marker);log.append(result)
            if not result['ok']:status=f'{name}:{result["rc"]}';break
            if name=='trim':Path('base.bin').unlink()
        else:
            files={file:[digest(file),Path(file).stat().st_size] for file in ('input.cnf','proof.lrat','proof.zst')};status='dual_checked'
    finally:
        for name in ('input.cnf','base.bin','proof.lrat'):Path(name).unlink(missing_ok=True)
        if status!='dual_checked':Path('proof.zst').unlink(missing_ok=True)
        row=dict(key=key,status=status,log=log,files=files);Path('result.tmp').write_text(json.dumps(row,sort_keys=True)+'\n');os.replace('result.tmp','result.json')
        with (OUT/'lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);account=OUT/'charged';account.write_text(str(int(account.read_text())+sum(path.stat().st_size for path in dest.iterdir())));(OUT/f'reserve.{key}').unlink()
    print(key,status,round(sum(step['cpu'] for step in log),2),files.get('proof.zst',[None,0])[1],flush=True)

def worker(keys):
    for key in keys:
        while True:
            with (OUT/'lock').open('a') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX);charged=int((OUT/'charged').read_text());reserved=len(list(OUT.glob('reserve.*')))*SLOT
                if (OUT/key).is_dir():break
                if (OUT/'stop').exists() or charged+SLOT>LIMIT:print('guard',key,flush=True);return
                if charged+reserved+SLOT<=LIMIT:(OUT/f'reserve.{key}').write_text(str(SLOT));(OUT/key).mkdir();acquired=True
                else:acquired=False
            if acquired:task(key);break
            time.sleep(2)

def reconcile():
    from hex18 import OUT as source
    keys=[line.split()[1] for line in (source/'manifest.tsv').read_text().splitlines()];out=[]
    for shard in range(2):
        lines=[line.split() for line in (source/f'check{shard}.log').read_text().splitlines()];assert [line[0] for line in lines]==keys[shard::2] and all(line[1]=='dual_replayed' for line in lines);out.extend((line[0],shard,line[2]) for line in lines)
    assert len(set(keys))==len(out)==2752;(OUT/'replay23.tsv').write_text(''.join(f'{key}\t{shard}\t{cpu}\n' for key,shard,cpu in sorted(out)));print('2752/2752 exact per-shard replay join;',round(sum(float(line[2]) for line in out),2),'checker child CPU-s, all existing receipts')

if __name__=='__main__':
    if sys.argv[1]=='bind':
        if sys.argv[2].startswith('b'):
            from repair24 import formula_repair
            form=formula_repair(sys.argv[2])
        elif sys.argv[2].startswith(('u','v')):
            from generic24 import formula_generic,GEN,discover
            if sys.argv[2].startswith('v') and not (GEN/f'{sys.argv[2]}.cards').exists():
                code=discover(sys.argv[2]);print('discovery',code,flush=True)
                if code:sys.exit(code)
            form=formula_generic(sys.argv[2])
        elif sys.argv[2].startswith('z'):
            from deep24 import formula_deep
            form=formula_deep(sys.argv[2])
        elif sys.argv[2].startswith('h'):
            from high24 import formula_high
            form=formula_high(sys.argv[2])
        elif sys.argv[2].startswith('s'):
            from split24 import formula_split
            form=formula_split(sys.argv[2])
        else:form=formula(sys.argv[2])
        form.write(Path('input.cnf'))
    elif sys.argv[1]=='reconcile':reconcile()
    elif sys.argv[1]=='worker':worker((OUT/sys.argv[2]).read_text().splitlines()[int(sys.argv[3])::int(sys.argv[4])]);
    else:worker(sys.argv[2:])
