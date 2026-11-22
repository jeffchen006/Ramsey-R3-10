import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import sys
import time

from pysat.card import CardEnc, EncType
from pysat.formula import CNF, IDPool
from pysat.solvers import Cadical195

from closure22 import ROOT, bits, stage
from shadow import decode

STORE=ROOT/'scratch/D/y22'


def independent(stars):
    words=[0]
    for site,neighbors in enumerate(stars):
        words += [word|(1<<site) for word in words if not word&neighbors]
    return words


def masks(stars,sites,ground):
    return [sum(1<<index for index,other in enumerate(ground) if stars[site]>>other&1) for site in sites]


def build(stars,widths,sizes,hits,degree,cap,minimum,weak,extra,whole=True):
    field=range(len(stars)); words=independent(stars);pool=IDPool();formula=CNF();rows=[];vars=[]
    def bound(terms,low,high):
        if low>high or low>len(terms) or high<0:formula.append([]);return
        for literals,upper in [(terms,high),([-term for term in terms],len(terms)-low)]:
            if upper>=len(literals):continue
            if not upper:formula.extend([[-term] for term in literals]);continue
            formula.extend(CardEnc.atmost(literals,bound=upper,vpool=pool,encoding=EncType.seqcounter).clauses)
    for group,width in enumerate(widths):
        if group and not whole:break
        low,high=sizes[group];ind=[word for word in words if low<=word.bit_count()<=high and not any((word&seed)==0 and seed.bit_count()>=width for seed in words)] if group==0 else [word for word in words if low<=word.bit_count()<=high]
        entries=[]
        for word in ind:
            duplicates=1 if word.bit_count()>=cap else width
            values=[pool.id(('mask',group,word,copy)) for copy in range(duplicates)];formula.extend([[prev,-nxt] for prev,nxt in zip(values,values[1:])]);entries.extend((word,value) for value in values)
        vars.append(entries);rows+=entries
        bound([var for word,var in entries],width,width)
        for site in field:bound([var for word,var in entries if word>>site&1],*hits[group])
        for sample in combinations(field,cap):
            sub=sum(1<<site for site in sample);bound([var for word,var in entries if word&sub==sub],0,1)
        for sample in combinations(field,2):
            sub=sum(1<<site for site in sample);bound([var for word,var in entries if word&sub==sub],0,2)
        for seed in words:
            if seed.bit_count()>=max(2,width-4):bound([var for word,var in entries if not(word&seed)],0,width-seed.bit_count())
        if group==0:
            inc=[var for word,var in entries for _ in range(word.bit_count()-low)];bound(inc,extra,len(inc))
    if whole:
        for site,neighbors in enumerate(stars):
            need=degree-neighbors.bit_count();bound([var for word,var in rows if word>>site&1],need,need)
        debits=[]
        for first,second in combinations(field,2):
            if stars[first]>>second&1:continue
            sub=1<<first|1<<second;known=(stars[first]&stars[second]).bit_count();occurs=[var for word,var in rows if word&sub==sub];bound(occurs,minimum-1-known,cap-known)
            if minimum>known:
                debit=pool.id(('debit',first,second));debits.append(debit);bound(occurs+[debit],minimum-known,len(occurs)+1)
        bound(debits,0,weak)
    return formula,vars


def plant():
    count=0;classcount=Counter()
    for line in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        full=decode(line)
        if any(star.bit_count()!=6 for star in full):continue
        classcount['regular']+=1
        if max((star&other).bit_count() for star,other in combinations(full,2))>3:continue
        classcount['cap3']+=1
        for left in range(22):
            for right in range(22):
                common=full[left]&full[right]
                if common.bit_count()!=1 or full[left]>>right&1:continue
                middle=common.bit_length()-1
                outside=sorted(set(range(22))-{left,right,middle}-set(bits(full[left]|full[right]|full[middle])))
                groups=[list(bits(full[middle]&~(1<<left|1<<right))),list(bits(full[left]&~common)),list(bits(full[right]&~common))]
                actual=[masks(full,group,outside) for group in groups];stars=masks(full,outside,outside)
                bounds=lambda seq:(min(seq),max(seq));sizes=[bounds([word.bit_count() for word in words]) for words in actual]
                hits=[bounds([sum(word>>site&1 for word in words) for site in range(len(outside))]) for words in actual]
                weak=sum((full[v]&full[w]).bit_count()<2 for v,w in combinations(outside,2) if not(full[v]>>w&1))
                formula,variables=build(stars,[len(group) for group in groups],sizes,hits,6,3,2,weak,sum(word.bit_count()-sizes[0][0] for word in actual[0]))
                pins=[]
                for words,entries in zip(actual,variables):
                    histogram=Counter(words)
                    for word,var in entries:
                        pins.append(var if histogram[word]>0 else -var); histogram[word]-=1
                    assert max(histogram.values())<=0
                with Cadical195(bootstrap_with=formula.clauses) as solver:
                    assert solver.solve(assumptions=pins);bad=next(term for term in pins if term>0);assert not solver.solve(assumptions=[-term if term==bad else term for term in pins]); count+=1
    assert (classcount['regular'],classcount['cap3'],count)==(10,3,250);print('C22 all 250 planted three-family populations pass, 250 adverse lost-row pins fail; 10 regular, 3 cap-three.')


def roster():
    for index,line in enumerate((STORE/'all.g6').read_text().splitlines(),1):
        stars=decode(line);size=sum(star.bit_count() for star in stars)//2
        if max(word.bit_count() for word in independent(stars))<=7: print(index,size,line,sep='\t')


def target(line,whole):
    stars=decode(line);edges=sum(star.bit_count() for star in stars)//2
    return build(stars,[7,8,8],[(4,6),(3,5),(3,5)],[(2,3)]*3,9,3,2,1,max(0,16-edges),whole)[0]


if __name__=='__main__':
    action=sys.argv[1]
    if action=='cal':plant()
    elif action=='roster':roster()
    else:
        index=int(sys.argv[2]);whole=action!='pole';start=time.process_time();word=(STORE/'all.g6').read_text().splitlines()[index-1];formula=target(word,whole);built=time.process_time()-start
        if action=='emit':formula.to_file(sys.argv[3]);print(index,formula.nv,len(formula.clauses));sys.exit(0)
        with Cadical195(bootstrap_with=formula.clauses) as solver:
            solver.conf_budget(int(sys.argv[3]));status=solver.solve_limited();print(json.dumps(dict(index=index,graph=word,full=whole,status=status,nv=formula.nv,nc=len(formula.clauses),conf=solver.accum_stats()['conflicts'],build=built,cpu=time.process_time()-start)),flush=True)
