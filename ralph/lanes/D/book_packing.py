"""Disjoint matched-petal quotas by allocating physical vertices to two books."""
from collections import Counter
from functools import lru_cache
from itertools import combinations,product
from pathlib import Path
import json
import sys
from book_controls import bitset,book,sites


def subsets(word):
    result=word
    while True:
        yield result
        if not result:break
        result=(result-1)&word


def grammar(frame):
    fixed,*rows=frame;degree=rows[0].bit_count();paths=[];wings=[]
    for ends in ((0,1),(2,3)):
        path,groups=book(rows,ends);paths.append(bitset(path));wings.append([bitset(side) for side in groups])
    marked=paths[0]|paths[1];assert marked.bit_count()==6
    union=[(left|right)&~marked for left,right in wings];overlap=union[0]&union[1]
    seeds=[]
    for subset in subsets(marked):
        free=0
        for point in sites(subset):
            if not fixed>>point&1:free |= bitset(other for other in range(len(rows)) if other!=point and not fixed>>other&1 and not rows[point]&rows[other]&fixed)
            free |= rows[point]
        if not(subset&free):seeds.append((subset,(~free)&~marked))
    return rows,paths,wings,union,overlap,seeds


def allocation(frame):
    rows,paths,wings,union,overlap,seeds=grammar(frame);degree=rows[0].bit_count()
    def guaranteed(side,active):
        score=0
        for seed,allowed in seeds:
            use=active&allowed
            score=max(score,use.bit_count()+seed.bit_count()-degree)
        return score
    result=Counter();example={};witnesses=[]
    for shared in subsets(overlap):
        left=union[0]&~(overlap^shared);right=union[1]&~shared
        bounds=(guaranteed(0,left),guaranteed(1,right));result[bounds]+=1;example[bounds]=shared
    frontier=sorted((x,y) for x,y in result if not any((a>x or b>y) and a>=x and b>=y for a,b in result))
    return frontier,[example[key] for key in frontier]


def matching(left, right, rows):
    owners={}
    def augment(first,used):
        for second in sites(rows[first]&right):
            if second in used:continue
            used.add(second)
            if second not in owners or augment(owners[second],used):owners[second]=first;return True
        return False
    for first in sites(left):augment(first,set())
    return len(owners)


def actual(frame):
    rows,paths,wings,union,overlap,seeds=grammar(frame);result=set()
    for shared in subsets(overlap):
        left=union[0]&~(overlap^shared);right=union[1]&~shared
        result.add((matching(wings[0][0]&left,wings[0][1]&left,rows),matching(wings[1][0]&right,wings[1][1]&right,rows)))
    return sorted((x,y) for x,y in result if not any((a>x or b>y) and a>=x and b>=y for a,b in result))


def run(source):
    for key,frame,truth in map(json.loads,source.read_text().splitlines()):
        frontier,example=allocation(frame);record=dict(id=key,front=frontier,split=example)
        if truth:
            precise=actual([(1<<len(truth))-1,*truth]);record['physical']=precise
            assert all(any(a>=x and b>=y for a,b in precise) for x,y in frontier)
        print(json.dumps(record,separators=(',',':')))


if __name__=='__main__':run(Path(sys.argv[1]))
