"""Unmarked matching on each selected side pool: an eleven-site book needs only a 4x4 type."""
from collections import Counter
from functools import lru_cache
from itertools import combinations,permutations,product
from pathlib import Path
import json,sys
from book_controls import bitset,book,flags,graph_masks,sites
from kernel_cnf import ROOT,decode


@lru_cache(None)
def perms(quota):return list(permutations(range(quota)))


@lru_cache(None)
def image(word,perm):return bitset(pos for pos,site in enumerate(perm) if word>>site&1)


def transpose(rows):return tuple(bitset(idx for idx,row in enumerate(rows) if row>>point&1) for point in range(len(rows)))


@lru_cache(None)
def key(rows):
    size=len(rows);rev=transpose(rows)
    if any(row.bit_count()>3 for row in rows+rev) or any((a&b).bit_count()>2 for side in (rows,rev) for a,b in combinations(side,2)):return None
    if not any(all(row>>site&1 for row,site in zip(rows,perm)) for perm in perms(size)):return None
    return min(tuple(sorted(image(row,perm) for row in side)) for side in (rows,rev) for perm in perms(size))


def planted(quota):
    occupied=Counter();parents=0;physical=0
    for line in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        graph=graph_masks(line)
        if any(row.bit_count()!=6 for row in graph) or max((a&b).bit_count()for a,b in combinations(graph,2))>3:continue
        tables={}
        for ends in flags(graph):
            path,(left,right)=book(graph,ends);alternatives=[]
            for lhs,rhs in product(combinations(left,quota),combinations(right,quota)):
                rows=tuple(bitset(idx for idx,point in enumerate(rhs) if graph[site]>>point&1) for site in lhs);typ=key(rows)
                if typ is not None:alternatives.append((bitset((*path,*lhs,*rhs)),typ))
            tables[ends]=(bitset(path),alternatives)
        for (first,left),(second,right) in combinations(tables.values(),2):
            if first&second:continue
            found=0
            for mask0,typ0 in left:
                if mask0&second:continue
                for mask1,typ1 in right:
                    if mask0&mask1:continue
                    occupied[tuple(sorted((typ0,typ1)))]+=1;found+=1
            parents+=bool(found);physical+=found
    return parents,physical,occupied


def run(folder):
    for quota in [2,3,4]:
        catalog=Counter()
        for rows in product(range(1<<quota),repeat=quota):
            typ=key(rows)
            if typ is not None:catalog[typ]+=1
        if quota==4:
            second=set()
            for raw in (folder/'genbg44.g6').read_text().splitlines():
                edges=decode(raw);rows=tuple(bitset(rhs-quota for lhs,rhs in edges if lhs==first) for first in range(quota));typ=key(rows)
                if typ is not None:second.add(typ)
            assert second==set(catalog)
        print('quota',quota,'labelled',sum(catalog.values()),'one-book types',len(catalog),'unordered pairs',len(catalog)*(len(catalog)+1)//2,'edge counts',dict(sorted(Counter(sum(x.bit_count()for x in typ)for typ in catalog).items())),flush=True)
        (folder/f'booktypes{quota}.tsv').write_text(''.join('\t'.join(map(str,(*typ,size)))+'\n'for typ,size in sorted(catalog.items())))
        if quota<=3:
            parents,physical,occupied=planted(quota);assert parents=={2:1734,3:783}[quota] and all(a in catalog and b in catalog for a,b in occupied);print('C22 planted quota',quota,'marks',parents,'unmatched pool choices',physical,'occupied type pairs',len(occupied),flush=True)


if __name__=='__main__':run(Path(sys.argv[1]))
