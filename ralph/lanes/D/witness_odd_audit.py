"""Rebuild odd-path parent buckets by deleting actual endpoint sites; verify every output."""
from collections import Counter,defaultdict
from hashlib import sha256
from pathlib import Path
import sys
from induced_pilot import line
from path_growth import read_profiles
from punct_path import profile_key
from witness_join_audit import ways


def reindex(mask,order):return sum(1<<position for position,old in enumerate(order) if mask>>old&1)


def run(source,children,width):
    parent_sets=set();ordered=[1,0,*range(width-1,1,-1)];mirror=[reindex(mask,ordered) for mask in range(1<<width)];extra=1+(1<<(width-1))
    for row in read_profiles(source):
        key=profile_key(row);parent_sets.add(key);parent_sets.add(tuple(sorted((mirror[m],n) for m,n in key)))
    offered=defaultdict(list);positions=[0,1,*range(3,width)];encode=[reindex(mask,positions) for mask in range(1<<width)];decode=[reindex(mask,[0,1,*range(len(positions)-1,1,-1)])for mask in range(1<<len(positions))]
    for key in parent_sets:
        if (extra,1) not in key:continue
        histogram=Counter();contains=Counter()
        for mask,cnt in key:
            if mask==extra:continue
            histogram[encode[mask]]+=cnt
            if mask&4:contains[encode[mask]]+=cnt
        offered[profile_key(histogram)].append(contains)
    labelled=pair_count=0
    for common,firsts in offered.items():
        opposite=tuple(sorted((decode[mask],n)for mask,n in common));seconds=offered.get(opposite,());pair_count+=len(firsts)*len(seconds)
        for first in firsts:
            for second in seconds:labelled+=ways(common,[first[m]for m,n in common],[second[decode[m]]for m,n in common],2,0)
    seen=set();sym=0;reverse=[0,1,*range(width,1,-1)];backwards=[reindex(mask,reverse) for mask in range(2<<width)];left=[mask&((1<<width)-1) for mask in range(2<<width)];right=[mask&((1<<width)-1) for mask in backwards]
    for row in read_profiles(children):
        key=profile_key(row);other=tuple(sorted((backwards[m],n) for m,n in key));sym+=key==other;digest=sha256(line(min(key,other)).encode()).digest();assert digest not in seen;seen.add(digest)
        for trans in (left,right):
            test=Counter({extra:1})
            for mask,num in key:test[trans[mask]]+=num
            assert profile_key(test) in parent_sets
        overlap=[mask&~(4|(1<<width))for mask,num in key if mask&4 and mask>>width&1 for idx in range(num)];assert len(overlap)<=2 and not any((a&b).bit_count()>1 for i,a in enumerate(overlap) for b in overlap[:i])
    assert labelled==2*len(seen)-sym;print('PASS deleted-site buckets',pair_count,'parent pairs,',labelled,'labelled,',len(seen),'distinct orbits,',sym,'self-reversing; both end parents independently bound')


if __name__=='__main__':run(Path(sys.argv[1]),Path(sys.argv[2]),int(sys.argv[3]))
