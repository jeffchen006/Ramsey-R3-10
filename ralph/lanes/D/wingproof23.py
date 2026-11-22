import fcntl
import hashlib
import json
import os
import sys
import time
from pathlib import Path

from closure22 import ROOT,digest,stage
from patch23 import STORE,OLD,physical

OUT=STORE/'wing'; RAW=28000000; ASCII=49000000; SLOT=96000000


def newtask(token):
    sub=OUT/token;sub.mkdir();os.chdir(sub);log=[];files={};status='open'
    try:
        for name,cmd,cap,limit,rc,marker in [
            ('bind',[sys.executable,'-B',Path(__file__).resolve(),'bind',token],45,11000000,0,None),
            ('solve',[ROOT/'opt/bin/cadical','--lrat','--binary','input.cnf','base.bin'],100,RAW,20,'s UNSATISFIABLE'),
            ('trim',[OLD/'lrat-trim','-a','input.cnf','base.bin','proof.lrat'],90,ASCII,20,'s VERIFIED'),
            ('check',[ROOT/'opt/bin/lrat-check','input.cnf','proof.lrat'],110,2000000,0,'c VERIFIED'),
            ('cake',[ROOT/'opt/bin/cake_lpr','--CML_HEAP_SIZE=256','--CML_STACK_SIZE=32','input.cnf','proof.lrat'],120,2000000,0,'s VERIFIED UNSAT'),
            ('compress',['zstd','--single-thread','-6','-q','proof.lrat','-o','proof.zst'],70,23000000,0,None),
            ('integrity',['zstd','-tq','proof.zst'],45,2000000,0,None)]:
            result=stage(name,cmd,cap,limit,rc,marker);log.append(result)
            if not result['ok']:status=f'{name}:{result["rc"]}';break
            if name=='trim':Path('base.bin').unlink()
        else:
            files={file:[digest(file),Path(file).stat().st_size] for file in ('input.cnf','proof.lrat','proof.zst')};status='dual_checked'
    finally:
        for name in ('input.cnf','base.bin','proof.lrat'):Path(name).unlink(missing_ok=True)
        if status!='dual_checked':Path('proof.zst').unlink(missing_ok=True)
        receipt=dict(token=token,status=status,log=log,files=files);Path('result.tmp').write_text(json.dumps(receipt,sort_keys=True)+'\n');os.replace('result.tmp','result.json')
        with (OUT/'lock').open('a') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX);account=OUT/'charged';account.write_text(str(int(account.read_text())+sum(path.stat().st_size for path in sub.iterdir())));(OUT/f'reserve.{token}').unlink()
    print(token,status,round(sum(step['cpu'] for step in log),2),files.get('proof.zst',[None,0])[1],flush=True)


def active_s():
    if not (OUT/'go_large').exists():return True
    for line in (OLD.parent/'m14r23/staticpids.tsv').read_text().splitlines():
        pid=line.split()[1]
        try:
            if b'/static23.py\0' in Path(f'/proc/{pid}/cmdline').read_bytes():return True
        except OSError:pass
    return False


def worker(tokens,shard=0):
    for token in tokens:
        while True:
            if (OUT/'stop_after_current').exists():return
            with (OUT/'lock').open('a') as lock:
                fcntl.flock(lock,fcntl.LOCK_EX)
                if (OUT/token).is_dir() or (OUT/f'reserve.{token}').exists():break
                charged=int((OUT/'charged').read_text());reserve=sum(int(path.read_text()) for path in OUT.glob('reserve.*'))
                if active_s():budget=740000000
                else:budget=min(4800000000,24_500_000_000-12_350_000_000-int((OLD.parent/'m14r23/accounted.bytes').read_text())-450000000)
                if charged+reserve+SLOT<=budget:(OUT/f'reserve.{token}').write_text(str(SLOT));reserved=True
                else:reserved=False
            if reserved:newtask(token);break
            if charged+SLOT>budget and not active_s():print('RETAINED_GUARD',token,budget,charged,flush=True);return
            time.sleep(3+shard%3)


if __name__=='__main__':
    if sys.argv[1]=='bind':
        key=sys.argv[2]
        if key.startswith('e18_'):
            from hex18 import formula18
            formula18(key).write(Path('input.cnf'))
        else:physical(key).write(Path('input.cnf'))
    elif sys.argv[1]=='squarefree18':
        from hex18 import OUT as hexdir
        shard=int(sys.argv[2]);worker([line.split()[1] for line in (hexdir/'manifest.tsv').read_text().splitlines() if int(line.split()[0])==shard],shard)
    elif sys.argv[1]=='shard':
        from static23 import recover
        shard=int(sys.argv[2]);recover(shard);manifest=OUT/'manifest.tsv';worker([line.split()[1] for line in manifest.read_text().splitlines() if int(line.split()[0])==shard],shard)
    else:worker(sys.argv[2:])
