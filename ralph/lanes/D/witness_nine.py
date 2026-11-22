"""Exact joins of surviving induced P8 ends to P9 stars; includes the common root."""
from collections import Counter,defaultdict
from itertools import product
from pathlib import Path
import sys
from induced_pilot import flip,graph_key,line,mapping,planted
from path_growth import read_profiles
from punct_path import profile_key


def join(source,dest,limit,width=10,stride=1):
    sibling=1<<width;skip=1+(1<<(width-1));full=(2*sibling)-1;ends=4|sibling;shared=full^ends;reflect=mapping((0,1,*range(width,1,-1)),2*sibling)
    source_flip=mapping((1,0,*range(width-1,1,-1)),sibling)
    transforms=[mapping(tuple(range(width)),sibling),mapping((0,1,*range(width,2,-1)),sibling)]
    tables=[defaultdict(list),defaultdict(list)]
    oriented=set()
    for index,row in enumerate(read_profiles(source)):
        key=profile_key(row)
        for direction,key in enumerate(sorted({key,tuple(sorted((source_flip[mask],num) for mask,num in key))})):
            if key in oriented or (skip,1) not in key:continue
            oriented.add(key)
            for side,trans in enumerate(transforms):
                hist=Counter();marks=Counter();tip=1<<(2 if side==0 else width)
                for mask,num in key:
                    if mask==skip:continue
                    value=trans[mask];cell=value&shared;hist[cell]+=num
                    if value&tip:marks[cell]+=num
                common=profile_key(hist);tables[side][common].append((2*index+direction,[marks[c] for c,num in common]))
    groups=sorted(tables[0].keys()&tables[1].keys());pairs=sum(len(tables[0][g])*len(tables[1][g]) for g in groups);print('shared fingerprints',len(groups),'matched pairs',pairs,flush=True)
    if pairs>limit:return
    labelled=kept=fixed=ordinal=tested=0
    with dest.open('w') as out:
        for common in groups:
            for (lid,left),(rid,right) in product(tables[0][common],tables[1][common]):
                ordinal+=1
                if (ordinal-1)%stride:continue
                tested+=1
                lows=[max(0,a+b-n) for (_,n),a,b in zip(common,left,right)];free=[min(a,b)-low for a,b,low in zip(left,right,lows)];slots=2-sum(lows)
                if slots<0:continue
                def choose(start,remain):
                    nonlocal labelled,kept,fixed
                    both=[mask for (mask,_),num in zip(common,lows) for j in range(num)]
                    if all((a&b).bit_count()<=1 for idx,a in enumerate(both)for b in both[:idx]):
                        labelled+=1
                        if lid<=rid:
                            row=tuple(sorted((mask|extra,num) for (mask,size),a,b,t in zip(common,left,right,lows) for extra,num in ((0,size-a-b+t),(4,a-t),(sibling,b-t),(ends,t)) if num))
                            other=tuple(sorted((reflect[mask],num) for mask,num in row))
                            if lid<rid or row<=other:out.write(line(row)+'\n');kept+=1;fixed+=row==other
                    if not remain:return
                    for idx in range(start,len(free)):
                        if not free[idx]:continue
                        free[idx]-=1;lows[idx]+=1;choose(idx,remain-1);free[idx]+=1;lows[idx]-=1
                choose(0,slots)
    if stride==1:assert labelled==2*kept-fixed
    print('tested pairs',tested,'labelled',labelled,'orbits retained',kept,'fixed',fixed)


if __name__=='__main__':join(Path(sys.argv[1]),Path(sys.argv[2]),*map(int,sys.argv[3:]))
