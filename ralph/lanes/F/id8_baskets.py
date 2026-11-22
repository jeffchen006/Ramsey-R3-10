"""Unsigned forest windows with a ten-site bipartite set outside. No signing search."""
from collections import Counter
from itertools import combinations,product
from pathlib import Path
import sys

from orbit_extend import independent_sets,vertices


def components(mask,adj):
    while mask:
        todo=mask&-mask;seen=todo
        while todo:
            site=(todo&-todo).bit_length()-1;todo^=1<<site
            more=adj[site]&mask&~seen;todo|=more;seen|=more
        yield seen;mask&=~seen


def bipartite(mask,adj):
    low=0;high=0
    for component in components(mask,adj):
        front=component&-component;low|=front;even=True
        while front:
            nbors=0
            for site in vertices(front):nbors|=adj[site]&mask
            if nbors & (low if even else high):return False
            front=nbors&~(low|high)
            if even:high|=front
            else:low|=front
            even=not even
    return True


def basket(adj,window,order):
    parts=list(components(window,adj))
    if sum((adj[site]&window).bit_count() for site in vertices(window))!=2*(window.bit_count()-len(parts)):return
    nontrivial=[part for part in parts if part&(part-1)]; eligible=[]
    for site in range(len(adj)):
        if window>>site&1:continue
        hits=[part&adj[site] for part in nontrivial if part&adj[site]]
        if len(hits)>1 or hits and len(list(components(hits[0],adj)))>1:continue
        eligible.append(site)
    for group in combinations(eligible,order):
        mask=sum(1<<site for site in group)
        if bipartite(mask,adj):return mask


def orbit(mask,size):
    full=(1<<size)-1;rev=sum(1<<(-site%size) for site in vertices(mask));return {(number<<offset&full)|(number>>(size-offset)) for offset in range(size) for number in (mask,rev)}


def control():
    from relift_audit import explicit_lift
    for size,order in [(5,4),(6,5)]:
        base=[[int(left==right or abs(left-right) in (1,size-1)) for right in range(size)] for left in range(size)];adj=[sum(1<<site for site in range(size) if site!=left and base[left][site]) for left in range(size)]
        window=2**(order-3)-1
        witness=basket(adj,window,order);assert bool(witness)==(size==5)
        if not witness:continue
        for signs in product((0,1),repeat=size):
            graph=explicit_lift(base,iter(signs));core=(1<<(2*size))-1
            if next(independent_sets(graph,core,order),None) is not None:continue
            for count in range(size+1):
                for feet in independent_sets(graph,core&~3,count):
                    assert next(independent_sets(graph,core&~feet,order-1),None) is not None
    print('C5 1-window/4-basket structural and physical controls; C6 insufficient basket retained')


def run(step=1):
    size=18;adj=[sum(1<<((site+shift)%18) for shift in range(6,13)) for site in range(18)];windows={};seen=set();candidates=0
    for group in combinations(range(18),7):
        mask=sum(1<<site for site in group)
        if mask in seen:continue
        images=orbit(mask,18);seen.update(images);candidates+=1
        if (candidates-1)%step:continue
        group2=basket(adj,mask,10)
        if group2:windows[mask]=group2
    print('window orbit reps priced',candidates,'stride',step,'qualifying reps',len(windows),flush=True)
    allwins=sorted(set().union(*(orbit(mask,18) for mask in windows))) if windows else []
    if step!=1:return
    Path('basket.reps').write_text(''.join(f'{mask} {group}\n' for mask,group in windows.items()));print('labelled windows',len(allwins))
    seen=set();hist=Counter();pre=Counter();groups={};standard=orbit(127,18);assert standard<=set(allwins)
    for count in range(8):
        for indices in combinations(range(18),count):
            foot=sum(1<<site for site in indices)
            if foot in seen:continue
            images=orbit(foot,18);seen.update(images)
            if not all(foot&mask for mask in standard):continue
            pre[count]+=len(images)
            if not all(foot&mask for mask in allwins):continue
            hist[count]+=len(images);groups[min(images)]=len(images)
    print('ordinary windows',sorted(pre.items()),'forest windows',sorted(hist.items()),'remaining dihedral reps',len(groups));Path('feet.reps').write_text(''.join(f'{mask} {count}\n' for mask,count in sorted(groups.items())))


if __name__=='__main__':
    if sys.argv[1]=='control':control()
    else:run(int(sys.argv[1]))
