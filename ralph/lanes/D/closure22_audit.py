import argparse
import collections
import csv
import json
import os
import shutil
import tempfile
from pathlib import Path

from closure22 import ROOT, STORE, board, digest, stage


def audit(host, work, recover=False):
    source=STORE/str(host); record=json.loads((source/'progress.json').read_text()); assert record['head']==[] and record['host']==host
    proof=STORE/'control/896.zst' if recover else source/'proof.zst'
    if not recover: assert record['status']=='dual_checked'
    with tempfile.TemporaryDirectory(dir=work) as directory:
        os.chdir(directory)
        formula,count=board(host,[],source/'cards');formula.to_file('input.cnf')
        results=[]
        for name,command,cap,limit,marker in [
            ('extract',['zstd','-dq',proof,'-o','proof.lrat'],100,260000000,None),
            ('check',[ROOT/'opt/bin/lrat-check','input.cnf','proof.lrat'],180,8000000,'c VERIFIED'),
            ('cake',[ROOT/'opt/bin/cake_lpr','--CML_HEAP_SIZE=256','--CML_STACK_SIZE=32','input.cnf','proof.lrat'],180,8000000,'s VERIFIED UNSAT')]:
            result=stage(name,command,cap,limit,0,marker);results.append(result);assert result['ok'],(host,name,result)
        files={name:{'sha256':digest(path),'size':path.stat().st_size} for name,path in [('cards',source/'cards'),('input.cnf',Path('input.cnf')),('proof.lrat',Path('proof.lrat')),('proof.zst',proof)]}
        if recover:
            assert host==896 and record['status']=='open' and all(item['ok'] for item in record['log']) and len(record['log'])==7
            record.update(status='dual_checked',files=files,packaging_replay=results);shutil.copyfile(proof,source/'proof.zst');assert digest(source/'proof.zst')==files['proof.zst']['sha256'];(source/'progress.json').write_text(json.dumps(record,sort_keys=True)+'\n');proof.unlink()
        else: assert files==record['files']
        os.chdir(work)
    print(json.dumps(dict(host=host,count=count,results=results,cnf=files['input.cnf']['sha256'])),flush=True)


def coverage():
    with (ROOT/'scratch/D/wing21/counts.tsv').open() as stream: old={int(row['row']):row for row in csv.DictReader(stream,delimiter='\t')}
    with (ROOT/'scratch/D/wing20/counts.tsv').open() as stream: earlier={int(row['row']):row for row in csv.DictReader(stream,delimiter='\t')}
    assert len(earlier)==162 and len(old)==159
    manifest=[int(line.split()[1]) for line in (STORE/'manifest.tsv').read_text().splitlines()];assert len(manifest)==len(set(manifest))==149
    assert set(manifest)=={host for host,row in old.items() if int(row['identity'])>0}-{404}
    total=collections.Counter();groups=collections.defaultdict(list)
    for host,row in sorted(earlier.items()):
        if host not in old: assert int(row['identity'])==0;key='D048'
        elif not int(old[host]['identity']):key='D050'
        elif host==404:key='R007'
        else:
            location=STORE/str(host)/'progress.json'
            key=json.loads(location.read_text())['status'] if location.exists() else 'missing'
        groups[key].append(host)
        if host in manifest:
            for field in ['identity','orbits']:total[(key,field)]+=int(old[host][field])
            group=int(old[host]['group']);fixed=[int(term.split(':')[1]) for term in old[host]['fixed'].split(',')];assert len(fixed)==group and sum(fixed)==group*int(old[host]['orbits']) and fixed[0]==int(old[host]['identity'])
    for key,hosts in groups.items(): print(key,len(hosts),total[key,'identity'],total[key,'orbits'],','.join(map(str,hosts)))


if __name__=='__main__':
    args=argparse.ArgumentParser();args.add_argument('work',type=Path,nargs='?');args.add_argument('hosts',type=int,nargs='*');args.add_argument('--recover',action='store_true');option=args.parse_args()
    if not option.work:coverage()
    else:
        dest=option.work.resolve();dest.mkdir(exist_ok=True)
        for host in option.hosts:audit(host,dest,option.recover)
