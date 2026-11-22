"""Propagate unsigned old-card obstructions and pole slots to all vertical masks."""
from collections import Counter,defaultdict
from functools import lru_cache
from itertools import combinations
from pathlib import Path
import sys
import numpy as np

from cyclic_check import read_base
from odd_check import verify
from relift_audit import encode
from four_slot import put


def lines(name):return Path(name).read_text().splitlines()


@lru_cache(None)
def orbit(mask):
    coords=[site for site in range(18) if mask>>site&1]
    return sorted({sum(1<<((shift+direction*site)%18) for site in coords) for shift in range(18) for direction in (-1,1)})


def survivors():return [int(row.split()[0]) for row in lines('max_odd.out') if not int(row.split()[1])]


def markings():
    quotients=[];roles=[];parents=lines('max.q')
    for index in survivors():
        base=read_base(parents[index]);
        if max(map(max,base))>1:continue
        for size in (1,2,3):
            masks={orbit(sum(1<<site for site in sites))[0] for sites in combinations(range(18),size) if 0 in sites}
            for mask in sorted(masks):
                for site in range(18):base[site][site]=1-(mask>>site&1)
                quotients.append(encode(base));roles.append(f'{index} {mask}')
    assert len(quotients)<2000 and len(quotients)==len(set(quotients))
    put('holes.q',quotients);put('holes.map',roles);print('hole roles',len(roles))


def counts():
    parents=lines('max.q');bad=defaultdict(list)
    for name,source,mapping in [('max',parents,[(idx,0) for idx in range(len(parents))]),('holes',lines('holes.q'),[tuple(map(int,row.split())) for row in lines('holes.map')])]:
        output=lines('max_odd.out' if name=='max' else 'holes.out');tokens=lines(name+'.odd');assert len(output)==len(tokens)==len(source)==len(mapping)
        for current,(text,receipt,summary,(parent,mask)) in enumerate(zip(source,tokens,output,mapping)):
            head,*pieces=receipt.split();idx,total,*_=map(int,summary.split());assert int(head)==idx==current
            assert verify(text,10,pieces)==total
            if name=='holes':
                base=read_base(parents[parent]);assert all(row[site] for site,row in enumerate(base))
                for site in range(18):base[site][site]=1-(mask>>site&1)
                assert encode(base)==text
                if total:bad[parent].append(mask)
    schedule=defaultdict(list)
    for row in lines('roles.tsv'):
        idx,degree,verts,shape,*prices=row.split();schedule[int(idx),int(verts)].append((shape,tuple(map(int,prices))))
    masks=np.arange(1<<18,dtype=np.int32);pop=np.asarray([int(val).bit_count() for val in masks],dtype=np.int8)
    results=[];witness=[]
    for idx in survivors():
        base=read_base(parents[idx]);degree=sum(base[0])-base[0][0];double=max(map(max,base))>1
        possible=np.ones(len(masks),dtype=bool) if not double else masks==(1<<18)-1
        for mask in sorted(bad[idx],key=int.bit_count):
            for move in orbit(mask):possible[(masks&move)==move]=False
        pools={};holes=Counter();post=Counter();postroles=0
        for count in range(19):
            group=masks[possible&(pop==count)];roles=schedule[idx,18-count]
            if not roles or not len(group):continue
            holes[count]=len(group);anyshape=np.zeros(len(group),dtype=bool)
            for shape,price in roles:
                low,high,slot,need,reach,cap0,cap1,req0,req1=price
                key=(count,cap0,cap1,req0,req1)
                if key not in pools:
                    passing=np.ones(len(group),dtype=bool)
                    for site,row in enumerate(base):
                        hole=(group>>site)&1
                        weighted=sum(pop[group&sum(1<<other for other in range(18) if other!=site and row[other]>=lim)] for lim in (1,2))
                        capacity=weighted*cap0+(degree-weighted)*cap1+(1-hole)*cap1
                        passing &= capacity>=np.where(hole,req0,req1)
                    pools[key]=passing
                passing=pools[key];anyshape|=passing;postroles+=int(sum(passing))
                if passing.any():witness.append(f'{idx} {count} {shape} {int(group[passing][0])} {int(passing.sum())}')
            if anyshape.any():post[count]=int(anyshape.sum())
        results.append(f'{idx} r={degree} double={int(double)} holecaps={dict(holes)} local={dict(post)} roles={postroles}')
    put('local.rows',results);put('local.byshape',witness);print('\n'.join(results));print('replayed',len(parents),'parents,',len(lines('holes.q')),'marked role rows')


if __name__=='__main__':{'mark':markings,'counts':counts}[sys.argv[1]]()
