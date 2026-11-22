"""Count unordered overlap placements without generating child keys; audit both deletions."""
import argparse
from collections import Counter
from hashlib import blake2b
from pathlib import Path
from induced_pilot import catalog,flip,line,mapping
from hub_lift import shapes
from long_root import reverse
from path_growth import read_profiles
from punct_path import profile_key


def ways(common,left,right,limit=3,minimum=1):
    mandatory=[];options=[]
    for (mask,size),first,second in zip(common,left,right):
        low=max(0,first+second-size);high=min(first,second)
        if low:mandatory.extend([mask]*low)
        if high>low:options.append((mask,high-low))
    if len(mandatory)>limit or any((a&b).bit_count()>1 for i,a in enumerate(mandatory) for b in mandatory[:i]):return 0
    def extend(start,selected):
        total=int(len(selected)>=minimum)
        if len(selected)==limit:return total
        for idx in range(start,len(options)):
            mask,capacity=options[idx]
            if any((mask&other).bit_count()>1 for other in selected):continue
            if selected.count(mask)-mandatory.count(mask)>=capacity:continue
            total+=extend(idx,selected+[mask])
        return total
    return extend(0,mandatory)


def run(source,children):
    halves,_=catalog(source);joined=0;pairs=0;keys=0
    for common in halves[0].keys()&halves[1].keys():
        for _,left in halves[0][common]:
            for _,right in halves[1][common]:pairs+=1;joined+=ways(common,left,right)
    print('independent small-multiset overlap count: parent pairs',pairs,'labelled profiles',joined,flush=True)
    allowed=set()
    for row in read_profiles(source):
        key=profile_key(row);allowed.add(key);allowed.add(reverse(key))
    mapped=[]
    for pins in shapes(10):
        omitted,=set(range(10))-set(pins);transform=[sum(1<<pos for pos,anchor in enumerate(pins) if mask>>anchor&1) for mask in range(1024)];extra=transform[(1<<(omitted%2))|(1<<(3 if omitted==2 else omitted-1))];mapped.append((transform,extra))
    seen=set();symmetric=0
    for row in read_profiles(children):
        key=profile_key(row);swapped=flip(key);symmetric+=key==swapped;digest=blake2b(line(min(key,swapped)).encode(),digest_size=16).digest();assert digest not in seen;seen.add(digest);keys+=1
        for transform,extra in mapped:
            marginal=Counter({extra:1})
            for mask,number in key:marginal[transform[mask]]+=number
            assert profile_key(marginal) in allowed
        witnesses=[mask&~516 for mask,num in key if mask&516==516 for k in range(num)];assert 1<=len(witnesses)<=3 and not any((a&b).bit_count()>1 for i,a in enumerate(witnesses) for b in witnesses[:i])
    assert 2*keys-symmetric==joined
    print('PASS two actual parent deletions on all',keys,'distinct reversal-orbits;',symmetric,'self-reversing; 2*orbits-fixed matches independent labelled count')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('source',type=Path);parser.add_argument('children',type=Path);args=parser.parse_args();run(args.source,args.children)
