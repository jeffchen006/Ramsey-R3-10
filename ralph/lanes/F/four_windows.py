"""Exact unsigned antineighbourhood measurements at fixed poles and whole holes."""
from collections import Counter
from itertools import combinations
from pathlib import Path

from cyclic_check import read_base
from four_slot import put
from orbit_extend import independent


def minimum(target,order):
    if order>=(0,1,3,6,9,14,18,23,28,36)[target]:return 10000
    stable=target-1
    general=max(0,order-stable,3*order-5*stable,5*order-10*stable,6*order-13*stable)
    tables={9:(26,[52,61,68,77,86,95,104,118,129,140]),8:(19,[25,30,35,42,49,56,65,73,85]),7:(19,[37,44,51,60])}
    if target in tables:
        start,values=tables[target]
        if order>=start:return values[order-start]
    return general


def screen(base,columns,flags):
    fibers=len(base);size=fibers+4;weights=[2]*fibers+[1]*4
    adjacency=[0]*size;edges=[[0]*size for _ in range(size)]
    def join(left,right,number):
        if number:adjacency[left]|=1<<right;adjacency[right]|=1<<left;edges[left][right]=edges[right][left]=number
    holes=columns[0]|columns[1]|columns[2]|columns[3];full=(1<<size)-1
    singles=((1<<4)-1)<<fibers
    for left,right in combinations(range(fibers),2):join(left,right,2*base[left][right])
    for index,column in enumerate(columns):
        for site in range(fibers):join(site,fibers+index,2*(column>>site&1))
    for index,(left,right) in enumerate(combinations(range(4),2)):join(fibers+left,fibers+right,flags>>index&1)
    verts=[int(site<fibers and not (holes>>site&1)) for site in range(size)]
    degrees=[sum(row)//weight+vertical for row,weight,vertical in zip(edges,weights,verts)]
    total=sum(sum(row) for row in edges)//2+sum(verts)
    for vertex in range(size):
        window=total-degrees[vertex]*verts[vertex]-sum(number*degrees[other] for other,number in enumerate(edges[vertex]))//weights[vertex]
        order=39-degrees[vertex];limit=minimum(9,order)
        if window<limit:return ('single',vertex,order,window,limit)
    for left,right in combinations(range(fibers,size),2):
        if adjacency[left]>>right&1:continue
        common=adjacency[left]&adjacency[right];codeg=sum(weight for site,weight in enumerate(weights) if common>>site&1)
        if codeg>degrees[left]+degrees[right]-11:return ('codegree',left,right,codeg,degrees[left]+degrees[right]-11)
    def recurse(eligible,available,mark,order):
        while eligible:
            bit=eligible&-eligible;site=bit.bit_length()-1;eligible^=bit
            nxt=available&~(bit|adjacency[site]);active=[idx for idx in range(size) if nxt>>idx&1]
            marked=mark|bit;used=order+weights[site];nwin=sum(weights[idx] for idx in active)
            ewin=sum(verts[idx] for idx in active)+sum(edges[left][right] for left,right in combinations(active,2));limit=minimum(10-used,nwin) if used<10 else 10000
            if ewin<limit:return ('orbits',marked,nwin,ewin,limit)
            fail=recurse(eligible&nxt,nxt,marked,used)
            if fail:return fail
    return recurse(holes|singles,full,0,0)


def main():
    base=read_base(Path('col53.q').read_text().strip());counts=Counter();survivors=[];traces=[]
    for row in Path('whole53.good').read_text().splitlines():
        values=list(map(int,row.split()));columns=values[:4];flags=values[4:];out=[]
        for bits in flags:
            failure=screen(base,columns,bits)
            if not failure:out.append(bits)
            counts[failure[0] if failure else 'pass']+=1
            traces.append(' '.join(map(str,(*columns,bits,*(failure or ('pass',))))))
        if out:survivors.append(' '.join(map(str,(*columns,*out))))
    put('windows53.receipt',traces);put('windows53.open',survivors);print('old-only necessary quadruple tests:',sorted(counts.items()),'open quadruple reps:',len(survivors))


if __name__=='__main__':main()
