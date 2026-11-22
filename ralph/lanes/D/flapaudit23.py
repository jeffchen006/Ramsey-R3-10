from collections import Counter
from itertools import combinations
from math import comb
from pathlib import Path
import json
import os
import sys
import tempfile

from closure22 import ROOT,digest,stage
from flap23 import WORK,SIDE,addcard,formula,masks
from hub23 import OUT,base


def alphabet():
    slots=masks();pairs=[(1<<left|1<<right,1 if (right-left)%2==0 else 3) for left,right in combinations(range(6),2) if right-left not in (1,5)];ans=[]
    for missing,triple,empty in [(0,0,1),(0,21,0),(0,42,0)]+[(mask,0,0) for mask,_ in pairs]:
        mult={mask:cap-int(mask==missing)-int(mask&triple==mask) for mask,cap in pairs};deck=[mask for mask,amount in mult.items() for _ in range(amount)]+[0]*empty+([triple] if triple else [])
        for site in range(6):deck.extend([1<<site]*((5 if site==0 else 6)-sum(mask>>site&1 for mask in deck)))
        ans.append(tuple(sorted(deck)))
    assert len(set(ans))==12 and set(ans)==set(map(tuple,slots));return slots


def coefficient(number,deck):
    groups=sorted(Counter(deck).items(),key=lambda item:(-item[1],item[0]));hist=Counter()
    def visit(i,left,counts,heads,weight):
        if i==len(groups):
            if not left and min(counts)>=1:hist[heads]+=weight
            return
        mask,mult=groups[i]
        for mark in range(min(mult,left)+1):
            new=[v+mark*((mask>>p)&1) for p,v in enumerate(counts)]
            if max(new)<=2:visit(i+1,left-mark,new,heads+(mark,) if i<2 else heads,weight*comb(mult,mark))
    visit(0,7,[0]*6,(),1);record={}
    for line in (OUT/f'cover{number}.tsv').read_text().splitlines():
        token,count,left,right=line.split();_,i,j=map(int,token.split('_'));assert int(left)==sum(1<<k for k,v in enumerate(deck) if v==groups[0][0]) and int(right)==sum(1<<k for k,v in enumerate(deck) if v==groups[1][0]);record[i,j]=int(count);assert hist[i,j]==int(count)
    assert len(record)==16 and len(hist)==9;print('count cells all',number,len(record),sum(hist.values()),flush=True);return [f'{number}_{i}_{j}' for (i,j),qty in record.items() if qty]


def replay(path,kind,number):
    row=json.loads((path/'progress.json').read_text());assert row['status']=='dual_checked';raw=set(map(int,(path/'cards').read_text().splitlines()));form=base(number,raw) if kind=='hub' else formula(int(number))
    if kind!='hub':
        for mask in sorted(raw):addcard(form,SIDE[:7],mask,10)
    form.write(Path('input.cnf'));files=row['files'];assert digest('input.cnf')==files['input.cnf']['sha256'] and digest(path/'cards')==files['cards']['sha256'];assert digest(path/'proof.zst')==files['proof.zst']['sha256']
    for name,cmd,marker in [('extract',['zstd','-f','-dq',path/'proof.zst','-o','proof.lrat'],None),('check',[ROOT/'opt/bin/lrat-check','input.cnf','proof.lrat'],'c VERIFIED'),('cake',[ROOT/'opt/bin/cake_lpr','--CML_HEAP_SIZE=256','--CML_STACK_SIZE=32','input.cnf','proof.lrat'],'s VERIFIED UNSAT')]:assert stage(name,cmd,120,100000000,0,marker)['ok'],(kind,number,name)
    assert digest('proof.lrat')==files['proof.lrat']['sha256'];print(kind,number,files['input.cnf']['sha256'],files['proof.lrat']['sha256'],'replayed',flush=True)


if __name__=='__main__':
    decks=alphabet();reflection=lambda mask:sum(1<<((-v)%6) for v in range(6) if mask>>v&1);assert sorted(map(reflection,decks[7]))==decks[4];print('slack-one alphabet all 12 exact; ordered-deck reflection 7 -> 4')
    directory=Path(sys.argv[1]).resolve();directory.mkdir();os.chdir(directory)
    for number in range(12):
        if number in (1,4):
            for token in coefficient(number,decks[number]):replay(OUT/token,'hub',token)
        elif number!=7:replay(WORK/str(number),'whole',str(number))
    Path('input.cnf').unlink();Path('proof.lrat').unlink()
