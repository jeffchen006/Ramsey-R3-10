from collections import Counter
from itertools import combinations,permutations
import json
from pathlib import Path
import sys

import numpy as np

from prefix22 import TARGET,inventory
from m14queue22 import BASE
from triple18_price import shore_words


def audit(key,repair=False):
    cached=TARGET/(key+'.json');old=json.loads(cached.read_text());new=json.loads(json.dumps(inventory(key)));assert old['heads']==new['heads'] and old['per_head_profiles']==new['per_head_profiles'] and old['orbits']==new['orbits'] and old['group']==new['group'];assert all(new['fixed'][tag]==old['fixed'].get(tag,0) for tag in new['fixed']);assert all(new['per_head_fixed'][head][tag]==old['per_head_fixed'][head].get(tag,0) for head in new['per_head_fixed'] for tag in new['fixed']);assert len(new['fixed'])==new['group']
    record=json.loads((BASE/'roster.jsonl').read_text().splitlines()[int(key.split('_')[1])-1]);kind=key[0];margins=([1]+[2]*6,[1]+[2]*6) if kind=='D' else ([1,1]+[2]*5,[2]*7) if kind=='S' else ([1]+[2]*6,[2,1]+[2]*5)
    pairs=list(combinations(range(7),2));masks=[1<<left|1<<right for left,right in pairs];universe=(1<<len(pairs))-1;weights=np.array([1<<position for position in range(len(pairs))],dtype=np.int64)
    sides=[np.array([list(word) for word in shore_words(pairs,margin,sum(margin)-8)],dtype=np.uint8) for margin in margins];heads=np.max((sides[0]>0)*np.array(masks),axis=1)
    columns=np.array(record['pairs'])+np.array([sum(mask&triple==mask for triple in record['triples']) for mask in masks]);assert max(columns)<=2
    left,right=[((array>=1)@weights,(array>=2)@weights) for array in sides];host=Counter(record['triples']+[mask for mask,multi in zip(masks,record['pairs']) for _ in range(multi)]);tags=[]
    for perm in permutations(range(7)):
        if any(margin[site]!=margin[dst] for margin in margins for site,dst in enumerate(perm)):continue
        def image(mask):return sum(1<<dst for site,dst in enumerate(perm) if mask>>site&1)
        if Counter({image(mask):multi for mask,multi in host.items()})!=host:continue
        tag=''.join(map(str,perm));tags.append(tag);move=[masks.index(image(mask)) for mask in masks];selected=[np.all(side==side[:,move],axis=1) for side in sides];observed=Counter()
        for index in np.flatnonzero(selected[0]):
            first=left[0][index];twice=left[1][index];known=(columns>=1)@weights;heavy=(columns>=2)@weights
            if (twice&known) or (first&heavy):continue
            positive=known|first;saturated=heavy|twice|(known&first);valid=selected[1]&((right[0]|positive)==universe)&((right[0]&saturated)==0)&((right[1]&positive)==0);observed[int(heads[index])]+=int(np.count_nonzero(valid))
        assert all(new['per_head_fixed'][str(head)][tag]==observed[head] for head in new['heads']) and sum(observed.values())==new['fixed'][tag]
    assert len(tags)==new['group'] and set(tags)==set(new['fixed']) and new['per_head_profiles']==dict(Counter(map(str,heads)))
    if repair:cached.write_text(json.dumps(new,sort_keys=True)+'\n')
    else:assert new==old
    print(key,len(tags),len(new['heads']),new['fixed']['0123456'],new['orbits'],'all prefix by action cells literal-aligned',flush=True)


if __name__=='__main__':
    repair='--repair' in sys.argv[1:]
    for key in sys.argv[1:]:
        if key!='--repair':audit(key,repair)
