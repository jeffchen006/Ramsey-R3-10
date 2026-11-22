"""Freeze the six middle-star shards and pack ordinary, dual-checked certificates."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import traceback
from zipfile import ZipFile, ZIP_DEFLATED

from middle16_price import BIN, ROOT, cpu, digest, fixedstars, target

DATA = ROOT / 'scratch/D/middle17'
FROZEN = DATA / 'frozen'
HOSTS = (17, 18, 19, 26, 31, 32)
CHECKS = (('cake_lpr', 0, 's VERIFIED UNSAT'), ('lrat-check', 0, 'c VERIFIED'))


def compact(obj):
    return json.dumps(obj, separators=(',', ':'), sort_keys=True)


def rows(path):
    return list(map(json.loads, path.read_bytes().splitlines()))


def tag(rec):
    return f"{rec['host']}-{rec['id']}"


def freeze():
    FROZEN.mkdir()
    prior = {tag(rec) for rec in rows(DATA/'prior.jsonl')}
    roster = rows(DATA/'roster.jsonl')
    assert len(set(map(tag, roster))) == len(roster) == 15282
    for host in HOSTS:
        shard = [rec for rec in roster if rec['host']==host]
        ranked = sorted(shard, key=lambda rec: (tag(rec) not in prior, digest(('D17-sample:'+tag(rec)).encode())))
        assert len([rec for rec in ranked[:64] if tag(rec) in prior]) == 12
        assignment = {row['id']:(index%4, 'checkpoint' if index<64 else 'rest', index) for index,row in enumerate(ranked)}
        enriched = [dict(rec,worker=assignment[rec['id']][0],phase=assignment[rec['id']][1],rank=assignment[rec['id']][2]) for rec in shard]
        path = FROZEN / f'{host}.jsonl'
        path.write_text(''.join(compact(rec)+'\n' for rec in enriched)); path.chmod(0o444)
    manifest = FROZEN/'SHA256SUMS'
    manifest.write_text(''.join(f'{digest(path.read_bytes())}  {path.name}\n' for path in sorted(FROZEN.glob('*.jsonl')))); manifest.chmod(0o444)


def read_frozen():
    result = []
    for line in (FROZEN/'SHA256SUMS').read_text().splitlines():
        expected, name = line.split(); path = FROZEN/name
        assert digest(path.read_bytes())==expected
        result.extend(rows(path))
    assert len(result)==15282 and sum(rec['weight'] for rec in result)==320878
    return result


def scheduled(phase, worker):
    return sorted((rec for rec in read_frozen() if rec['phase']==phase and rec['worker']==worker), key=lambda rec:(rec['rank'], rec['host']))


def checked(tool, rc, marker, args, allowance):
    assert allowance>0
    proc = subprocess.run(['timeout','24','prlimit',f'--cpu={max(1,int(allowance))}:{max(1,int(allowance))+1}','--fsize=16777216:16777216','--',BIN/tool,*args],stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    if proc.returncode!=rc or marker.encode() not in proc.stdout.splitlines():
        raise RuntimeError((tool,proc.returncode,marker,proc.stdout[-1000:]))
    return [tool,proc.returncode,marker]


def produce(rec, work, pack):
    start=cpu(); key=tag(rec)
    first=work/'producer.cnf'; second=work/'independent.cnf'; proof=work/'proof.lrat'
    assert not proof.exists()
    word=rec['word']; fixedstars.run([rec['Y'],fixedstars.fromprofile(*word[:2]),fixedstars.fromprofile(*word[2:])],7,17,9,16,1,rules=1,export=first)
    target(rec,second); data=first.read_bytes(); assert data==second.read_bytes(),key
    receipts=[checked('cadical',20,'s UNSATISFIABLE',['--lrat','--no-binary',first,proof],10-(cpu()-start))]
    for tool,rc,marker in CHECKS:
        receipts.append(checked(tool,rc,marker,[second,proof],10-(cpu()-start)))
    raw=proof.read_bytes(); assert raw
    for ext,payload in [('cnf',data),('lrat',raw)]:pack.writestr(key+'.'+ext,payload)
    result=dict(key=key,weight=rec['weight'],receipts=receipts,cnf=digest(data),lrat=digest(raw),physical=digest(compact(rec).encode()),zbytes=sum(pack.getinfo(key+'.'+ext).compress_size for ext in ['cnf','lrat']),cnf_bytes=len(data),proof_bytes=len(raw))
    for path in (first,second,proof):path.unlink()
    result['cpu']=cpu()-start; assert result['cpu']<10
    pack.writestr(key+'.json',compact(result)); return result


def worker(phase,number):
    planned=scheduled(phase,number)
    work=DATA/f'{phase}-{number}'; work.mkdir()
    staged=0
    if phase=='rest':
        assert (DATA/'APPROVE').read_text().strip()==digest((FROZEN/'SHA256SUMS').read_bytes())
        staged=sum(path.stat().st_size for path in (DATA/f'checkpoint-{number}').glob('batch*.zip'))
    for offset in range(0,len(planned),24):
        assert not (DATA/'STOP').exists()
        packpath=work/f'batch{offset:04d}.zip'; group=planned[offset:offset+24]
        with ZipFile(packpath,'x',compression=ZIP_DEFLATED,compresslevel=1) as pack:
            for rec in group:
                assert not (DATA/'STOP').exists() and staged+pack.fp.tell()<600*2**20
                assert cpu()< (135 if phase=='checkpoint' else 3320)
                print('produce',tag(rec),flush=True); produce(rec,work,pack)
        staged+=packpath.stat().st_size
        subprocess.run([sys.executable,'-B',Path(__file__).with_name('middle17_recheck.py'),str(packpath),phase,str(number),str(offset)],check=True)
        print('batch',offset,'worker_cpu',cpu(),'archive_cumulative',staged,flush=True)
    (work/'done').write_text(compact({'count':len(planned),'worker_cpu':cpu(),'archive_cumulative':staged})+'\n')


if __name__=='__main__':
    if sys.argv[1:] == ['freeze']:freeze()
    else:
        assert sys.argv[1] in ('checkpoint','rest') and int(sys.argv[2]) in range(4)
        try:worker(sys.argv[1],int(sys.argv[2]))
        except BaseException:
            (DATA/'STOP').touch(); traceback.print_exc(); raise
