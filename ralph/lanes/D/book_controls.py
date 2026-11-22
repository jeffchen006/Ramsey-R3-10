"""Physical deficient-flag books, calibration, and deliberately misaligned joins."""
from collections import Counter
from itertools import combinations, permutations, product
from pathlib import Path
from functools import lru_cache
import json
import sys

from kernel_cnf import ROOT, decode


def sites(word):
    while word:
        low = word & -word
        yield low.bit_length()-1
        word -= low


def bitset(seq):
    return sum(1 << point for point in seq)


def graph_masks(text):
    rows = [0] * (ord(text[0])-63)
    for left, right in decode(text):
        rows[left] |= 1 << right
        rows[right] |= 1 << left
    return rows


def flags(rows):
    return [(left, right) for left, right in combinations(range(len(rows)), 2)
            if (rows[left] & rows[right]).bit_count() == 1]


def book(rows, ends):
    left, right = ends
    centre, = sites(rows[left] & rows[right])
    return (centre, left, right), (tuple(sites(rows[left] ^ (1 << centre))),
                                    tuple(sites(rows[right] ^ (1 << centre))))


def reorder(rows, order):
    return [bitset(idx for idx, other in enumerate(order) if rows[point] >> other & 1) for point in order]


def squares(rows, left, right):
    return sum((rows[point] & rows[right] & ~(1 << left)).bit_count() for point in sites(rows[left] & ~(1 << right)))


def realize(rows, pair):
    anchors, (left, right) = book(rows, pair)
    fill = [(anchors[0], anchors[1], first, second, anchors[2]) for first, second in product(left, right) if rows[first] >> second & 1]
    match = [perm for perm in permutations(right) if all(rows[first] >> second & 1 for first, second in zip(left, perm))]
    assert match
    return fill, match, left, right


def rectangle(left, right, rows):
    return {tuple(sorted((first, second))): bool(rows[first] >> second & 1) for first, second in product(left, right)}


def controls(dest):
    totals=Counter(); negatives=[]; panel=[]; panels=set(); positives=[]; histogram=Counter()
    for host, text in enumerate((ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines()):
        rows=graph_masks(text)
        if {row.bit_count() for row in rows} != {6} or max((left&right).bit_count() for left,right in combinations(rows,2))>3:continue
        tables={pair:realize(rows,pair) for pair in flags(rows)}
        for first,second in combinations(tables,2):
            path0, _=book(rows,first);path1,_=book(rows,second)
            if set(path0)&set(path1):continue
            fills0,match0,left0,right0=tables[first];fills1,match1,left1,right1=tables[second]
            disjoint=sum(not(set(left)&set(right)) for left,right in product(fills0,fills1));assert disjoint
            totals.update(flags=1,disjoint=disjoint,paired_matchings=len(match0)*len(match1));histogram[disjoint]+=1
            indices=(*first,*second);order=indices+tuple(sorted(set(range(22))-set(indices)));rr=reorder(rows,order)
            positives.append([host,*indices,*match0[0],*match1[0]])
            rootmask=bitset([*path0,*path1]);group={point:rows[point]&rootmask for point in range(22) if not(rootmask>>point&1)}
            leftmap=rectangle(left0,right0,rows);rightmap=rectangle(left1,right1,rows)
            for a,b in combinations(group,2):
                if group[a]!=group[b] or not ({a,b}&set(leftmap_point for edge in leftmap.keys()&rightmap.keys() for leftmap_point in edge)):continue
                swap=lambda point:b if point==a else a if point==b else point
                altered={tuple(sorted((swap(x),swap(y)))):value for (x,y),value in rightmap.items()}
                clash=sorted(edge for edge in leftmap.keys()&altered.keys() if leftmap[edge]!=altered[edge]);
                if not clash:continue
                negatives.append([host,*indices,a,b,*clash[0]]);break
            key=(host,disjoint//10)
            if key not in panels:
                panels.add(key);panel.append([host,*indices,rr]);
    assert totals['flags']==1734 and totals['disjoint']==67189 and negatives
    for name,records in [('controls',positives),('mixed',negatives),('panel',panel)]:
        (dest/(name+'.jsonl')).write_text(''.join(json.dumps(row)+'\n' for row in records))
    print('physical',dict(totals),'negative marks with a root-preserving swap',len(negatives),'fixed SAT panel',len(panel),'histogram',dict(sorted(histogram.items())))


if __name__=='__main__':controls(Path(sys.argv[1]))
