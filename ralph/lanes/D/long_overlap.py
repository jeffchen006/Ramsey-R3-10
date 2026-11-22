"""Rerooted nine-star fingerprint relation for a library of P7 profiles."""

import argparse
from collections import Counter,defaultdict
from pathlib import Path

from long_root import kernel,reverse
from path_growth import bits,read_profiles
from punct_path import profile_key


def graph_for(profile):
    graph=kernel()
    for mask,size in sorted(profile.items()):
        for _ in range(size):
            row=set(bits(mask))
            for point in row:
                graph[point].add(len(graph))
            graph.append(row)
    return graph


def placements(graph):
    for src,neighbors in enumerate(graph):
        for dst in sorted(neighbors):
            block=(graph[src]|graph[dst])-{src,dst}
            walks=[(point,) for point in graph[src]-{dst}]
            for _ in range(6):
                walks=[walk+(vertex,) for walk in walks for vertex in (graph[walk[-1]] & block)-set(walk)]
            for path in walks:
                if path[0]<path[-1]:
                    yield (src,dst)+path


def demands(graph,frozen):
    result=set()
    for core in placements(graph):
        keep=sum(1<<index for index,point in enumerate(core) if point in frozen)
        counts=Counter(sum(1<<index for index,point in enumerate(core) if point in frozen and vertex in graph[point]) for vertex in range(len(graph)) if vertex not in core)
        result.add((keep,profile_key(counts)))
    return result


def fingerprints(key,keep):
    counts=Counter()
    for mask,size in key:
        counts[mask&keep]+=size
    return profile_key(counts)


def fixed_point(profiles):
    requests=[demands(graph_for(profile),set(range(9))) for profile in profiles]
    keeps=sorted({keep for rows in requests for keep,_ in rows})
    active=set(range(len(profiles)))
    waves=[]
    while active:
        offers={(keep,fingerprints(key,keep)) for index in active for key in (profile_key(profiles[index]),reverse(profile_key(profiles[index]))) for keep in keeps}
        deleted={index for index in active if requests[index]-offers}
        if not deleted:
            break
        waves.append(sorted(deleted))
        active.difference_update(deleted)
    return active,waves


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source',type=Path)
    parser.add_argument('--out',type=Path)
    args=parser.parse_args()
    profiles=list(read_profiles(args.source))
    remaining,waves=fixed_point(profiles)
    if args.out:
        original=args.source.read_text().splitlines()
        args.out.write_text(''.join(original[index]+'\n' for index in sorted(remaining)))
    print('active',len(remaining),'removed indices by wave',waves)
