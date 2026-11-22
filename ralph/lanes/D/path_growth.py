"""Lower bounds on simple paths in edge kernels from eight pinned stars."""

import argparse
from collections import Counter
from itertools import combinations
from pathlib import Path

from punct_path import ROOT, core_instances, decode, neighbors, pairs, profile_key, template


def bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def fixed_graph(profile, cycle=False):
    masks = [mask for mask, size in sorted(profile.items()) for _ in range(size)]
    graph = [sum(1 << other for other in row) for row in template(cycle)] + masks
    for vertex, mask in enumerate(masks, 8):
        for anchor in bits(mask):
            graph[anchor] |= 1 << vertex
    return graph


def path_lengths(graph):
    maximum = 0
    for first, row in enumerate(graph):
        for second in bits(row & ~((2 << first) - 1)):
            remain = (row ^ (1 << second)) | (graph[second] ^ (1 << first))
            if remain.bit_count() <= maximum:
                continue
            while remain:
                search = remain & -remain
                found = search
                while search:
                    nxt = 0
                    for vertex in bits(search):
                        nxt |= graph[vertex]
                    search = nxt & remain & ~found
                    found |= search
                maximum = max(maximum, found.bit_count())
                remain ^= found
    return maximum


def independent_path_max(adj):
    maximum = 0
    for first, row in enumerate(adj):
        for second in row:
            if first >= second:
                continue
            kernel = (row - {second}) | (adj[second] - {first})
            walks = [(vertex,) for vertex in kernel]
            while walks:
                maximum = max(maximum, len(walks[0]))
                walks = [path + (other,) for path in walks for other in adj[path[-1]].intersection(kernel).difference(path)]
    return maximum


def check():
    checks = Counter()
    for line in (ROOT / 'gluing/val/r3_7_22.g6').read_text().splitlines():
        adj = neighbors(22, decode(line))
        if {len(row) for row in adj} != {6} or max(len(left & right) for left, right in pairs(adj)) > 3:
            continue
        actual = independent_path_max(adj)
        for cycle, core in core_instances(adj):
            profile = Counter(sum(1 << index for index, anchor in enumerate(core) if anchor in adj[vertex])
                              for vertex in set(range(22)) - set(core))
            graph = fixed_graph(profile, cycle)
            lower = path_lengths(graph)
            partial = [row & set(core) if vertex not in core else row for vertex, row in enumerate(adj)]
            assert lower == independent_path_max(partial) <= actual
            checks[lower, actual] += 1
    assert sum(checks.values()) == 239
    print('PASS 239 planted fixed-star bounds vs independent simple-path DFS; (bound, true max)', sorted(checks.items()), flush=True)


def read_profiles(path):
    for line in path.read_text().splitlines():
        yield dict(tuple(map(int, term.split(':'))) for term in line.split())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    check()
    hist = Counter()
    with args.out.open('w') as output:
        for index, profile in enumerate(read_profiles(args.source)):
            graph = fixed_graph(profile)
            if max((left & right).bit_count() for left, right in pairs(graph)) > 3:
                hist['cap fail'] += 1
                print(index, 'cap', file=output)
                continue
            longest = path_lengths(graph)
            hist[longest] += 1
            print(index, longest, file=output)
    print('all', dict(hist))
