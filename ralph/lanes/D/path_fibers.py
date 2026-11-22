"""Integer contacts with six consecutive wing sites. Populations, not Q graphs."""
from functools import lru_cache
from collections import Counter
from itertools import combinations,product
from time import process_time
import json,sys
from book_controls import bitset,sites,flags,graph_masks,book,reorder
from kernel_cnf import ROOT
from equal_roles import DEST


def instance(graph,degree,order):
    outside=order-(2*degree+1);size=len(graph);pairs=list(combinations(range(size),2));ind=[word for word in range(1<<size) if all(not(graph[site]&word) for site in sites(word))];return outside,pairs,ind


def census(graph,demand,bounds,population,debit,write,only=None):
    start=process_time();size=len(graph);pairs=list(bounds);masks=[mask for mask in range(1<<size) if all(not(graph[site]&mask) for site in sites(mask))];pool=[mask for mask in sorted(masks,key=lambda mask:(-mask.bit_count(),mask)) if mask.bit_count()>=2];uses=[list(sites(mask)) for mask in pool];pairsets=[[idx for idx,(left,right) in enumerate(pairs) if (mask>>left)&(mask>>right)&1] for mask in pool];remaining=list(demand);lower=[bounds[key][0] for key in pairs];capacity=[bounds[key][1] for key in pairs];chosen={};count=0;dedup=Counter();target=only
    def walk(index,spent,leaks):
        nonlocal count
        if index==len(pool):
            gap=population-spent-sum(remaining)
            if gap<0:return
            profile=dict(chosen);profile.update({1<<idx:value for idx,value in enumerate(remaining) if value});
            if gap:profile[0]=gap
            if target is not None and profile!=target:return
            count+=1
            if write:write(profile,leaks)
            dedup[leaks]+=1;return
        mask=pool[index];one=uses[index];two=pairsets[index];maximum=min([*(remaining[site] for site in one),*(capacity[site] for site in two)]);minimum=0
        if mask.bit_count()==2:minimum=max(0,lower[two[0]]-debit+leaks)
        for value in (range(minimum,maximum+1) if target is None else (target.get(mask,0),)):
            if not minimum<=value<=maximum:continue
            extra=max(0,lower[two[0]]-value) if len(two)==1 else 0
            if leaks+extra>debit:continue
            for term in one:remaining[term]-=value
            for term in two:capacity[term]-=value;lower[term]-=value
            if value:chosen[mask]=value
            walk(index+1,spent+value,leaks+extra)
            if value:del chosen[mask]
            for term in one:remaining[term]+=value
            for term in two:capacity[term]+=value;lower[term]+=value
    walk(0,0,0);return count,dedup,process_time()-start


def data(graph,core,points,degree):
    rows=reorder(graph,points);demand=[degree-(graph[site]&core).bit_count() for site in points];bounds={}
    for left,right in combinations(range(len(points)),2):
        if rows[left]>>right&1:continue
        used=(graph[points[left]]&graph[points[right]]&core).bit_count();bounds[left,right]=(2-used,3-used)
    return rows,demand,bounds


def cal():
    seen=0
    for text in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=graph_masks(text)
        if {word.bit_count() for word in graph}!={6} or max((one&two).bit_count() for one,two in combinations(graph,2))>3:continue
        for ends in flags(graph):
            frame,(left,right)=book(graph,ends);core=bitset(frame+left+right);points=(*left[:3],*right[:3]);rows,demand,bounds=data(graph,core,points,6);outer=[site for site in range(22) if not(core>>site&1)];target=Counter(bitset(idx for idx,point in enumerate(points) if graph[site]>>point&1) for site in outer);debit=sum((graph[points[lhs]]&graph[points[rhs]]).bit_count()==1 for lhs,rhs in bounds);count,_,_=census(rows,demand,bounds,len(outer),debit,None,target);assert count==1;seen+=1
    print('PASS 125 literal C22 integer profiles and exact physical min-codegree exceptions',seen)


if __name__=='__main__':
    if sys.argv[1]=='cal':cal()
    else:
        from equal_roles import shape,standard
        parts=(8,);rows,cycles=shape(parts);graph=standard(rows);points=cycles[0][:6];arrays=data(graph,(1<<19)-1,points,9)
        def output(profile,leak):print(' '.join(str(word) for word,count in sorted(profile.items()) for _ in range(count)))
        print('size,leak counts,CPU',census(*arrays,21,1,output if sys.argv[1]=='emit' else None),file=sys.stderr)
