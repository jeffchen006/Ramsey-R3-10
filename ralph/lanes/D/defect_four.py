"""Incidence census on the endpoints of two disjoint singleton-codegree pairs."""

import argparse
from collections import Counter,defaultdict
from itertools import combinations,permutations
from pathlib import Path

from induced_pilot import ROOT,graph_key,line,mapping
from punct_path import decode,neighbors,pairs,profile_key


PAIR_SET={frozenset((0,1)),frozenset((2,3))}
PERMS=[perm for perm in permutations(range(4)) if {frozenset(perm[pos]for pos in part)for part in PAIR_SET}==PAIR_SET]
MAPS=[mapping(perm,16)for perm in PERMS]
CROSS=[(first,second)for first in (0,1)for second in (2,3)]


def census(order,degree):
    classes={};labelled=0
    for shape in range(16):
        edges={pair for rank,pair in enumerate(CROSS)if shape>>rank&1}
        def move(perm):return sum(1<<CROSS.index(tuple(sorted((perm[first],perm[second])))) for first,second in edges)
        orbit={move(perm)for perm in PERMS}
        if shape!=min(orbit):continue
        autom=[trans for trans,perm in zip(MAPS,PERMS)if move(perm)==shape]
        graph=neighbors(4,edges);room={};minimum={}
        for first,second in pairs(range(4)):
            if second in graph[first]:continue
            base=len(graph[first]&graph[second]);cap=1 if frozenset((first,second))in PAIR_SET else 3
            room[first,second]=cap-base;minimum[first,second]=max(0,1-base)
        if min(room.values())<0:continue
        moves=[]
        for size in (4,3,2):
            for part in combinations(range(4),size):
                subs=list(pairs(part))
                if all(room.get(pair,0)>0 for pair in subs):moves.append((sum(1<<pos for pos in part),part,subs))
        remain=[degree-len(row)for row in graph];table={};used=Counter();count=0;reps=set()
        def visit(index,slots):
            nonlocal count
            if index==len(moves):
                if sum(remain)>slots or any(used[pair]<limit for pair,limit in minimum.items()):return
                counts=Counter(table);counts[0]=slots-sum(remain)
                for point,val in enumerate(remain):counts[1<<point]=val
                key=profile_key(+counts);count+=1;reps.add(min(tuple(sorted((trans[mask],val)for mask,val in key))for trans in autom));return
            mask,part,subs=moves[index];limit=min([slots]+[remain[pos]for pos in part]+[room[pair]-used[pair]for pair in subs])
            for amount in range(limit+1):
                table[mask]=amount
                for pos in part:remain[pos]-=amount
                for pair in subs:used[pair]+=amount
                visit(index+1,slots-amount)
                for pos in part:remain[pos]+=amount
                for pair in subs:used[pair]-=amount
            del table[mask]
        visit(0,order-4);classes[shape]=reps;labelled+=count*len(orbit)
        assert count==sum(len({tuple(sorted((trans[mask],val)for mask,val in key))for trans in autom})for key in reps)
    return classes,labelled


def calibration(classes):
    physical=0;found=defaultdict(set)
    for code in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=neighbors(22,decode(code))
        if {len(row) for row in graph}!={6} or max(len(first&second)for first,second in pairs(graph))>3:continue
        low=[pair for pair in pairs(range(22))if len(graph[pair[0]]&graph[pair[1]])==1]
        for left,right in pairs(low):
            if set(left)&set(right):continue
            physical+=1;pins=left+right;allways=[]
            for perm in PERMS:
                order=[pins[pos]for pos in perm];shape=sum(1<<idx for idx,(first,second)in enumerate(CROSS)if order[first]in graph[order[second]]);allways.append((shape,graph_key(graph,order)))
            shape,key=min(allways);assert key in classes[shape];found[shape].add(key)
    print('C22 physical disjoint-pair marks',physical,'real by shape',{shape:len(keys)for shape,keys in sorted(found.items())})


def raw(shape,key):
    graph=[sum(1<<pos for pos in row)for row in neighbors(4,{pair for rank,pair in enumerate(CROSS)if shape>>rank&1})]
    for mask,size in key:
        for _ in range(size):
            index=len(graph);graph.append(mask)
            for pos in range(4):
                if mask>>pos&1:graph[pos]|=1<<index
    return ' '.join(map(str,(15,*graph)))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('dest',type=Path);args=parser.parse_args()
    for order,degree in ((22,6),(40,9)):
        classes,labelled=census(order,degree);print('order',order,'labelled',labelled,'profile reps',{shape:len(keys)for shape,keys in classes.items()})
        if order==22:calibration(classes)
        for shape,keys in classes.items():(args.dest/f'four-{order}-{shape}.in').write_text(''.join(raw(shape,key)+'\n'for key in sorted(keys)))
