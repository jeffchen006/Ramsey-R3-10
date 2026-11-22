import json
import sys
from collections import Counter
from itertools import combinations,product
from pathlib import Path
from wing24 import OUT,graph_masks,expand,sites,population

def profiles(wing,points,words,added,degree,required,budget,hub=False):
    groups=sorted(Counter(words).items());side=len(wing)//2;debit=0
    for left,right in combinations(range(len(points)),2):
        if wing[points[left]]>>points[right]&1:continue
        total=(wing[points[left]]&wing[points[right]]).bit_count()+int((points[left]<side)==(points[right]<side))+sum(mask>>left&mask>>right&1 for mask in words);debit+=max(0,2-total)
    bounds=[]
    for site in points:
        if hub:bounds.append((1,2,False));continue
        if wing[site]>>added&1:bounds.append((0,0,False));continue
        known=(wing[site]&wing[added]).bit_count()+int((site<side)==(added<side));bounds.append((2-known,3-known,True))
    hist=[];current=[];partial=[0]*len(points)
    def walk(idx,remaining):
        if idx==len(groups):
            extra=sum(max(0,low-have) for (low,upper,allow),have in zip(bounds,partial) if allow)
            if not remaining and debit+extra<=budget and all(allow or have>=low for (low,upper,allow),have in zip(bounds,partial)):hist.append((tuple(current),extra))
            return
        mask,count=groups[idx];bits=list(sites(mask));upper=min([count,remaining,*[bounds[bit][1]-partial[bit] for bit in bits]])
        for qty in range(max(0,remaining-sum(n for _,n in groups[idx+1:])),upper+1):
            current.append(qty)
            for bit in bits:partial[bit]+=qty
            walk(idx+1,remaining-qty)
            for bit in bits:partial[bit]-=qty
            current.pop()
    walk(0,required);return hist

def children(wing,points,words,added,degree,budget):
    groups=sorted(Counter(words).items());hist=profiles(wing,points,words,added,degree,degree-1-wing[added].bit_count(),budget);decks=sorted(tuple(sorted(word for (mask,count),qty in zip(groups,profile) for word in [mask]*(count-qty)+[mask|(1<<len(points))]*qty)) for profile,debit in hist);assert len(decks)==len(set(decks));return decks

def roster():
    records=json.loads((OUT/'spec.json').read_text());result={};checks=set();sizes=Counter();hubs=Counter()
    for row in records:
        wing=graph_masks(row['g6']);points=row['points']
        for idx,words in enumerate(row['decks']):
            options=[]
            for added in sorted(set(range(16))-set(points)):
                decks=children(wing,points,words,added,9,1);options.append((len(decks),added,decks))
            size,added,decks=min(options);sizes[size]+=1;key=f'{row["number"]}_{idx}';result[key]=dict(added=added,decks=decks);checks.add((row['number'],added));hubs[len(profiles(wing,points,words,None,9,7,1,True))]+=1
    (OUT/'split.json').write_text(json.dumps(result));print('360 min charge fifth-site lift census',sizes,'all roots',sum(k*v for k,v in sizes.items()),'unique 5site checks',len(checks),'hub support hist',hubs,flush=True)
    for number,added in sorted(checks):
        row=next(row for row in records if row['number']==number);expected=set(population(graph_masks(row['g6']),[*row['points'],added],9,21,1));actual=set()
        for idx,words in enumerate(row['decks']):actual.update(children(graph_masks(row['g6']),row['points'],words,added,9,1))
        assert actual==expected,(number,added)
    print('all selected five-site multiplicity censuses independently matched')

def formula_split(token):
    parent,child=token[1:].split('-');number,idx=map(int,parent.split('_'));row=next(row for row in json.loads((OUT/'spec.json').read_text()) if row['number']==number);spec=json.loads((OUT/'split.json').read_text())[parent];return expand(graph_masks(row['g6']),[*row['points'],spec['added']],spec['decks'][int(child)],45,9,True)

if __name__=='__main__':roster()
