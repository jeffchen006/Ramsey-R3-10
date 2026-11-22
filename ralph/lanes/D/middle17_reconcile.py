"""Reconcile physical roster, assignment, production and second verification receipts."""
import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
from pathlib import Path
from zipfile import ZipFile


def read(path):return list(map(json.loads,path.read_bytes().splitlines()))


def sha(data):return sha256(data).hexdigest()


def canonical(obj):return json.dumps(obj,sort_keys=True,separators=(',',':')).encode()


def run(data,dest,require_full):
    dest.mkdir(exist_ok=True,parents=True)
    source={(row['host'],row['id']):row for row in read(data/'roster.jsonl')}
    assert len(source)==15282
    frozen={}; assignment=defaultdict(list); archive_names=set(); sizes=Counter(); times=Counter(); hashes=[]
    sha_list=(data/'frozen/SHA256SUMS').read_text().splitlines(); assert len(sha_list)==6
    for line in sha_list:
        expected,name=line.split(); file=data/'frozen'/name; assert sha(file.read_bytes())==expected
        for row in read(file):
            key=(row['host'],row['id']); assert key not in frozen and key in source and row['host']==int(file.stem)
            assert source[key]=={field:value for field,value in row.items() if field not in ('worker','phase','rank')}
            frozen[key]=row; assignment[row['phase'],row['worker']].append(key)
    assert frozen.keys()==source.keys() and len(assignment)==8
    cake=['cake_lpr',0,'s VERIFIED UNSAT']; lrat=['lrat-check',0,'c VERIFIED']; cadical=['cadical',20,'s UNSATISFIABLE']
    complete={}; upper=0; largest=None
    for (phase,worker),entries in sorted(assignment.items()):
        entries.sort(key=lambda key:(frozen[key]['rank'],key[0])); directory=data/f'{phase}-{worker}'
        for offset in range(0,len(entries),24):
            packfile=directory/f'batch{offset:04d}.zip'; ok=packfile.with_suffix('.ok')
            if not ok.exists():continue
            group=entries[offset:offset+24]; receipts=read(ok); assert len(receipts)==len(group)
            with ZipFile(packfile) as book:
                expected=[f'{host}-{index}.{ext}' for host,index in group for ext in ['cnf','lrat','json']]
                assert expected==book.namelist()
                for key,rep in zip(group,receipts):
                    name='-'.join(map(str,key)); assert rep['key']==name and key not in complete
                    prod=json.loads(book.read(name+'.json'))
                    assert prod['key']==name and rep['physical']==prod['physical']==sha(canonical(frozen[key]))
                    assert rep['weight']==prod['weight']==source[key]['weight']
                    assert prod['receipts']==[cadical,cake,lrat] and rep['receipts']==[lrat,cake]
                    for ext,field in [('cnf','cnf_bytes'),('lrat','proof_bytes')]:
                        content=book.read(name+'.'+ext)
                        assert len(content)==prod[field] and sha(content)==prod[ext]==rep[ext]
                        sizes[ext]+=len(content)
                    used=rep['production']+rep['replay']; assert rep['production']==prod['cpu'] and 0<used<10
                    if used>upper:upper,largest=used,name
                    for field in ['production','replay']:times[field]+=rep[field]
                    complete[key]=(rep['weight'],rep['cnf'],rep['lrat'],packfile.relative_to(data))
            archive_names.add(packfile); sizes['packed']+=packfile.stat().st_size
            for file in [packfile,ok]:hashes.append(f'{sha(file.read_bytes())}  {file.relative_to(data)}\n')
    if require_full:
        assert complete.keys()==source.keys() and not (data/'STOP').exists()
        assert archive_names==set(data.glob('rest-*/batch*.zip'))|set(data.glob('checkpoint-*/batch*.zip'))
        assert all((data/f'{phase}-{worker}/done').exists() for phase,worker in assignment)
    with (dest/'complete.tsv').open('w') as out:
        for key in sorted(complete):print(*key,*complete[key],sep='\t',file=out)
    with (dest/'open.tsv').open('w') as out:
        for key in sorted(source.keys()-complete.keys()):print(*key,source[key]['weight'],sep='\t',file=out)
    (dest/'archives.sha256').write_text(''.join(sorted(hashes)))
    stats=Counter()
    for key in sorted(source):stats[key[0],key in complete,'ids']+=1; stats[key[0],key in complete,'weight']+=source[key]['weight']
    for host in sorted({key[0] for key in source}):print('host',host,'completed',stats[host,True,'ids'],stats[host,True,'weight'],'open',stats[host,False,'ids'],stats[host,False,'weight'])
    print('completed IDs / weight',len(complete),sum(value[0] for value in complete.values()),'of',len(source),sum(row['weight'] for row in source.values()))
    print('archives',len(archive_names),'bytes',dict(sizes),'direct CPU seconds',dict(times),'max combined CPU',upper,largest)
    print('PASS: full marked roster' if require_full else 'Partial: only listed double-verified IDs count')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('data',type=Path);parser.add_argument('dest',type=Path);parser.add_argument('--full',action='store_true');args=parser.parse_args()
    run(args.data,args.dest,args.full)
