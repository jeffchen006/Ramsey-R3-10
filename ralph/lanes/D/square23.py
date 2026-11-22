from collections import Counter
from itertools import combinations,product
from pathlib import Path
import json
import sys

from patch23 import ROOT,OLD,STORE,build,patch_data,census,Cadical195,task
from shadow import decode,bits

WORK=ROOT/'scratch/D/square18r23'


def squares(wing):
    return [tuple([left,right,*list(bits((wing[left]&wing[right])))]) for left,right in combinations(range(8),2) if (wing[left]&wing[right]).bit_count()==2]


def weakhex(wing):
    for selected in product(combinations(range(8),3),combinations(range(8,16),3)):
        points=selected[0]+selected[1]
        if sum(wing[v].bit_count() for v in points)>13:continue
        mask=sum(1<<v for v in points)
        if all((wing[v]&mask).bit_count()==2 for v in points):return True
    return False


def roster():
    counts=Counter();headers=[];dispatch=[]
    for number,line in enumerate((WORK/'raw.g6').read_text().splitlines(),1):
        wing=decode(line);assert len(wing)==16 and sum(row.bit_count() for row in wing)==36;counts['raw']+=1
        if any((a&b).bit_count()>2 for a,b in combinations(wing,2)):counts['pair_cap']+=1;continue
        marks=squares(wing)
        if not marks:counts['outside_square_sector']+=1;continue
        if any(sum(wing[v].bit_count() for v in square)<11 for square in marks):counts['D039']+=1;continue
        if weakhex(wing):counts['hex23']+=1;continue
        candidates=[]
        for square in marks:
            for left in set(range(8))-set(square):
                for right in set(range(8,16))-set(square):
                    points=sorted([*square,left,right]);rows,demand,bounds=patch_data(wing,[0]*8+[1]*8,points,9);slack=21+sum(hi for lo,hi in bounds.values())-sum(demand);candidates.append((slack,-sum(row.bit_count() for row in rows),points,square))
        slack,_,points,square=min(candidates);rows,demand,bounds=patch_data(wing,[0]*8+[1]*8,points,9);decks=[];census(rows,demand,bounds,21,1,lambda profile,leak:decks.append(sorted(mask for mask,qty in profile.items() for _ in range(qty))));assert len(set(map(tuple,decks)))==len(decks);counts['rostered']+=1;headers.append(dict(number=number,g6=line,pinned=points,square=square,count=len(decks),slack=slack));(WORK/f'decks{number}.jsonl').write_text(''.join(json.dumps(deck)+'\n' for deck in decks));dispatch.extend(f'{number}_{i}' for i in range(len(decks)))
    (WORK/'shapes.jsonl').write_text(''.join(json.dumps(row)+'\n' for row in headers));(WORK/'tokens').write_text(''.join(key+'\n' for key in dispatch));print(counts,'decks',len(dispatch),flush=True)


def formula(token):
    number,index=map(int,token.split('_'));spec=next(row for line in (WORK/'shapes.jsonl').read_text().splitlines() if (row:=json.loads(line))['number']==number);words=json.loads((WORK/f'decks{number}.jsonl').read_text().splitlines()[index]);return build(decode(spec['g6']),[0]*8+[1]*8,list(range(16)),spec['pinned'],words,45,9,True)


def calibration():
    from book_controls import flags,book,graph_masks,reorder,bitset
    count=square_count=0
    for line in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=graph_masks(line)
        if {v.bit_count() for v in graph}!={6} or max((a&b).bit_count() for a,b in combinations(graph,2))>3:continue
        for ends in flags(graph):
            (h,a,b),(left,right)=book(graph,ends);wing=left+right;outside=sorted(set(range(22))-{h,a,b}-set(wing));core=bitset([h,a,b,*wing]);outer=bitset(outside)
            for pp,qq in product(combinations(left,2),combinations(right,2)):
                points=pp+qq;mask=bitset(points)
                if not all((graph[p]&mask).bit_count()==2 for p in points):continue
                hits=[(graph[y]&mask).bit_count() for y in outside];assert max(hits)<=1;assert sum(hits)==sum(6-(graph[v]&core).bit_count() for v in points);square_count+=1
            count+=1
    assert count==125;print('C22',count,'planted flags, square footprints checked',square_count)


if __name__=='__main__':
    if sys.argv[1]=='roster':roster()
    elif sys.argv[1]=='cal':calibration()
    elif sys.argv[1]=='bind':formula(sys.argv[2]).write(Path('input.cnf'))
    elif sys.argv[1]=='discover':Path('cards').write_text('')
    elif sys.argv[1]=='work':
        for token in sys.argv[2:]:
            if not (WORK/token).exists():task(token,[],20,45000000,WORK,str(Path(__file__).resolve()),390000000,OLD/'lrat-trim')
