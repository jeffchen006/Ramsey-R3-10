from collections import Counter
from itertools import combinations,permutations
import json
import sys

import pynauty
from square23 import WORK,STORE,decode,bits
from wingaudit23 import independent


def signature(rows):
    return pynauty.certificate(pynauty.Graph(16,False,{v:list(bits(row)) for v,row in enumerate(rows)},[set(range(8)),set(range(8,16))]))


def components():
    domain=[('P',length,color) for length in range(1,6) for color in ([0] if length%2 else [0,1])]+[('C',4,0)]
    def visit(start,used,edges,counts,acc):
        if used==[8,8]:
            if edges==10 and counts==[2,2]:yield acc
            return
        for index in range(start,len(domain)):
            kind,length,color=domain[index];colors=[(color+i)%2 for i in range(length+(kind=='P'))];twos=colors if kind=='C' else colors[1:-1];vertices=[used[i]+colors.count(i) for i in [0,1]];degrees=[counts[i]+twos.count(i) for i in [0,1]]
            if max(vertices)<=8 and max(degrees)<=2 and edges+length<=10:yield from visit(index,vertices,edges+length,degrees,[*acc,domain[index]])
    return visit(0,[0,0],0,[0,0],[])


def audit():
    raw=[decode(row) for row in (WORK/'raw.g6').read_text().splitlines()];known={signature(rows) for rows in raw};assert len(known)==len(raw)==516;found=set();total=0;genera=0
    for component in components():
        rows=[0]*16;used=[0,8];genera+=1
        for kind,length,color in component:
            path=[]
            for j in range(length+(kind=='P')):
                side=(color+j)%2;path.append(used[side]);used[side]+=1
            if kind=='C':path.append(path[0])
            for u,v in zip(path,path[1:]):rows[u]|=1<<v;rows[v]|=1<<u
        for perm in permutations(range(8,16)):
            if any(rows[u]>>v&1 for u,v in enumerate(perm)):continue
            full=rows.copy()
            for u,v in enumerate(perm):full[u]|=1<<v;full[v]|=1<<u
            if any((u&v).bit_count()>2 for u,v in combinations(full,2)):continue
            found.add(signature(full));total+=1
    admissible={signature(row) for row in raw if all((u&v).bit_count()<=2 for u,v in combinations(row,2))};assert found<=admissible
    print('matching-deletion types',genera,'labelled disjoint matchings',total,'admissible genbg',len(admissible),'cover with perfect matching',len(found),'extra genbg',len(admissible-found),flush=True)
    total=0;zeros=0
    for line in (WORK/'shapes.jsonl').read_text().splitlines():
        row=json.loads(line);wing=decode(row['g6']);graph=[*wing,0,0,0];square=row['square'];assert all(sum((wing[v]>>w)&1 for w in square)==2 for v in square)
        for v in range(16):
            tip=16+(v>=8);graph[v]|=1<<tip;graph[tip]|=1<<v
        for tip in (16,17):graph[tip]|=1<<18;graph[18]|=1<<tip
        checked=independent(graph,row['pinned'],(1<<19)-1,21,1);actual={tuple(json.loads(row)) for row in (WORK/f'decks{row["number"]}.jsonl').read_text().splitlines()};assert actual==checked and len(actual)==row['count'];total+=len(actual);zeros+=not actual
    print('32 square roots all independent column counts agree,',zeros,'zero roots,',total,'decks',flush=True)


if __name__=='__main__':audit()
