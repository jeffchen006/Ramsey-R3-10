"""Count compatible adjacent-deletion joins of P7s on a C8 kernel."""

import argparse
from collections import Counter,defaultdict
from itertools import product
from pathlib import Path

from long_root import reverse
from path_growth import bits,read_profiles
from punct_path import profile_key


def catalog(profiles):
    keys={key for profile in profiles for key in (profile_key(profile),reverse(profile_key(profile))) if profile.get(262)==1}
    tables=[]
    for pins,unique in ((tuple(range(9)),2),((1,0,3,4,5,6,7,8,9),9)):
        mapped={mask:sum(1<<pins[index] for index in bits(mask)) for mask in range(512)}
        groups=defaultdict(list)
        for key in keys:
            total=Counter();hit=Counter()
            for mask,size in key:
                if mask==262:
                    continue
                full=mapped[mask];both=full&~(1<<unique)
                total[both]+=size
                if full&(1<<unique):
                    hit[both]+=size
            signature=profile_key(total)
            groups[signature].append(tuple(hit[mask] for mask,_ in signature))
        tables.append(groups)
    return keys,tables


def joins(groups,table_right):
    for common,options in groups:
        if common not in table_right:
            continue
        for left,right in product(options,table_right[common]):
            row={}
            for (mask,total),low,high in zip(common,left,right):
                shared=total-low-high
                if shared<0:
                    break
                if shared:row[mask]=shared
                if low:row[mask|4]=low
                if high:row[mask|512]=high
            else:
                yield profile_key(row)


def deletions(key):
    for skip in range(8):
        counts=Counter({262:1})
        mapping=DELETION_MAPS[skip]
        for mask,size in key:
            counts[mapping[mask]]+=size
        yield profile_key(counts)


def lookup():
    tables=[]
    for skip in range(8):
        start=(skip+1)%8
        pins=(start%2,1-start%2)+tuple(2+(start+step)%8 for step in range(7))
        tables.append([sum(1<<index for index,anchor in enumerate(pins) if mask>>anchor&1) for mask in range(1024)])
    return tables


DELETION_MAPS=lookup()


def dihedral():
    for shift in range(8):
        for step in (-1,1):
            perm=(shift%2,1-shift%2)+tuple(2+(shift+step*point)%8 for point in range(8))
            yield [sum(1<<perm[point] for point in bits(mask)) for mask in range(1024)]


SYMMETRIES=list(dihedral())


def count(source,sample,out):
    profiles=list(read_profiles(source));keys,(left,right)=catalog(profiles)
    groups=sorted(left.items());total=sum(len(opts)*len(right.get(common,[])) for common,opts in groups)
    print('oriented',len(keys),'buckets',len(groups),'candidate pairs',total,flush=True)
    if sample:
        groups=groups[::sample]
    possible=sum(len(opts)*len(right.get(common,[])) for common,opts in groups)
    combined=coherent=0
    reps=set()
    for row in joins(groups,right):
        combined+=1
        if all(view in keys for view in deletions(row)):
            coherent+=1
            if out:
                reps.add(min(tuple(sorted((mapping[mask],size) for mask,size in row)) for mapping in SYMMETRIES))
    print('sample stride',sample,'pairs',possible,'compatible adjacent joins',combined,'all eight views present',coherent,flush=True)
    if out:
        assert not sample
        rebuilt=sum(len({tuple(sorted((mapping[mask],size) for mask,size in row)) for mapping in SYMMETRIES}) for row in reps)
        assert rebuilt==coherent
        out.write_text(''.join(' '.join(f'{mask}:{size}' for mask,size in row)+'\n' for row in sorted(reps)))
        print('dihedral representatives',len(reps),'orbit sum',rebuilt,flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--stride',type=int,default=0)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    count(args.source,args.stride,args.out)
