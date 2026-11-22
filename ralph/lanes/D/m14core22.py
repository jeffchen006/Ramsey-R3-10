from collections import Counter
from itertools import combinations
from pathlib import Path
import json
import sys

from pysat.card import CardEnc
from pysat.formula import CNF,IDPool
from pysat.solvers import Cadical195

from closure22 import ROOT, bits
from shadow import decode
from triple18 import pairs

BASE=ROOT/'scratch/D/m14r22'


def rows(record):
    return list(record['triples'])+[mask for mask,number in zip(pairs(7),record['pairs']) for _ in range(number)]


def hall_cards(support,count):
    size=1<<len(support);unions=[0]*size;bad=bytearray(size);cards=[]
    for word in range(1,size):
        low=word&-word;unions[word]=unions[word^low]|support[low.bit_length()-1]
        if any(bad[word^(1<<site)] for site in bits(word)):
            bad[word]=1;continue
        if unions[word].bit_count()>=word.bit_count():continue
        bad[word]=1
        poles=((1<<count)-1)^unions[word];mask=word<<count
        for site in bits(poles):
            if mask.bit_count()==count+1:break
            mask|=1<<site
        assert mask.bit_count()==count+1;cards.append(mask)
    return cards


def formula(support,poles,inside,yranges,cap,cards):
    pool=IDPool();cnf=CNF();ys=list(range(poles,poles+len(support)));sites=list(range(poles))+ys
    def edge(left,right):return pool.id(('edge',min(left,right),max(left,right)))
    def bound(entries,low,high):
        if low>len(entries) or high<0:cnf.append([]);return
        if low>0:cnf.extend(CardEnc.atleast(entries,bound=low,vpool=pool).clauses)
        if high<len(entries):cnf.extend(CardEnc.atmost(entries,bound=high,vpool=pool).clauses)
    for left,right in combinations(range(poles),2):cnf.append([-edge(left,right)])
    for site,mask,interval in zip(ys,support,yranges):
        for pole in range(poles):cnf.append([edge(site,pole)*(1 if mask>>pole&1 else -1)])
        bound([edge(site,other) for other in ys if other!=site],*interval)
    bound([edge(left,right) for left,right in combinations(ys,2)],inside,inside)
    for triple in combinations(sites,3):cnf.append([-edge(left,right) for left,right in combinations(triple,2)])
    for left,right in combinations(sites,2):
        via=[]
        for witness in sites:
            if witness in (left,right):continue
            path=pool.id(('via',left,right,witness));via.append(path);cnf.append([-edge(left,witness),-edge(right,witness),path])
        bound(via,0,cap-int(right<poles))
    for mask in cards:
        assert mask>=0 and mask>>len(sites)==0 and mask.bit_count()==poles+1
        cnf.append([edge(left,right) for left,right in combinations(bits(mask),2)])
    return cnf,edge


def calibration():
    directed=0
    for line in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=decode(line)
        if any(star.bit_count()!=6 for star in graph) or max((left&right).bit_count() for left,right in combinations(graph,2))>3:continue
        for first in range(22):
            for second in range(22):
                common=graph[first]&graph[second]
                if common.bit_count()!=1 or graph[first]>>second&1:continue
                middle=common.bit_length()-1;poles=list(bits(graph[middle]&~((1<<first)|(1<<second))));ys=sorted(set(range(22))-{first,second,middle}-set(bits(graph[first]|graph[second]|graph[middle])))
                masks=[sum(1<<index for index,pole in enumerate(poles) if graph[y]>>pole&1) for y in ys];degs=[sum(graph[y]>>other&1 for other in ys) for y in ys]
                cards=hall_cards(masks,len(poles));cnf,edge=formula(masks,len(poles),sum(degs)//2,list(zip(degs,degs)),3,cards);labels=poles+ys
                pins=[edge(left,right)*(1 if graph[labels[left]]>>labels[right]&1 else -1) for left,right in combinations(range(len(labels)),2)]
                changed=edge(len(poles),len(poles)+1)
                with Cadical195(bootstrap_with=cnf.clauses) as solver:assert solver.solve(assumptions=pins) and not solver.solve(assumptions=[-term if abs(term)==changed else term for term in pins])
                directed+=1
    assert directed==250;print('250 physical C22 pole-only boards pass; 250 adverse Y mutations fail.')


def build(record):
    support=rows(record);cards=hall_cards(support,7);return formula(support,7,14,[(3-mask.bit_count(),5-mask.bit_count()) for mask in support],3,cards)[0],cards


if __name__=='__main__':
    if sys.argv[1]=='cal':calibration();sys.exit()
    records=[json.loads(line) for line in (BASE/'roster.jsonl').read_text().splitlines()]
    for index in map(int,sys.argv[1:]):
        cnf,cards=build(records[index-1]);
        with Cadical195(bootstrap_with=cnf.clauses) as solver:
            solver.conf_budget(4000);print(index,len(cards),solver.solve_limited(),solver.accum_stats()['conflicts'],flush=True)
