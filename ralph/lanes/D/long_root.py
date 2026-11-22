"""Glue two unrestricted P6 profiles along seven common stars, keeping both endpoints."""

import argparse
from collections import Counter,defaultdict
from itertools import combinations,product
from pathlib import Path
import time

from path_growth import ROOT,bits,read_profiles
from path_reroot import orientations
from punct_path import core_instances,decode,neighbors,pairs,profile_key


def kernel():
    edges = {(0,1)} | {(index%2,index+2) for index in range(7)} | {(index,index+1) for index in range(2,8)}
    return neighbors(9,edges)


def sections():
    for path in (list(range(2,9)),list(reversed(range(2,9)))):
        yield (1,path[0],path[2],path[4],0,path[3],path[5],path[1]),path[6]


def table(profiles):
    fixed = kernel()
    tables = []
    oriented = {profile_key(other) for profile in profiles for other in orientations(profile)}
    for pins,exception in sections():
        required = sum(1<<index for index,anchor in enumerate(pins) if anchor in fixed[exception])
        unique = 1<<(2 if exception == 8 else 8)
        masks = {mask:sum(1<<anchor for index,anchor in enumerate(pins) if mask >> index & 1) for mask in range(256)}
        buckets = defaultdict(list)
        for key in sorted(oriented):
            counts = Counter(dict(key))
            if not counts[required]:
                continue
            counts[required] -= 1
            total,hit = Counter(),Counter()
            for mask,count in counts.items():
                if count:
                    full = masks[mask]
                    common = full & ~unique
                    total[common] += count
                    if full & unique:
                        hit[common] += count
            buckets[profile_key(total)].append(hit)
        tables.append(buckets)
    return tables


def reverse(key):
    return tuple(sorted((REV[mask],count) for mask,count in key))


REV = {mask:sum(1<<(point if point<2 else 10-point) for point in bits(mask)) for mask in range(512)}


def census(profiles,cap=3):
    left,right = table(profiles)
    base = len(kernel()[2] & kernel()[8])
    joined = set()
    count = 0
    matches = 0
    for seven,items in left.items():
        for one,two in product(items,right.get(seven,())):
            matches += 1
            options = [range(max(0,one[mask]+two[mask]-total),min(one[mask],two[mask])+1) for mask,total in seven]
            for meeting in product(*options):
                if sum(meeting)+base>cap:
                    continue
                profile = {}
                for (mask,total),both in zip(seven,meeting):
                    for extension,num in ((0,total-one[mask]-two[mask]+both),(4,one[mask]-both),(256,two[mask]-both),(260,both)):
                        if num:
                            profile[mask|extension] = num
                record = profile_key(profile)
                count += 1
                joined.add(min(record,reverse(record)))
    labelled = sum(1+(row!=reverse(row)) for row in joined)
    assert labelled == count
    return joined,(len(left),len(right),len(left.keys() & right.keys()),matches,labelled)


def calibration(control=None):
    keys = set()
    seen = Counter()
    for line in (ROOT/'gluing/val/r3_7_22.g6').read_text().splitlines():
        adj = neighbors(22,decode(line))
        if {len(row) for row in adj}!={6} or max(len(left&right) for left,right in pairs(adj))>3:
            continue
        marks = set()
        for cycle,core in core_instances(adj):
            assert not cycle
            counts = Counter(sum(1<<index for index,vertex in enumerate(core) if vertex in adj[other]) for other in range(22) if other not in core)
            keys.add(profile_key(counts))
        for root in range(22):
            for other in adj[root]:
                block = (adj[root]|adj[other])-{root,other}
                paths = [(start,) for start in adj[root]-{other}]
                for _ in range(6):
                    paths = [path+(new,) for path in paths for new in (adj[path[-1]] & block)-set(path)]
                for path in paths:
                    if path[0]>path[-1]:
                        continue
                    core = (root,other)+path
                    assert all((core[second] in adj[core[first]]) == (second in kernel()[first]) for first,second in pairs(range(9)))
                    key = profile_key(Counter(sum(1<<index for index,vertex in enumerate(core) if vertex in adj[exterior]) for exterior in range(22) if exterior not in core))
                    seen[min(key,reverse(key))]+=1
    joined,info = census([dict(key) for key in keys])
    assert len(seen)>0 and set(seen)<=joined
    print('PASS smaller P7 joins: physical marks',sum(seen.values()),'distinct real profiles',len(seen),'joined candidates',len(joined),'join info',info)
    if control:
        with control.open('w') as stream:
            for row in sorted(seen):
                print(' '.join(f'{mask}:{count}' for mask,count in row),file=stream)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--out',type=Path)
    parser.add_argument('--control',type=Path)
    args=parser.parse_args()
    if not args.out:
        calibration(args.control)
    else:
        start=time.process_time()
        profiles=list(read_profiles(args.source))
        assert len(profiles)==2434
        rows,info=census(profiles)
        print('unrestricted P6 input',len(profiles),'buckets/matched/pairs/labelled',info,'P7 reflection orbits',len(rows),'CPU',time.process_time()-start)
        with args.out.open('w') as stream:
            for row in sorted(rows):
                print(' '.join(f'{mask}:{count}' for mask,count in row),file=stream)
