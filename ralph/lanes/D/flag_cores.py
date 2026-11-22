"""Freeze all endpoints of the exact four non-star flags, omitting centre labels."""
from collections import Counter
from itertools import combinations,permutations
from pathlib import Path
import json
import sys
from flag_shapes import key


def census(order,degree,defects,types):
    width=max(max(pair) for pair in defects)+1
    pairs=list(combinations(range(width),2))
    masks=[(1<<left)|(1<<right) for left,right in pairs]
    defect_masks={1<<left|1<<right for left,right in defects}
    perm=[order for order in permutations(range(width)) if {tuple(sorted((order[left],order[right]))) for left,right in defects}==set(defects)]
    transforms=[[sum(1<<image[vertex] for vertex in range(width) if mask>>vertex&1) for mask in range(1<<width)] for image in perm]
    optional=[mask for mask in masks if mask not in defect_masks]
    seen=set();lab=Counter();full=[]
    for integer in range(1<<len(optional)):
        core=[0]*width
        for idx,mask in enumerate(optional):
            if integer>>idx&1:
                for vertex in range(width):
                    if mask>>vertex&1:core[vertex]|=mask^(1<<vertex)
        base=[(core[left]&core[right]).bit_count() for left,right in pairs]
        lo=[0 if core[left]>>right&1 else 1 if mask in defect_masks else 2 for (left,right),mask in zip(pairs,masks)]
        hi=[0 if core[left]>>right&1 else 1 if mask in defect_masks else 3 for (left,right),mask in zip(pairs,masks)]
        if any(value>cap for value,cap in zip(base,hi)):continue
        hist=[0]*(1<<width);slots=[mask for mask in range(1<<width) if mask.bit_count()>=3 and all(not(mask>>vertex&1 and mask&core[vertex]) for vertex in range(width))];slots.sort(key=int.bit_count,reverse=True)
        slots+=masks;indices=[[idx for idx,pair in enumerate(masks) if pair&mask==pair] for mask in slots]
        def generate(pos):
            if pos<len(slots):
                mask=slots[pos];ids=indices[pos];low=max(0,lo[ids[0]]-base[ids[0]]) if mask.bit_count()==2 else 0
                high=min(hi[idx]-base[idx] for idx in ids)
                if mask.bit_count()==2 and hi[ids[0]]==0:high=0
                for mult in range(low,high+1):
                    hist[mask]=mult
                    for idx in ids:base[idx]+=mult
                    generate(pos+1)
                    for idx in ids:base[idx]-=mult
                hist[mask]=0;return
            for vertex in range(width):hist[1<<vertex]=degree-core[vertex].bit_count()-sum(hist[mask] for mask in slots if mask>>vertex&1)
            hist[0]=order-width-sum(hist[1:])
            if min(hist)<0:return
            graph=core.copy()
            for mask,num in enumerate(hist):
                for _ in range(num):
                    for vertex in range(width):
                        if mask>>vertex&1:graph[vertex]|=1<<len(graph)
                    graph.append(mask)
            flags=[]
            for left,right in defects:
                centre=graph[left]&graph[right];assert centre.bit_count()==1
                flags.append((left,centre.bit_length()-1,right))
            if any(not set(left)&set(right) for left,right in combinations(flags,2)) or set.intersection(*map(set,flags)):return
            vertices=sorted(set().union(*map(set,flags)));family=tuple(tuple(vertices.index(point) for point in flag) for flag in flags)
            shape=types[key(family)];lab[shape]+=1
            fields=tuple((mask,size) for mask,size in enumerate(hist) if size)
            marker=min((tuple(sorted(image[mask] for idx,mask in enumerate(optional) if integer>>idx&1)),tuple(sorted((image[mask],num) for mask,num in fields))) for image in transforms)
            if marker in seen:return
            seen.add(marker);low_rows=[0]*order
            for left,right in defects:low_rows[left]|=1<<right;low_rows[right]|=1<<left
            full.append((shape,graph,low_rows))
        generate(0)
    return full,lab


def run(dest):
    types={key(family):idx for idx,family in enumerate(family for family in json.loads((dest/'abstract.json').read_text()) if len(family)==4)}
    with (dest/'nonstar.in').open('w') as raw,(dest/'nonstar.ids').open('w') as names:
        for defects in [((0,1),(1,2),(2,3),(3,4)),((0,1),(1,2),(1,3),(2,3))]:
            full,lab=census(40,9,defects,types);width=1+max(map(max,defects))
            print('width',width,'labelled',sorted(lab.items()),'orbits',sorted(Counter(row[0] for row in full).items()),flush=True)
            for idx,(shape,graph,low) in enumerate(full):
                print(2**width-1,*graph,*low,file=raw);print(width,shape,idx,file=names)


if __name__=='__main__':run(Path(sys.argv[1]))
