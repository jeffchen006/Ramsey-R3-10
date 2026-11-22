"""Independent verifier of the five-word necessary cover (not of realizability)."""
from collections import Counter
from itertools import combinations,product
from pathlib import Path
import json
import subprocess
import numpy as np

from cyclic_check import read_base,rank
from four_slot import put
from odd_check import verify
from orbit_extend import ROOT,parse_graph6


def lines(name):return Path(name).read_text().splitlines()


def bind():
    sources=lines('max.q');images={};parent=lines('parents.tsv')
    for idx,text in enumerate(sources):
        base=read_base(text);row=base[0];word=''.join(map(str,row[1:10]));ident,actual,size=parent[idx].split();assert (int(ident),actual)==(idx,word)
        assert len(base)==18 and all(base[a][b]==row[(b-a)%18] for a,b in product(range(18),repeat=2)) and row[0]==int(max(row)!=2)
        equiv={tuple(row[(unit*offset)%18] for offset in range(1,10)) for unit in (1,5,7,11,13,17)}
        assert len(equiv)==int(size) and not equiv&images.keys();images.update({key:idx for key in equiv})
    fresh=set()
    for word in product(range(3),repeat=9):
        row=(0,)+word+word[-2::-1];degree=sum(row);assert len(row)==18
        if degree not in (6,7,8) or degree==6 and 2 in row:continue
        if any(row[a]==2 and row[b] and row[(a-b)%18] for a,b in product(range(1,18),repeat=2)):continue
        fresh.add(word)
    assert fresh==images.keys();assert len(fresh)==340 and len(sources)==120
    surviving=[]
    for idx,(text,line) in enumerate(zip(sources,lines('max.odd'),strict=True)):
        ident,*tokens=line.split();assert int(ident)==idx
        if not verify(text,10,tokens):surviving.append(idx)
    assert surviving==[8,15,21,43,53,54,76,80,81,83,84,116]
    print('independent source 340/120; unbranched old-card survivors',surviving)
    return sources


def close_holes(sources):
    parents={83:[],84:[]}
    for lineno,(role,row,line) in enumerate(zip(lines('holes.map'),lines('holes.q'),lines('holes.odd'),strict=True)):
        idx,mask=map(int,role.split());ident,*tokens=line.split();assert int(ident)==lineno
        if idx not in parents or not tokens:continue
        base=read_base(row);origin=read_base(sources[idx]);assert all(base[a][b]==(int(not mask>>a&1) if a==b else origin[a][b]) for a,b in product(range(18),repeat=2))
        assert verify(row,10,tokens)>0
        for sign,shift in product((1,-1),range(18)):
            parents[idx].append(sum(1<<((sign*a+shift)%18) for a in range(18) if mask>>a&1))
    allm=np.arange(1<<18,dtype=np.int64);pop=np.asarray([i.bit_count() for i in range(1<<18)])
    for idx,masks in parents.items():
        live=allm[pop>=8];base=read_base(sources[idx])
        for mask in set(masks):live=live[live&mask!=mask]
        before=len(live)
        for site in range(18):
            near=sum(1<<other for other in range(18) if other!=site and base[site][other]);live=live[((live>>site)&1!=0)|(pop[live&near]>=4)]
        assert (before,len(live))==((81,0) if idx==83 else (0,0));print('r8 mask audit',idx,before,'->',len(live))


def all_subsets(mask):
    subset=mask
    while True:
        yield subset
        if not subset:break
        subset=(subset-1)&mask


def audit_columns(sources,idx):
    text=sources[idx];base=read_base(text);assert int(lines(f'col{idx}.log')[0].split()[3]) in (18,72)
    subprocess.run(['../r9/forced',f'col{idx}.q','9','1000000',f'col{idx}.nine'],check=True,stdout=subprocess.DEVNULL)
    tokens=lines(f'col{idx}.nine')[0].split()[1:];supports=[]
    for token in tokens:
        both,one,count=map(int,token.split(':'));assert both==0 and count>=2;supports.append(one)
    assert verify(text,9,[f'U1:0,{mask}' for mask in supports])==len(supports)
    universe=(1<<18)-1;neighbors=[sum(1<<other for other in range(18) if other!=site and row[other]) for site,row in enumerate(base)]
    def components(mask):
        result=[]
        while mask:
            reach=mask&-mask
            while True:
                old=reach
                for site in range(18):
                    if reach>>site&1:reach|=mask&neighbors[site]
                if reach==old:break
            result.append(reach);mask^=reach
        return result
    good={}
    for mask in supports:
        parts=components(mask);lookup=np.zeros(1<<18,dtype=np.uint8)
        for subset in all_subsets(mask):lookup[subset]=not all(len(components(subset&part))<=1 for part in parts)
        good[mask]=lookup
    alphas=[0]*(1<<18)
    for mask in range(1,1<<18):
        bit=mask&-mask;alphas[mask]=max(alphas[mask^bit],1+alphas[(mask^bit)&~neighbors[bit.bit_length()-1]])
    passed=set()
    for full in range(1<<18):
        ns=full.bit_count();limit=9-2*ns
        if limit<0 or alphas[full]!=ns:continue
        available=universe^full
        for site in range(18):
            if full>>site&1:available&=~neighbors[site]
        one=np.asarray([mask for mask in all_subsets(available) if mask.bit_count()<=limit and (full or mask)],dtype=np.int32)
        for mask,lookup in good.items():
            if not mask&full:one=one[lookup[one&mask]!=0]
            if not len(one):break
        for raw in one:
            single=int(raw);weak=sum(1<<site for site in range(18) if not (full|single)>>site&1 and (neighbors[site]&single).bit_count()<=1)
            if alphas[weak]+single.bit_count()<9:passed.add((full,single))
    saved={tuple(map(int,row.split()[:2])) for row in lines(f'col{idx}.rows')};assert passed==saved
    even=sum(1<<site for site in range(0,18,2))
    if idx==53:assert all(not single and (not full&even or not full&~even) and full.bit_count() in (3,4) for full,single in passed)
    if idx==116:assert all(not single and full.bit_count()==4 for full,single in passed)
    print('columns rederived',idx,'balanced witnesses',len(good),'passed',len(passed),'full sizes',sorted(Counter(mask.bit_count() for mask,single in passed).items()))


def audit_rank(sources):
    base=read_base(sources[54]);edges=[(left,right) for right in range(18) for left in range(right) if base[left][right]==1];bits={edge:1<<pos for pos,edge in enumerate(edges)}
    triangles=[sum(bits[e] for e in combinations(triple,2)) for triple in combinations(range(18),3) if all(e in bits for e in combinations(triple,2))];seen={0}
    for step in range(18):seen.update(other for edge in edges if seen.intersection(edge) for other in edge)
    assert len(seen)==18 and len(edges)-rank(triangles)-17==2
    cyclechars=[]
    for line in lines('col54.models'):
        fields=line.split();point=int(fields[1]);assert all((point&row).bit_count()%2==0 for row in triangles);cyclechars.append(point)
        graph=[0]*36
        for left,right in combinations(range(36),2):
            site,other=left//2,right//2;val=base[site][other];adjacent=val==2 or (val==1 and (((left^right)&1)^bool(point&bits[site,other])))
            if adjacent:graph[left]|=1<<right;graph[right]|=1<<left
        assert all(not(graph[left]&graph[right]) for left,right in combinations(range(36),2) if graph[left]>>right&1)
        if fields[2]=='I10':
            mask=int(fields[3]);assert mask.bit_count()==10 and not any(mask>>site&1 and mask&hood for site,hood in enumerate(graph));continue
        assert graph==parse_graph6(lines('col54.strict.g6')[0]);result=json.loads(subprocess.check_output([sys.executable,'-I',str(ROOT/'.hmz/flows/r310_ralph/gate.py'),str(ROOT),'check','col54.strict.g6','36','10']));assert result['graphs'][0]['ok'];Path('rank.gate').write_text(json.dumps(result)+'\n')
        nine=[]
        def stable(selected,eligible,need):
            if not need:nine.append(selected);return
            while eligible.bit_count()>=need:
                bit=1<<(eligible.bit_length()-1);eligible^=bit;stable(selected|bit,eligible&~graph[bit.bit_length()-1],need-1)
        stable(0,(1<<36)-1,9);assert len(nine)==180
        nodes=0
        def hits(eligible,rows,room):
            nonlocal nodes
            nodes+=1
            if not rows:return True
            if not room:return False
            opts=min((row&eligible for row in rows),key=int.bit_count)
            while opts:
                bit=opts&-opts;opts^=bit;eligible^=bit
                if hits(eligible&~graph[bit.bit_length()-1],[row for row in rows if not row&bit],room-1):return True
            return False
        assert not hits((1<<36)-1,nine,7);print('old54 strict model gate; 180 nines, no independent <=7 transversal; hitting nodes',nodes)
    cuts=[sum(value for edge,value in bits.items() if site in edge) for site in range(18)]
    assert len(cyclechars)==4 and all(rank(cuts+[left^right])>rank(cuts) for left,right in combinations(cyclechars,2))
    print('all four old switching classes independently bound')


if __name__=='__main__':
    import sys
    parents=bind();close_holes(parents)
    for ident in (53,76,116):audit_columns(parents,ident)
    audit_rank(parents);print('residual ID/word:',[(idx,lines('parents.tsv')[idx].split()[1]) for idx in (8,15,21,43,81)])
