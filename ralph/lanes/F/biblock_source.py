"""Unsigned simultaneous rotation of two fiber blocks; no reflection or sign symmetry assumed."""

from argparse import ArgumentParser
from collections import Counter
from itertools import product, combinations_with_replacement
from math import gcd
from pathlib import Path

from dihedral_source import canon
from relift_audit import encode, decode


def build(first,second,cross):
    length=len(cross)
    return [[(first if left<length else second)[(right-left)%length] if left//length==right//length
             else cross[(right-left if left<right else left-right)%length] for right in range(2*length)]
            for left in range(2*length)]


def eligible(layer,cross):
    size=len(layer); vertical=layer[0]
    if vertical and (2 in layer or 2 in cross): return False
    for step in range(1,size):
        if not layer[step]: continue
        if any(cross[other] and cross[(other+step)%size] and max(layer[step], cross[other], cross[(other+step)%size])==2
               for other in range(size)): return False
        if layer[step]==2 and any(layer[other] and layer[(other+step)%size]
                                 for other in range(1,size) if (other+step)%size): return False
    return True


def variants(size,low,high,sum_min):
    units=[unit for unit in range(1,size) if gcd(unit,size)==1]
    layers=[(vertical,)+tuple(half[min(step,size-step)-1] for step in range(1,size))
            for vertical in range(2) for half in product(range(3),repeat=size//2)]
    seen=set()
    for cross in product(range(3),repeat=size):
        mass=sum(cross)
        if mass>high or cross in seen: continue
        stabilizer=set()
        for unit in units:
            for shift in range(size):
                image=tuple(cross[(unit*step+shift)%size] for step in range(size))
                seen.add(image)
                if image==cross: stabilizer.add(unit)
        valid=[layer for layer in layers if low<=mass+sum(layer)<=high and eligible(layer,cross)]
        for first,second in combinations_with_replacement(valid,2):
            if sum(first)+sum(second)+2*mass<sum_min: continue
            chosen=tuple(sorted((first,second)))
            if any(tuple(sorted(tuple(layer[(unit*step)%size] for step in range(size)) for layer in chosen))<chosen
                   for unit in stabilizer): continue
            yield first,second,cross


def generate(tag,size,low,high,sum_min,old,only_count):
    if only_count:
        counts=Counter((sum(first)+sum(cross),sum(second)+sum(cross)) for first,second,cross in variants(size,low,high,sum_min))
        print('affine block-pair counts',counts,'total',sum(counts.values())); return
    cache={}; rows=[]; counts=Counter()
    for index,text in enumerate(old):
        key,perm=canon(decode(text)); cache[key]=('old',index,perm)
    with open(tag+'.maps','w') as receipt:
        for first,second,cross in variants(size,low,high,sum_min):
            base=build(first,second,cross); orig=encode(base); key,perm=canon(base)
            if key not in cache:
                cache[key]=('new',len(rows),perm); rows.append(orig)
            name,index,dest=cache[key]; counts[name]+=1
            print(orig,name,index,','.join(str(dest[perm.index(left)]) for left in range(2*size)),file=receipt)
    Path(tag+'.q').write_text(''.join(text+'\n' for text in rows))
    print(tag,'affine rows',dict(counts),'new',len(rows))


if __name__=='__main__':
    parser=ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('small','ctl','target'))
    parser.add_argument('--count',action='store_true'); args=parser.parse_args()
    size,low,high,total,old={'small':(2,0,7,0,[]),'ctl':(4,4,5,9,[]),'target':(10,8,9,17,['../r8/target.q','target.q'])}[args.mode]
    previous=[text for filename in old for text in Path(filename).read_text().splitlines()]
    generate('bi'+args.mode,size,low,high,total,previous,args.count)
