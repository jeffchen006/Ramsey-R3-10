import argparse
from itertools import combinations
import json
import os
from pathlib import Path
import tempfile

from closure22 import ROOT, digest, stage
from rebind import physical

BASE=ROOT/'scratch/D/m14r22'


def rebuild(key,head,cards):
    kind,number=key.split('_');record=json.loads((BASE/'roster.jsonl').read_text().splitlines()[int(number)-1]); assert record['kind']==('one' if kind=='D' else 'two') and not record['hall']
    pairs=[sum(2**site for site in pair) for pair in combinations(range(7),2)];sites=[*record['triples'],*[mask for mask,amount in zip(pairs,record['pairs']) for _ in range(amount)]]
    exceptional=[0,1] if kind=='S' else [0];pole_degrees=[2-(pole in exceptional) for pole in range(7)]
    ranks=sorted([1]*(16-sum(pole_degrees))+[2]*(sum(pole_degrees)-8),reverse=True);edge_total=8*8-17-sum(ranks)
    formula,count,_=physical(sites,head,ranks,pole_degrees,(5,6),(2,3),(6,7),edge_total,14,9,map(int,cards.read_text().splitlines()));return formula,count


def replay(key,head,work):
    sub=BASE/key if not head else BASE/'prefix'/f'{key}-{head[0]}';record=json.loads((sub/('progress.json' if not head else 'result.json')).read_text());assert record['status']=='dual_checked';cards=BASE/key/'cards'
    if head:assert record['key']==key and record['head']==head[0]
    else:assert record['host']==key and not record['head']
    with tempfile.TemporaryDirectory(dir=work) as staging:
        os.chdir(staging);formula,count=rebuild(key,head,cards);formula.to_file('input.cnf')
        for name,command,limit,marker in [('extract',['zstd','-dq',sub/'proof.zst','-o','proof.lrat'],120000000,None),('check',[ROOT/'opt/bin/lrat-check','input.cnf','proof.lrat'],8000000,'c VERIFIED'),('cake',[ROOT/'opt/bin/cake_lpr','--CML_HEAP_SIZE=256','--CML_STACK_SIZE=32','input.cnf','proof.lrat'],8000000,'s VERIFIED UNSAT')]:
            result=stage(name,command,180,limit,0,marker);assert result['ok'],(key,head,result)
        for name,path in [('cards',cards),('input.cnf',Path('input.cnf')),('proof.lrat',Path('proof.lrat')),('proof.zst',sub/'proof.zst')]:
            value=record['files'][name];expected=value[0] if head else value['sha256'];assert digest(path)==expected
        print(key,head,count,'dual_replayed',flush=True);os.chdir(work)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('staging',type=Path);parser.add_argument('keys',nargs='+');args=parser.parse_args();work=args.staging.resolve();work.mkdir(exist_ok=True)
    for key in args.keys:
        prefix=BASE/'prefix'/(key+'.json')
        if not prefix.exists():replay(key,[],work);continue
        from prefix22 import inventory
        regenerated=json.loads(json.dumps(inventory(key)));assert regenerated==json.loads(prefix.read_text());assert len(regenerated['heads'])==len(set(regenerated['heads']))
        for head in regenerated['heads']:replay(key,[head],work)
