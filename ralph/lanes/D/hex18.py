from collections import Counter
from itertools import combinations,product
from pathlib import Path
import hashlib
import json
import sys

from square23 import WORK,STORE,decode,squares,patch_data,census,build
from wingaudit23 import independent

OUT=WORK/'hex'


def census18():
    counts=Counter();specs=[];tokens=[]
    for number,line in enumerate((WORK/'raw.g6').read_text().splitlines(),1):
        wing=decode(line)
        if any((a&b).bit_count()>2 for a,b in combinations(wing,2)) or squares(wing):continue
        counts['no_square']+=1;options=[]
        for left,right in product(combinations(range(8),3),combinations(range(8,16),3)):
            points=left+right;loss=sum(wing[v].bit_count() for v in points)-12
            if loss>2:continue
            mask=sum(1<<v for v in points)
            if all((wing[v]&mask).bit_count()==2 for v in points):options.append((loss,points))
        if not options:counts['outside']+=1;continue
        loss,points=min(options)
        if loss<2:counts['old_hex_exclusion']+=1;continue
        rows,demand,bounds=patch_data(wing,[0]*8+[1]*8,points,9);decks=[];census(rows,demand,bounds,21,1,lambda profile,leak:decks.append(sorted(mask for mask,n in profile.items() for _ in range(n))));graph=[*wing,1<<18,1<<18,(1<<16)|(1<<17)]
        for v in range(16):
            tip=16+(v>=8);graph[v]|=1<<tip;graph[tip]|=1<<v
        assert independent(graph,points,(1<<19)-1,21,1)==set(map(tuple,decks)) and len(decks)==len(set(map(tuple,decks)))
        counts['covered_shape']+=1;specs.append(dict(g6=line,number=number,pinned=points,count=len(decks)));(OUT/f'decks{number}.jsonl').write_text(''.join(json.dumps(deck)+'\n' for deck in decks));tokens.extend(f'e18_{number}_{i}' for i in range(len(decks)))
    (OUT/'spec.jsonl').write_text(''.join(json.dumps(spec)+'\n' for spec in specs));tokens.sort(key=lambda token:hashlib.sha256(token.encode()).digest());(OUT/'manifest.tsv').write_text(''.join(f'{i%28}\t{key}\n' for i,key in enumerate(tokens)));print(counts,'exact joined decks',len(tokens))


def formula18(key):
    tag,number,idx=key.split('_');assert tag=='e18';row=next(row for line in (OUT/'spec.jsonl').read_text().splitlines() if (row:=json.loads(line))['number']==int(number));deck=json.loads((OUT/f'decks{number}.jsonl').read_text().splitlines()[int(idx)]);return build(decode(row['g6']),[0]*8+[1]*8,list(range(16)),row['pinned'],deck,45,9,True)


if __name__=='__main__':census18()
