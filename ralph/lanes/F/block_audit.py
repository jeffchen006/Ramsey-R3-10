"""Independent source-map, affine cover, support-multiplicity and terminal-proof verifier."""

import argparse
from collections import Counter
from csv import DictReader
from hashlib import sha256
from itertools import combinations
from math import gcd
from pathlib import Path

from cyclic_check import read_base, rank, check


def lines(filename): return Path(filename).read_text().splitlines()


def inherited():
    rows=lines('../r8/target.q')
    receipts=Path('../../critic/r8/F/F.tsv').read_bytes()
    assert receipts==Path('../r8/target.receipt.tsv').read_bytes()
    data=list(DictReader(receipts.decode().splitlines(),delimiter='\t'))
    assert len(data)==len(rows)==99
    for index,(text,receipt) in enumerate(zip(rows,data)):
        assert int(receipt['row'])==index and sha256(text.encode()).hexdigest()==receipt['source_sha256']
    print('INHERITED confirmed F-011 row hashes',len(data),flush=True)
    return rows


def patterns(base):
    size=len(base)//2
    first=tuple(base[0][:size]);second=tuple(base[size][size:]);cross=tuple(base[0][size:])
    for left in range(size):
        for right in range(size):
            assert base[left][right]==first[(right-left)%size]
            assert base[size+left][size+right]==second[(right-left)%size]
            assert base[left][right+size]==cross[(right-left)%size]
    for left,row in enumerate(base):
        for right,weight in enumerate(row):
            if weight==2:
                assert not any(x and y for x,y in zip(row,base[right]))
    return first,second,cross


def affine(first,second,cross):
    size=len(cross)
    for unit in range(1,size):
        if gcd(size,unit)!=1: continue
        moved=[bytes(row[(step*unit)%size] for step in range(size)) for row in [first,second]]
        for shift in range(size):
            last=bytes(cross[(step*unit+shift)%size] for step in range(size))
            yield moved[0]+moved[1]+last
            yield moved[1]+moved[0]+last


def source(tag, old, counts_file, dtype, limit=None, receipts=None):
    rows=lines(tag+'.q');covered=set();domains=set();usage=Counter();reached=set()
    for receipt in (receipts if receipts is not None else lines(tag+'.maps')):
        text,name,number,image=receipt.split();index=int(number);assert name in ['old','new'] and index>=0
        base=read_base(text);first,second,cross=patterns(base);size=len(cross)
        assert dtype=='B' or first==second
        dest=read_base((old if name=='old' else rows)[index]);perm=list(map(int,image.split(',')))
        assert sorted(perm)==list(range(2*size)) and len(dest)==2*size
        assert all(weight==dest[perm[left]][perm[right]] for left,row in enumerate(base) for right,weight in enumerate(row))
        if name=='new': reached.add(index)
        images=set(affine(first,second,cross));assert images.isdisjoint(covered);covered.update(images)
        for key in images:
            degrees=sum(key[:size])+sum(key[2*size:]),sum(key[size:])
            usage[degrees]+=1
        assert text not in domains; domains.add(text)
    expected={}
    for line in lines(counts_file):
        kind,first,second,count=line.split(); degrees=int(first),int(second)
        if kind==dtype and (not limit or degrees in limit):expected[degrees]=int(count)
    assert reached==set(range(len(rows))) and usage==expected, (dict(usage),expected)
    print('SOURCE',tag,'indexed',len(rows),'affine records',len(domains),'labelled',sum(usage.values()),'counts',sorted(usage.items()),flush=True)


def support_total(base,target,entries):
    size=len(base);ident={};boundary=[];triangles=[]
    for left,right in combinations(range(size),2):
        if base[left][right]==1:
            ident[left,right]=1<<len(boundary);boundary.append((1<<left)|(1<<right))
    for triple in combinations(range(size),3):
        edges=list(combinations(triple,2))
        if all(edge in ident for edge in edges):triangles.append(sum(ident[edge] for edge in edges))
    tri_rank=rank(triangles);seen=set();counter=0
    for entry in entries:
        full,single,weight=map(int,entry.split(':'))
        assert 0<=(full|single)<1<<size and not(full&single) and 2*full.bit_count()+single.bit_count()==target
        assert (full,single) not in seen;seen.add((full,single))
        occupied=[vertex for vertex in range(size) if (full|single)&(1<<vertex)]
        for left in occupied:
            if full&(1<<left):assert all(base[left][right]==0 for right in occupied)
        assert all(base[left][right]!=2 for left,right in combinations(occupied,2))
        active=[index for index,incident in enumerate(boundary) if not incident&~single]
        boundary_rank=rank(boundary[index] for index in active)
        components=single.bit_count()-boundary_rank;dim=len(active)-boundary_rank
        if dim:
            keep=sum(1<<index for index in active)
            assert tri_rank-rank(triangle&~keep for triangle in triangles)==dim
        assert weight==1<<components
        counter+=weight
    return counter


def verify_bounds(tag,target):
    rows=lines(tag+'.q');certs=lines(tag+'.fcert');report=lines(tag+'.forced');assert len(rows)==len(certs)==len(report)
    result=[];used=0
    for index,(text,cert,line) in enumerate(zip(rows,certs,report)):
        raw,*entries=cert.split();number,total,count=map(int,line.split());assert int(raw)==number==index and len(entries)==count
        assert support_total(read_base(text),target,entries)==total
        result.append(total);used+=count
    print('BOUND',tag,'rows',len(rows),'supports',used,'zero',result.count(0),'at least 25',sum(value>=25 for value in result),flush=True)
    return result


def terminal(tag,folder,ids,values):
    rows=lines(tag+'.q');indices=list(map(int,lines(ids)))
    assert len(indices)==len(set(indices)) and all(0<=index<len(rows) for index in indices)
    assert {index for index,value in enumerate(values) if not value}<=set(indices)
    receipt=[]
    for index in indices:
        stem=Path(folder)/f'{index:04}';cuts=check(rows[index],10,stem)
        hashes=[sha256(stem.with_suffix(ext).read_bytes()).hexdigest() for ext in ['.cnf','.trace','.lrat']]
        receipt.append(' '.join(map(str,[index,cuts,sha256(rows[index].encode()).hexdigest(),*hashes])))
    expected={Path(folder)/f'{index:04}.lrat' for index in indices};assert expected==set(Path(folder).glob('*.lrat'))
    Path(folder+'.receipt').write_text('\n'.join(receipt)+'\n');print('PROOF',folder,'independent semantic + dual LRAT',len(receipt),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('mode',choices=['source_ctl','source','bounds_ctl','bounds'])
    args=parser.parse_args();assert __debug__
    if args.mode=='source_ctl':
        source('small',[],'counts.small','D');source('bismall',[],'counts.small','B')
        source('ctl',[],'counts.ctl','D',{(5,5)});source('bictl',[],'counts.ctl','B')
    elif args.mode=='source':
        old=inherited();source('target',old,'counts.target','D')
        source('bitarget',old+lines('target.q'),'counts.target','B')
    elif args.mode=='bounds_ctl':
        assert verify_bounds('small',4)==list(map(int,lines('small.scores')))
        checked=verify_bounds('ctl',6)
        assert checked[5]==0 and all(checked[int(line.split()[0])]==0 for line in lines('ctl.log') if line.split()[1]=='yes')
    else:
        terminal('target','hardproof','hard.ids',verify_bounds('target',10))
        terminal('bitarget','bizproof','bizero.ids',verify_bounds('bitarget',10))
