from collections import Counter
from itertools import chain,combinations
from pathlib import Path
import hashlib
import json
import os
import sys

from closure22 import Board,DECK,Cadical195,separate,task
from rebind import physical,controls
from m14core22 import BASE,hall_cards,rows


def data(key):
    letter,number=key.split('_');record=json.loads((BASE/'roster.jsonl').read_text().splitlines()[int(number)-1]);assert not record['hall'] and (letter=='D')==(record['kind']=='one')
    support=rows(record);hits=[1,1,2,2,2,2,2] if letter=='S' else [1,2,2,2,2,2,2];nr=sum(hits)-8;ranks=[2]*nr+[1]*(8-nr)
    assert len(support)==14 and [sum(mask>>pole&1 for mask in support) for pole in range(7)]==([6,4,4,4,4,4,4] if letter=='D' else [5,5,4,4,4,4,4])
    return support,hits,ranks


def rebound(key,cards):
    support,hits,ranks=data(key)
    return physical(support,[],ranks,hits,(5,6),(2,3),(6,7),64-17-sum(hits),14,9,map(int,cards.read_text().splitlines()))[:2]


def manifest():
    records=[json.loads(line) for line in (BASE/'roster.jsonl').read_text().splitlines()];keys=[]
    for number,record in enumerate(records,1):
        if not record['hall']:
            for letter in ('D' if record['kind']=='one' else 'SO'):keys.append(f'{letter}_{number}')
    ordered=sorted(keys,key=lambda key:(key[0]!='D',hashlib.sha256(key.encode()).digest()));assert len(ordered)==8233
    for number,key in enumerate(ordered):print(number%24,key,sep='\t')


if __name__=='__main__':
    action=sys.argv[1]
    if action=='manifest':manifest()
    elif action=='cal':controls()
    elif action=='discover':
        support,hits,ranks=data(sys.argv[2]);engine=Board(7,support,[-1]*8,9,3,(2,3),(2,3),14,17,ranks=ranks,poledegrees=hits,ordered=True)
        sys.exit(separate(engine,chain(hall_cards(support,7),map(int,DECK.read_text().splitlines()))))
    elif action=='bind':
        formula,count=rebound(sys.argv[2],Path('cards'));formula.to_file('input.cnf');print('rebound',count,formula.nv,len(formula.clauses))
    elif action=='task':task(sys.argv[2],[],120,180000000,BASE,__file__,13500000000)
    elif action=='worker':
        index=int(sys.argv[2]);assigned=[line.split()[1] for line in (BASE/'dispatch.tsv').read_text().splitlines() if int(line.split()[0])==index]
        for key in assigned:
            if (BASE/key).exists():continue
            task(key,[],120,120000000,BASE,__file__,13500000000,BASE/'lrat-trim')
            result=json.loads((BASE/key/'progress.json').read_text());
            if result['status']=='staging_guard':break
