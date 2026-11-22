"""Small positive certificates for two simultaneous matchings on disjoint site pools."""
from itertools import product
from pathlib import Path
from time import process_time
import argparse
import json
from book_controls import book,sites,bitset


def upper(frame):
    fixed,*graph=frame;order=len(graph)
    return [row if fixed>>point&1 else row|bitset(other for other in range(order) if point!=other and not fixed>>other&1 and not(row&graph[other]&fixed)) for point,row in enumerate(graph)]


def catalogue(frame,full,quota):
    fixed,*graph=frame;order=len(graph);degree=graph[0].bit_count();may=upper(frame);paths=[];pools=[]
    for ends in ((0,1),(2,3)):
        path,groups=book(graph,ends);paths.append(bitset(path));pools.append(bitset((*groups[0],*groups[1])))
    core=paths[0]|paths[1];assert core.bit_count()==6;pools=[pool&~core for pool in pools]
    result=[]
    for pool in pools:
        table={}
        def visit(seed,live,allowed):
            need=degree+quota-seed.bit_count()
            if allowed.bit_count()>=need and (allowed not in table or table[allowed].bit_count()<seed.bit_count()):table[allowed]=seed
            while live:
                site=live&-live;live^=site;point=site.bit_length()-1
                future=allowed&~(may[point]|site);candidates=live&~may[point]
                if future.bit_count()+seed.bit_count()+1+min(9-seed.bit_count()-1,candidates.bit_count())>=degree+quota:visit(seed|site,candidates,future)
        visit(0,(1<<order)-1 if full else core,pool);result.append(table)
    return result


def prove(frame,quota,full):
    degree=frame[1].bit_count();left,right=catalogue(frame,full,quota)
    for (pool0,seed0),(pool1,seed1) in product(left.items(),right.items()):
        required=[degree+quota-seed.bit_count() for seed in (seed0,seed1)]
        if (pool0|pool1).bit_count()<sum(required):continue
        common=pool0&pool1;first=pool0&~common
        for site in sites(common):
            if first.bit_count()>=required[0]:break
            first|=1<<site
        second=pool1&~first;assert first.bit_count()>=required[0] and second.bit_count()>=required[1]
        return [seed0,first,seed1,second]


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('input',type=Path);parser.add_argument('quota',type=int);parser.add_argument('--full',action='store_true');args=parser.parse_args()
    for key,frame,truth in map(json.loads,args.input.read_text().splitlines()):
        start=process_time();record=prove(frame,args.quota,args.full);print(json.dumps(dict(id=key,certificate=record,cpu=process_time()-start),separators=(',',':')),flush=True)
