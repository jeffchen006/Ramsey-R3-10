"""Lift end-deletion restrictions for rooted paths with an individualized vertex."""

import argparse
from collections import Counter,defaultdict
from pathlib import Path

from induced_pilot import graph_key,line,mapping,planted
from long_overlap import placements
from path_growth import read_profiles
from punct_path import profile_key


def shapes(size):
    path=list(range(2,size));forward=tuple(range(size-1));reverse=(int(len(path)%2==0),int(len(path)%2!=0),*reversed(path[1:]))
    return (forward,reverse)


def code(key,where,size):
    if where<size:return where
    start=size
    for mask,num in key:
        if where<start+num:return size+mask
        start+=num
    raise AssertionError(where)


def rows(source,size):
    flip=(int(size%2==0),int(size%2!=0),*reversed(range(2,size)));mapped=mapping(flip,1<<size)
    offers=defaultdict(set)
    for text in source.read_text().splitlines():
        items=text.split();site=int(items[0]).bit_length()-1;key=tuple(tuple(map(int,field.split(':'))) for field in items[1:]);mark=code(key,site,size)
        offers[key].add(mark);other=tuple(sorted((mapped[mask],num)for mask,num in key));offers[other].add(flip[mark] if mark<size else size+mapped[mark-size]);
    return offers


def survey(source,library,size,dest):
    offers=rows(library,size-1);maps=[]
    for pins in shapes(size):
        omitted,=set(range(size))-set(pins)
        transform=[sum(1<<index for index,point in enumerate(pins) if mask>>point&1)for mask in range(1<<size)]
        adjacent=(1<<(omitted%2))|(1<<(3 if omitted==2 else omitted-1))
        maps.append((pins,omitted,transform,transform[adjacent]))
    seen=kept=marks=both=0
    with dest.open('w')as output:
        for row in read_profiles(source):
            key=profile_key(row);seen+=1;profiles=[]
            for pins,omitted,transform,extra in maps:
                marginal=Counter({extra:1})
                for mask,num in key:marginal[transform[mask]]+=num
                options=offers.get(profile_key(marginal))
                if not options:break
                profiles.append((pins,transform,extra,options))
            if len(profiles)!=2:continue
            both+=1;start=size;ext=[]
            for mask,num in key:ext.append((size+mask,start));start+=num
            found=False
            for mark,site in [(point,point) for point in range(size)]+ext:
                if all((pins.index(mark) if mark in pins else size-1+(extra if mark<size else transform[mark-size])) in options for pins,transform,extra,options in profiles):
                    print(1<<site,line(key),file=output);marks+=1;found=True
            kept+=int(found)
    print('size',size,'source',seen,'both marginal keys',both,'common hub',kept,'marked roots',marks)


def control(dest):
    actual=defaultdict(set);directed=0
    from induced_pilot import ROOT
    from punct_path import decode,neighbors,pairs
    for text in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=neighbors(22,decode(text))
        if {len(row)for row in graph}!={6}or max(len(left&right)for left,right in pairs(graph))>3:continue
        for pins in placements(graph):
            directed+=1
            for core in (pins,(*pins[:2],*reversed(pins[2:]))):
                key=graph_key(graph,core);actual[key]|=set(range(9))|{9+mask for mask,_ in key}
    assert directed==155
    source=dest/'hub-cal7.tsv';source.write_text(''.join(line(key)+'\n' for key in sorted(actual)));survey(source,dest/'hub-cal.tsv',9,dest/'hub-lift-cal.tsv');assert dict(rows(dest/'hub-lift-cal.tsv',9))==dict(actual)
    eight={}
    for graph,pins in planted():
        for core in (pins,(pins[1],pins[0],*reversed(pins[2:]))):
            key=graph_key(graph,core);eight[key]=set(range(10))|{10+mask for mask,_ in key}
    source=dest/'hub-cal8.tsv';source.write_text(''.join(line(key)+'\n'for key in sorted(eight)));survey(source,dest/'hub-lift-cal.tsv',10,dest/'hub-lift8-cal.tsv');assert dict(rows(dest/'hub-lift8-cal.tsv',10))==eight
    print('PASS C22 155 P7 and 31 P8 marks, all hub sites in both orientations against direct child-deletion census')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=Path);parser.add_argument('--size',type=int);parser.add_argument('--library',type=Path);parser.add_argument('--out',type=Path);args=parser.parse_args()
    survey(args.source,args.library,args.size,args.out) if args.size else control(args.source)
