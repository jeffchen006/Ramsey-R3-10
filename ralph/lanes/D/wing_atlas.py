"""Control matrices and raw 4x4 subbook dictionary for complete deficient wings."""
from collections import Counter
from itertools import combinations,permutations
from pathlib import Path
from book_strata import DEST,TYPES,OLD
from book_controls import bitset,sites,book,flags,graph_masks
from kernel_cnf import ROOT,decode
import json,sys


def raw(rows):return sum(word<<(4*idx) for idx,word in enumerate(rows))


def build():
    answers=[-1]*65536;perms=list(permutations(range(4)))
    for idx,typ in enumerate(TYPES):
        for direction in (typ,[bitset(point for point,word in enumerate(typ) if word>>site&1) for site in range(4)]):
            for order in perms:
                rows=[bitset(j for j,v in enumerate(order) if word>>v&1) for word in direction]
                for perm in perms:
                    key=raw([rows[i] for i in perm]);assert answers[key] in (-1,idx);answers[key]=idx
    assert sum(t>=0 for t in answers)==18474;(DEST/'dict.bin').write_bytes(bytes(t+1 for t in answers));bad={r['id'] for r in map(json.loads,(OLD/'single-types.jsonl').read_text().splitlines()) if r['general'] and r['status']=='excluded'};(DEST/'bad.in').write_text(' '.join(map(str,sorted(bad)))+'\n');plants=[]
    for idx,text in enumerate((ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines()):
        graph=graph_masks(text)
        if {word.bit_count() for word in graph}!={6} or max((a&b).bit_count() for a,b in combinations(graph,2))>3:continue
        for a,b in flags(graph):
            (h,*_), (lhs,rhs)=book(graph,(a,b));rows=[bitset(j for j,v in enumerate(rhs) if graph[u]>>v&1) for u in lhs];core=set(lhs)|set(rhs)|{a,b,h};y=[];z=[]
            for v in set(range(22))-core:
                mask=bitset(j for j,u in enumerate(lhs+rhs) if graph[v]>>u&1);(y if graph[h]>>v&1 else z).append(mask)
            plants.append(dict(host=idx,ends=[a,b],rows=rows,y=y,z=z))
    (DEST/'wing-cal.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in plants));print('wing matrices',len(plants),'dictionary',sum(t>=0 for t in answers),'forbidden general',bad)


def labelled(rows):
    width=len(rows);bits=[int(u<width<=v and rows[u]>>(v-width)&1) for v in range(2*width) for u in range(v)];bits.extend([0]*(-len(bits)%6));return chr(63+2*width)+''.join(chr(63+sum(bits[i+j]<<(5-j) for j in range(6))) for i in range(0,len(bits),6))


if __name__=='__main__':
    build();(DEST/'planted-wings.g6').write_text(''.join(labelled(r['rows'])+'\n' for r in map(json.loads,(DEST/'wing-cal.jsonl').read_text().splitlines())))
