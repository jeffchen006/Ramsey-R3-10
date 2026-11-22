"""Test hereditary obstructions on cyclic card templates with missing fibres."""

from itertools import combinations,product
from pathlib import Path
import sys

from punctured_cards import rows,write
from cyclic_check import read_base
from relift_audit import encode,explicit_lift,walk_score
from orbit_extend import independent


def project(base, missing):
    kept = [index for index in range(len(base)) if index not in missing]
    return encode([[base[left][right] for right in kept] for left in kept])


def make(tag, pilot):
    source = rows(tag+'.q');size = len(read_base(source[0]));limit=(size-1)//2
    lines=[]; maps=[]
    for index,text in enumerate(source):
        base=read_base(text)
        for step in range(1,limit+1):
            if pilot and (index not in (0,len(source)-3,len(source)-1) or step not in (1,limit)):continue
            lines.append(project(base,{0,step}));maps.append(f'{index} 0 {step}')
    stem=tag+('.pilot' if pilot else '.core')
    write(stem+'.q',lines);write(stem+'.maps',maps)
    print('projected core rows', stem,len(lines))


def control():
    make('small',False)
    mins=[]
    for text in rows('small.core.q'):
        base=read_base(text)
        count=sum(base[left][right]==1 for left,right in combinations(range(len(base)),2))
        scores=[]
        for signs in product(range(2),repeat=count):
            graph=explicit_lift(base,iter(signs))
            if all(independent(row,graph) for row in graph):scores.append(walk_score(graph,3))
        mins.append(min(scores))
    write('small.core.exact',mins);print('physical independent-three minima',mins)


if __name__=='__main__':
    if sys.argv[1]=='control':control()
    else: make('card',sys.argv[1]=='pilot')
