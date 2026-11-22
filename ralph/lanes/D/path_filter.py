"""Force/forbid exterior pairs by eight-star incidence and a global path cap."""

import argparse
from collections import Counter
from itertools import combinations
import json

from path_growth import (ROOT, Path, bits, check, core_instances, decode, fixed_graph,
                         independent_path_max, neighbors, pairs, path_lengths, read_profiles)


def trial(graph, src, dst, cap):
    choice = (1 << src) | (1 << dst)
    if graph[src] & graph[dst]:
        return 'triangle'
    if any((graph[vertex] & graph[other]).bit_count() >= 3
           for vertex, partner in ((src, dst), (dst, src)) for other in bits(graph[partner])):
        return 'codegree'
    graph[src] |= 1 << dst
    graph[dst] |= 1 << src
    long = path_lengths(graph) > cap
    graph[src] ^= 1 << dst
    graph[dst] ^= 1 << src
    return 'path' if long else ''


def arc_support(graph, degree, cap):
    work = list(graph)
    order = len(work)
    possible = [row if vertex < 8 else row | (((1 << order) - 256) ^ (1 << vertex)) for vertex, row in enumerate(work)]
    while True:
        if any(row.bit_count() > degree for row in work):
            return 'forced-degree', possible
        if path_lengths(work) > cap:
            return 'long', possible
        for src, dst in pairs(range(8, order)):
            if not ((possible[src] ^ work[src]) >> dst & 1):
                continue
            if work[src].bit_count() == degree or work[dst].bit_count() == degree or trial(work, src, dst, cap):
                possible[src] ^= 1 << dst
                possible[dst] ^= 1 << src
        changes = set()
        for vertex, row in enumerate(possible):
            if row.bit_count() < degree:
                return f'short-degree:{vertex}', possible
            if row.bit_count() == degree:
                changes.update(tuple(sorted((vertex, other))) for other in bits(row ^ work[vertex]))
        for src, dst in pairs(range(order)):
            if possible[src] >> dst & 1:
                continue
            common = possible[src] & possible[dst]
            if not common:
                return f'undominated:{src}:{dst}', possible
            if common.bit_count() == 1:
                pivot = common.bit_length() - 1
                changes.update(tuple(sorted((vertex, pivot))) for vertex in (src, dst) if not work[vertex] >> pivot & 1)
        if not changes:
            return 'open', possible
        for src, dst in sorted(changes):
            if trial(work, src, dst, cap):
                return 'incompatible-forced-arcs', possible
            work[src] |= 1 << dst
            work[dst] |= 1 << src


def controls():
    total = 0
    for line in (ROOT / 'gluing/val/r3_7_22.g6').read_text().splitlines():
        adj = neighbors(22, decode(line))
        if {len(row) for row in adj} != {6} or max(len(left & right) for left, right in pairs(adj)) > 3:
            continue
        maximum = independent_path_max(adj)
        for cycle, core in core_instances(adj):
            outer = sorted(set(range(22)) - set(core), key=lambda vertex: (sum(1 << index for index, anchor in enumerate(core) if anchor in adj[vertex]), vertex))
            profile = Counter(sum(1 << index for index, anchor in enumerate(core) if anchor in adj[vertex]) for vertex in outer)
            graph = fixed_graph(profile, cycle)
            result, possible = arc_support(graph, 6, maximum)
            vertices = core + outer
            assert result == 'open' and all(possible[src] >> dst & 1 for src, dst in pairs(range(22)) if vertices[dst] in adj[vertices[src]])
            total += 1
    assert total == 239
    print('PASS all 239 planted C22 completions with true max; every edge retained', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    controls()
    counts = Counter()
    with args.out.open('w') as output:
        for index, profile in enumerate(read_profiles(args.source)):
            graph = fixed_graph(profile)
            if path_lengths(graph) > 6:
                continue
            result, possible = arc_support(graph, 9, 6)
            counts[result.split(':')[0]] += 1
            print(json.dumps([index, result, possible]), file=output)
    print('max6 survivors pass:', dict(counts), flush=True)
