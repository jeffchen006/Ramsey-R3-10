from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import sys

BASE=Path(__file__).resolve().parents[3]/'scratch/D/m14r22'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze(directory):
    with (directory/'status.tsv').open() as stream:status=list(csv.DictReader(stream,delimiter='\t'))
    counts=Counter();sizes=Counter();seen=set()
    with (directory/'receipt-index.tsv').open('x') as output:
        output.write('key\thead\tprogress_sha256\tcards_sha256\tcnf_sha256\traw_lrat_sha256\tcompressed_sha256\tbytes\n')
        for row in status:
            key=row['key'];assert key not in seen;seen.add(key);counts[key[0],row['effective']]+=1
            if row['effective'] not in ('dual_checked','prefix_complete'):continue
            heads=json.loads((BASE/'prefix'/(key+'.json')).read_text())['heads'] if row['effective']=='prefix_complete' else [None]
            for head in heads:
                path=BASE/key/'progress.json' if head is None else BASE/'prefix'/f'{key}-{head}'/'result.json';receipt=json.loads(path.read_text());assert receipt['status']=='dual_checked'
                if head is None:assert receipt['host']==key and receipt['head']==[];stages=receipt['log']
                else:assert receipt['key']==key and receipt['head']==head;stages=receipt['checks']
                assert all(item['ok'] for item in stages) and {item['stage'] for item in stages}>={'check','cake','solve','bind','compress'}
                files=receipt['files'];fingerprints=[files[name][0] if head is not None else files[name]['sha256'] for name in ['cards','input.cnf','proof.lrat','proof.zst']];amount=files['proof.zst'][1] if head is not None else files['proof.zst']['size'];assert (path.parent/'proof.zst').stat().st_size==amount
                sizes[key[0]]+=amount;output.write('\t'.join(map(str,[key,'-' if head is None else head,digest(path),*fingerprints,amount]))+'\n')
    assert len(seen)==8233;print('frozen effective statuses',dict(sorted(counts.items())),'compressed bytes by branch',dict(sorted(sizes.items())))


if __name__=='__main__':freeze((BASE/sys.argv[1]).resolve())
