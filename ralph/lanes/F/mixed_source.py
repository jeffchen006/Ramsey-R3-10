"""Factor the complete unsigned (n,n,n/2) rotation source by its three cross words."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from functools import lru_cache
from itertools import product
from math import gcd, prod
from pathlib import Path

from relift_audit import encode


def bad(values):
    return min(values) > 0 and max(values) == 2


@lru_cache(None)
def words(size):
    return tuple(product(range(3), repeat=size))


@lru_cache(None)
def layers(size):
    result = []
    for vertical in (0, 1):
        for half in words(size//2):
            layer = (vertical,) + tuple(half[min(i,size-i)-1] for i in range(1,size))
            if vertical and 2 in layer: continue
            if any(bad((layer[i],layer[j],layer[j-i])) for i in range(1,size) for j in range(i+1,size)): continue
            result.append(layer)
    return tuple(result)


@lru_cache(None)
def allow(layer, cross):
    if layer[0] and 2 in cross: return False
    return not any(bad((weight,cross[pos],cross[(pos+step)%len(cross)]))
                   for step,weight in enumerate(layer[1:],1) if weight for pos in range(len(cross)))


@lru_cache(None)
def perm(word,unit,offset):
    return tuple(word[(unit*i+offset)%len(word)] for i in range(len(word)))


def crosses(size, high):
    short=size//2; units=[unit for unit in range(1,size) if gcd(unit,size)==1]; seen=set()
    for across in words(size):
        if sum(across)>high or across in seen: continue
        group=[(unit,offset) for unit in units for offset in range(size)]
        orbit={perm(across,*move) for move in group}; seen.update(orbit)
        stabilizer=[move for move in group if perm(across,*move)==across]; used=set()
        for first,second in product(words(short),repeat=2):
            if (first,second) in used or 2*(sum(first)+sum(second))>high or sum(across)+max(sum(first),sum(second))>high: continue
            images={(perm(first,unit,offset),perm(second,unit,offset-step)) for unit,step in stabilizer for offset in range(short)}
            used.update(images)
            if any(bad((weight,first[pos],second[(pos-delta)%short])) for delta,weight in enumerate(across) if weight for pos in range(short)): continue
            yield across,first,second,len(orbit)*len(images)


@lru_cache(None)
def choices(size,cross1,cross2,external,low,high):
    result=defaultdict(list)
    for layer in layers(size):
        degree=sum(layer)+external
        if low<=degree<=high and allow(layer,cross1) and allow(layer,cross2): result[degree].append(layer)
    return result


def matrix(long, small, across, first, second, inner):
    blocks=[(block,pos) for block,size in enumerate((long,long,small)) for pos in range(size)]
    cross={(0,1):across,(0,2):first,(1,2):second}
    def weight(left,right):
        (leftblock,leftpos),(rightblock,rightpos)=sorted((left,right))
        word=inner[leftblock] if leftblock==rightblock else cross[leftblock,rightblock]
        return word[(rightpos-leftpos)%len(word)]
    return [[weight(left,right) for right in blocks] for left in blocks]


def run(args):
    size,low,high,minedges={'small':(2,3,3,15),'mid':(4,4,5,45),'target':(8,4,9,161)}[args.mode]
    reps=Counter();raw=Counter(); rank=0; extras=0
    with Path(args.out).open('w') as output:
        for across,first,second,mult in crosses(size,high):
            domains=(choices(size,across,first,sum(across)+sum(first),low,high),
                choices(size,across,second,sum(across)+sum(second),low,high),
                choices(size//2,first,second,2*(sum(first)+sum(second)),low,high))
            for deg in product(*domains):
                edges=size*(deg[0]+deg[1])+size//2*deg[2]
                if edges<minedges: continue
                group=[domain[d] for domain,d in zip(domains,deg)]; count=prod(map(len,group))
                reps[deg]+=count;raw[deg]+=mult*count
                if args.stride>0 and (args.edges==0 or edges==args.edges):
                    for local in range((args.offset-rank)%args.stride,count,args.stride):
                        digits=[]; place=local
                        for domain in reversed(group): place,pos=divmod(place,len(domain));digits.insert(0,domain[pos])
                        text=encode(matrix(size,size//2,across,first,second,digits));print(rank+local,mult,text,file=output);extras+=1
                rank+=count
    for deg in sorted(reps): print(*deg,reps[deg],raw[deg])
    print('total',sum(reps.values()),sum(raw.values()),'extracted',extras)


if __name__=='__main__':
    parser=ArgumentParser(description=__doc__);parser.add_argument('mode',choices=('small','mid','target'));parser.add_argument('out');parser.add_argument('--stride',type=int,default=0);parser.add_argument('--offset',type=int,default=0);parser.add_argument('--edges',type=int,default=0);run(parser.parse_args())
