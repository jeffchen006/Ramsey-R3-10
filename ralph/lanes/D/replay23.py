import argparse
import csv
from itertools import combinations
import json
import os
from pathlib import Path
import tempfile

from closure22 import ROOT,stage,digest
from m14replay22 import BASE,physical,rebuild
from pysat.card import CardEnc
from pysat.formula import IDPool


def rebuild_join(key,head,cards,reverse):
    kind,number=key.split('_');assert kind in ('O','S');record=json.loads((BASE/'roster.jsonl').read_text().splitlines()[int(number)-1]);rows=record['triples']+[1<<a|1<<b for (a,b),mult in zip(combinations(range(7),2),record['pairs']) for _ in range(mult)];assert len(rows)==14
    raw=list(map(int,cards.read_text().splitlines()));parts=[];directions=(1,0) if reverse else (0,1)
    for side in directions:
        deficit=({0,1} if kind=='S' else {0}) if side==0 else (set() if kind=='S' else {1});margin=[2-int(i in deficit) for i in range(7)];doubles=sum(margin)-8;ranks=[2]*doubles+[1]*(8-doubles);deck=[abs(mask) for mask in raw if (mask<0)==bool(side)]
        cnf,count,var=physical(rows,head if not side else [],ranks,margin,(5,6),(2,3),(6,7),47-sum(margin),14,9,deck);parts.append((cnf,var))
    (first,edge0),(second,edge1)=parts;offset=first.nv;shares={edge1(i,j):edge0(i,j) for i,j in combinations(range(21),2)};lookup=lambda var:shares[var] if var in shares else offset+var
    for clause in second.clauses:first.append([lookup(lit) if lit>0 else -lookup(-lit) for lit in clause]);
    pool=IDPool(start_from=offset+second.nv+1)
    for y in range(7,21):
        neighbors=[edge0(y,z) for z in range(7,21) if y!=z]+[edge0(y,z) for z in range(21,29)]+[lookup(edge1(y,z)) for z in range(21,29)];first.extend(CardEnc.equals(neighbors,bound=9-rows[y-7].bit_count(),vpool=pool).clauses)
    return first


def replay(row,work):
    key=row['key'];head=[] if row['head']=='root' else [int(row['head'])];source=ROOT/row['storage'];cards=source/'cards';
    if not cards.is_file():cards=BASE/key/'cards'
    assert digest(cards)==row['cards_sha256'] and digest(source/'proof.zst')==row['zst_sha256']
    raw=cards.read_text().splitlines();formula=rebuild_join(key,head,cards,source.parent.name=='lift') if any(line.startswith('-') for line in raw) else rebuild(key,head,cards)[0]
    with tempfile.TemporaryDirectory(dir=work) as stage_dir:
        os.chdir(stage_dir);formula.to_file('formula.cnf');assert digest('formula.cnf')==row['cnf_sha256'],(key,head)
        for tag,cmd,marker in [('extract',['zstd','-dq',source/'proof.zst','-o','proof.lrat'],None),('check',[ROOT/'opt/bin/lrat-check','formula.cnf','proof.lrat'],'c VERIFIED'),('cake',[ROOT/'opt/bin/cake_lpr','--CML_HEAP_SIZE=256','--CML_STACK_SIZE=32','formula.cnf','proof.lrat'],'s VERIFIED UNSAT')]:
            assert stage(tag,cmd,180,150000000,0,marker)['ok'],(key,head,tag)
        assert digest('proof.lrat')==row['lrat_sha256'];os.chdir(work);print(key,head,'rebound and dual replayed',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('index',type=Path);parser.add_argument('work',type=Path);parser.add_argument('keys',nargs='*');args=parser.parse_args();work=args.work.resolve();work.mkdir();keys=set(args.keys);rows=list(csv.DictReader((args.index/'leaves.tsv').open(),delimiter='\t'));seen=set()
    for row in rows:
        if keys and row['key'] not in keys:continue
        assert row['result']=='cert',(row['key'],row['result']);replay(row,work);seen.add(row['key'])
    assert not keys or seen==keys
