from collections import Counter
from itertools import combinations,combinations_with_replacement,product
from pathlib import Path
import json
import subprocess

from patch23 import ROOT,STORE,Cadical195
from shadow import decode,bits


def signature(rows):
    high=[site for site,word in enumerate(rows) if word.bit_count()==3];assert len(high)==2 and high[0]<8<=high[1] and all(2<=word.bit_count()<=3 for word in rows)
    assert all((rows[a]&rows[b]).bit_count()<=1 for a,b in combinations(range(16),2));remaining={(u,v) for u,v in combinations(range(16),2) if rows[u]>>v&1};walks=[];cycles=[]
    def walk(start,nxt,stop):
        last=start;step=1;remaining.remove(tuple(sorted((last,nxt))))
        while nxt not in stop:
            old=nxt;nxt,=bits(rows[nxt]&~(1<<last));last=old;remaining.remove(tuple(sorted((last,nxt))));step+=1
        return nxt,step
    for v in high:
        for n in bits(rows[v]):
            if tuple(sorted((n,v))) in remaining:
                end,length=walk(v,n,high);walks.append((v,end,length))
    while remaining:
        v,n=next(iter(remaining));_,length=walk(v,n,[v]);cycles.append(length)
    if all(a!=b for a,b,_ in walks):center=('theta',*sorted(k for a,b,k in walks))
    else:center=('barbell',next(k for a,b,k in walks if a==b==high[0]),next(k for a,b,k in walks if a!=b),next(k for a,b,k in walks if a==b==high[1]))
    return center,tuple(sorted(cycles))


def types():
    odd=range(1,18,2);even=range(6,18,2);out=set()
    for count in range(3):
        for cycles in combinations_with_replacement(even,count):
            for legs in combinations_with_replacement(odd,3):
                if sum(cycles)+sum(legs)==17 and legs[0]+legs[1]>=6:out.add((('theta',*legs),cycles))
            for left,bridge,right in product(even,odd,even):
                if sum(cycles)+left+bridge+right==17:out.add((('barbell',left,bridge,right),cycles))
    return out


def independent(graph,points,core,exterior,budget):
    demand=[9-(graph[v]&core).bit_count() for v in points];known=[-1 if graph[v]>>w&1 else (graph[v]&graph[w]&core).bit_count() for i,v in enumerate(points) for w in points[:i]];binary=STORE/'columns'
    inp=' '.join(map(str,[exterior,budget,*demand,*known]));result=subprocess.run([binary],input=inp,text=True,capture_output=True,check=True);raw=[tuple(map(int,line.split())) for line in result.stdout.splitlines()];assert len(raw)==len(set(raw));return set(raw)


def main():
    inputdata='5 0 1 1 1 1 1 1 '+' '.join(['2']*15);small=subprocess.run([STORE/'columns'],input=inputdata,text=True,capture_output=True,check=True);assert (0,0,0,0,63) in [tuple(map(int,line.split())) for line in small.stdout.splitlines()];seen={}
    for line in (STORE/'shapes.jsonl').read_text().splitlines():
        row=json.loads(line);wing=decode(row['g6']);number=row['shape'];sign=signature(wing);assert sign not in seen;seen[sign]=number
        graph=[*wing,0,0,0];
        for v in range(16):
            tip=16+(v>=8);graph[v]|=1<<tip;graph[tip]|=1<<v
        for tip in (16,17):graph[tip]|=1<<18;graph[18]|=1<<tip
        decks=independent(graph,row['pinned'],(1<<19)-1,21,1);source={tuple(json.loads(line)) for line in (STORE/f'decks{number}.jsonl').read_text().splitlines()};assert len(decks)==row['count'] and decks==source;print(number,sign,len(decks),'literal column match',flush=True)
    assert set(seen)==types() and len(seen)==15;print('exact theta/barbell plus even cycle type set; every holding deck matched independently')


if __name__=='__main__':main()
