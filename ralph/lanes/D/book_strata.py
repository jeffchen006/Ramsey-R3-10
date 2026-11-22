"""Independent dense-boundary draws, literal small controls, and pre-LP gates."""
from collections import Counter
from functools import lru_cache
from itertools import combinations, product
from pathlib import Path
from random import Random
from time import process_time
import json, sys
from book_contacts import standard, scores
from book_controls import sites, bitset, reorder, book, graph_masks, rectangle
from kernel_cnf import ROOT

OLD = ROOT/'scratch/D/join13'
DEST = ROOT/'scratch/D/book14'
TYPES = [json.loads(line)[0] for line in (OLD/'book-footprints.jsonl').read_text().splitlines()]
PAIRS = ((35,35),(0,0),(6,25),(13,32))
TOTALS = (20,26,32,38)


def independent_sets(rows):
    def walk(word, pool):
        yield word
        while pool:
            bit=pool&-pool;pool^=bit
            yield from walk(word|bit,pool&~rows[bit.bit_length()-1])
    return list(walk(0,(1<<len(rows))-1))


def local(rows, weak, degree):
    return all(star.bit_count()<=degree for star in rows) and all((rows[a]&rows[b]).bit_count() <= (0 if rows[a]>>b&1 else 1 if (a,b) in weak else 3) for a,b in combinations(range(len(rows)),2))


def draw(first,second,total,seed):
    rows=standard(TYPES[first])+[word<<11 for word in standard(TYPES[second])];rng=Random(seed);edges=list(product(range(11),range(11,22)));rng.shuffle(edges);count=0
    for left,right in edges:
        rows[left]|=1<<right;rows[right]|=1<<left
        if local(rows,{(1,2),(12,13)},9):
            count+=1
            if count==total:return rows
        else:rows[left]^=1<<right;rows[right]^=1<<left


def signature(rows,points):
    return tuple(bitset(idx for idx,other in enumerate(points) if rows[site]>>other&1) for site in points),Counter(bitset(idx for idx,other in enumerate(points) if rows[site]>>other&1) for site in range(len(rows)) if site not in points)


@lru_cache(None)
def library():
    source=(OLD.parent/'ind10/four-40.in').read_text().splitlines();roster={line for line in (OLD/'four-star101.in').read_text().splitlines()};result=[]
    orders=set()
    for first,second in (((0,1),(2,3)),((2,3),(0,1))):
        for lhs,rhs in product((first,first[::-1]),(second,second[::-1])):orders.add(lhs+rhs)
    for idx,line in enumerate(source):
        if line not in roster:continue
        frame=list(map(int,line.split()))[1:];seen=set()
        for order in sorted(orders):
            fixed,counts=signature(frame,order);key=(fixed,tuple(sorted(counts.items())))
            if key not in seen:seen.add(key);result.append((idx,order,fixed,counts))
    assert len({row[0] for row in result})==101;return result


def root_fits(rows):
    fixed,used=signature(rows,(1,2,12,13));return [(idx,order) for idx,order,header,counts in library() if fixed==header and used<=counts]


@lru_cache(None)
def thresholds(internal,degree,pop):return [(word,bound-pop) for word,bound in enumerate(scores(internal,degree)) if bound>pop]


def gates(rows,degree,order):
    half=len(rows)//2;side=(1<<half)-1;internal=[tuple((row>>off)&side for row in rows[off:off+half]) for off in (0,half)];cross=[tuple((row>>(half-off))&side for row in rows[off:off+half]) for off in (0,half)]
    def touched(word,stars):
        result=0
        for site in sites(word):result|=stars[site]
        return result
    maxsets=[[word for word in independent_sets(graph) if word.bit_count()==(half-1)//2] for graph in internal];direct=next(((left,right) for left in maxsets[0] for forbidden in [touched(left,cross[0])] for right in maxsets[1] if not(right&forbidden) and (left|right<<half).bit_count()>degree),None)
    footprint=next(((idx,word,need,touched(word,cross[idx]).bit_count()) for idx in (0,1) for word,need in thresholds(internal[idx],degree,order-2*half) if touched(word,cross[idx]).bit_count()<need),None)
    return direct,footprint


def plants():
    for (key,_,truth),result in zip(map(json.loads,(OLD/'cal.in').read_text().splitlines()),map(json.loads,(OLD/'cal-pack2.jsonl').read_text().splitlines()),strict=True):
        blocks=[]
        for ends,petals in zip(((0,1),(2,3)),result['bouquet']):blocks.extend([*book(truth,ends)[0],*[pair[0] for pair in petals],*[pair[1] for pair in petals]])
        yield key,reorder(truth,blocks+sorted(set(range(22))-set(blocks))),len(blocks)


def cal():
    samples=0
    for _,truth,width in plants():
        lower=(1<<width)-1;boundary=[row&lower for row in truth[:width]];exterior=[row>>width for row in truth[width:]];assert gates(boundary,6,22)==(None,None);assert sum(row.bit_count() for row in exterior)-sum(row.bit_count() for row in boundary)==6*(22-2*width);samples+=1
    lines=(ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines();negative=0
    for host,a,b,c,d,left,right,one,two in map(json.loads,(OLD/'mixed.jsonl').read_text().splitlines()):
        graph=graph_masks(lines[host]);lhs=rectangle(*book(graph,(a,b))[1],graph);rhs=rectangle(*book(graph,(c,d))[1],graph);swap=lambda site: right if site==left else left if site==right else site;assert lhs[one,two]!=rhs[tuple(sorted([swap(one),swap(two)]))];negative+=1
    assert samples==18 and negative==1106;print('PASS C22 planted boundaries, footprints, alpha and edge identities:',samples,'mislabelled physical joins rejected:',negative)


def generate(extra=False):
    pair_roster={tuple(map(int,line.split())) for line in (OLD/'pairs-general.tsv').read_text().splitlines()};assert all(pair in pair_roster for pair in PAIRS);started=process_time()
    for block,(first,second) in enumerate(((1,35),(15,25)) if extra else PAIRS):
        for total in ((22,25,28) if extra else TOTALS):
            for replicate in range(6):
                seed=(15000000 if extra else 14000000)+block*100000+total*1000+replicate*100;record=dict(pair=[first,second],holdout=extra or block==3,cross=total,rep=replicate)
                for attempt in range(100):
                    graph=draw(first,second,total,seed+attempt)
                    if graph is not None:break
                record.update(tries=attempt+1,rows=graph)
                if graph is not None:
                    direct,foot=gates(graph,9,40);fits=root_fits(graph);record.update(direct=direct,foot=foot,roots=sorted({idx for idx,_ in fits}))
                print(json.dumps(record,separators=(',',':')),flush=True)
    print('generator and gates CPU',process_time()-started,file=sys.stderr)


if __name__=='__main__':cal() if sys.argv[1]=='cal' else generate(sys.argv[1]=='extra')
