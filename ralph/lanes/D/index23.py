import argparse
import hashlib
import json
import os
import sqlite3
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'scratch/D/m14r22';NEW=BASE.parent/'m14r23'; HARD=NEW/'hard'


def digest(path):
    checksum=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1048576),b''):checksum.update(block)
    return checksum.hexdigest()


def getrecord(folder,filename):
    path=folder/filename
    return json.loads(path.read_text()) if path.is_file() else {}


def receipt(record,folder,oldprefix,verify,cards):
    if record.get('status')!='dual_checked':return None
    stages=record['checks' if oldprefix else 'log'];assert all(stage['ok'] for stage in stages)
    names={stage['stage'] for stage in stages};assert {'check','cake','compress'}<=names and ('solve' in names or 'lift' in names and record.get('parent')) and ('roundtrip' in names or 'integrity' in names)
    for stem,marker in [('check','c VERIFIED'),('cake','s VERIFIED UNSAT')]:assert marker in (folder/(stem+'.log')).read_text().splitlines()
    files={name:(entry if oldprefix else (entry['sha256'],entry['size'])) for name,entry in record['files'].items()}
    for name,path in [('proof.zst',folder/'proof.zst'),('cards',cards)]:
        if not path.exists() or path.stat().st_size!=files[name][1]:return None
        if verify:assert digest(path)==files[name][0],path
    return [files[n][0] for n in ('input.cnf','proof.lrat','proof.zst','cards')]


def timecost(record):return sum(stage['cpu'] for stage in record.get('checks',record.get('log',[])))


def snapshot(dst=None,verify=False):
    keys=[line.split()[1] for line in (BASE/'manifest.tsv').read_text().splitlines()];assert len(set(keys))==len(keys)==8233
    stats=Counter();leaves=Counter();cost=Counter();rows=[];keysout=[];active=set();duplicates=[]
    for store in [BASE,NEW]:active.update(path.name[8:] for path in store.glob('reserve.*'))
    def leaf(key,head,status,hashes,folder):
        leaves[key[0],status]+=1;rows.append([key,str(head),status,*(hashes or ['-']*4),str(folder.relative_to(ROOT))])
    for key in keys:
        direct='unstarted';credit=False
        for place in [BASE,NEW]:
            folder=place/key
            if not folder.is_dir():continue
            found=getrecord(folder,'progress.json');direct=found.get('status','no_progress');cost[place.name]+=timecost(found)
            hashes=receipt(found,folder,False,verify,folder/'cards')
            if direct=='dual_checked' and not hashes:direct='archive_missing'
            if found:assert (found['host'],found['head'])==(key,[])
            if hashes:
                if credit:
                    assert credit==hashes,(key,credit,hashes);duplicates.append([key,str(folder.relative_to(ROOT)),*hashes]);continue
                credit=hashes;leaf(key,'root','cert',hashes,folder)
        decision='root_cert' if credit else direct
        if key in active and decision in ('unstarted','staging_guard','no_progress','open'):decision='running'
        for prefixplace in [BASE/'prefix',HARD]:
            inv=getrecord(prefixplace,key+'.json')
            if not inv:continue
            assert not credit and inv['key']==key and inv['heads'] and len(inv['heads'])==len(set(inv['heads']))
            covered=0
            for head in inv['heads']:
                folder=prefixplace/f'{key}-{head}';old=prefixplace!=HARD;record=getrecord(folder,'result.json' if old else 'progress.json');cards=BASE/key/'cards' if old else folder/'cards'
                if record:assert (record['key'],record['head'])==(key,head) if old else (record['host'],record['head'])==(f'{key}-{head}',[])
                cost['prefix']+=timecost(record)
                replacement=HARD/'lift'/f'{key}-{head}'
                if not old and (replacement/'progress.json').is_file():
                    assert record['status']!='dual_checked';folder=replacement;cards=folder/'cards';record=getrecord(folder,'progress.json');assert (record['host'],record['head'])==(f'{key}-{head}',[]);cost['lift']+=timecost(record)
                hashes=receipt(record,folder,old,verify,cards);result='cert' if hashes else record.get('status','pending')
                if not hashes and result=='dual_checked':result='archive_missing'
                covered+=bool(hashes);leaf(key,head,result,hashes,folder)
            decision='prefix_cert' if covered==len(inv['heads']) else 'prefix_partial'
        if not credit and decision not in ('prefix_cert','prefix_partial'):leaf(key,'root',decision,None,NEW/key if (NEW/key).is_dir() else BASE/key)
        stats[key[0],decision]+=1;keysout.append([key,direct,decision])
    assert sum(stats.values())==8233
    def plain(counts):return {f'{letter}:{name}':v for (letter,name),v in sorted(counts.items())}
    charged={};reserved={}
    for place in (BASE,NEW,HARD):
        if (place/'accounted.bytes').exists():
            charged[place.name]=int((place/'accounted.bytes').read_text() or 0);reserved[place.name]=sum(int(path.read_text() or 0) for path in place.glob('reserve.*') if path.exists())
    summary=dict(time=datetime.now().astimezone().isoformat(timespec='seconds'),key_counts=plain(stats),leaf_counts=plain(leaves),duplicates_not_counted=len(duplicates),stage_cpu_h={k:round(v/3600,6) for k,v in cost.items()},charged=charged,reserved=reserved,hashes_read=verify)
    if dst:
        dst.mkdir();
        for file,header,lines in [('keys.tsv',['key','direct','effective'],keysout),('leaves.tsv',['key','head','result','cnf_sha256','lrat_sha256','zst_sha256','cards_sha256','storage'],rows),('duplicates.tsv',['key','extra_storage','cnf_sha256','lrat_sha256','zst_sha256','cards_sha256'],duplicates),('open.tsv',['key','direct','effective'],[row for row in keysout if row[2] not in ('prefix_cert','root_cert')])]:
            (dst/file).write_text(''.join('\t'.join(row)+'\n' for row in [header,*lines]));os.chmod(dst/file,0o444)
        (dst/'summary.json').write_text(json.dumps(summary,sort_keys=True)+'\n');(dst/'SHA256SUMS').write_text(''.join(f'{digest(path)}  {path.name}\n' for path in sorted(dst.iterdir())));os.chmod(dst,0o555)
    print(json.dumps(summary,sort_keys=True),flush=True)
    return summary


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('dst',nargs='?',type=Path);parser.add_argument('--hash',action='store_true');parser.add_argument('--watch',action='store_true');args=parser.parse_args()
    if args.watch:
        while True:
            try:snapshot()
            except FileNotFoundError: snapshot()
            time.sleep(300-time.time()%300)
    else:snapshot(args.dst,args.hash)
