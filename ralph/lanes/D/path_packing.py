"""Verify short diamonds and the four profile hole codegrees separately."""

from collections import Counter
from itertools import combinations
from pathlib import Path
from pysat.solvers import Cadical195

from path_growth import ROOT, bits, fixed_graph, pairs, read_profiles
from path_reroot import core_instances, decode, neighbors


def check_stars():
    counts = Counter()
    for line in (ROOT / 'duo/reg6_22.g6').read_text().splitlines():
        adj = neighbors(22, decode(line))
        if max(len(left & right) for left, right in pairs(adj)) > 3:
            continue
        for root in range(22):
            hood = adj[root]
            largest = 0
            cyclic = False
            for center in hood:
                kernel = (hood | adj[center]) - {root, center}
                remain = set(kernel)
                while remain:
                    found = {min(remain)}
                    todo = list(found)
                    while todo:
                        vertex = todo.pop()
                        extra = (adj[vertex] & kernel) - found
                        found.update(extra)
                        todo.extend(extra)
                    largest = max(largest, len(found))
                    cyclic |= all(len(adj[vertex] & found) == 2 for vertex in found)
                    remain -= found
            if largest > 6 or cyclic:
                continue
            counts['short'] += 1
            supports = [row & hood for vertex, row in enumerate(adj) if vertex not in hood and vertex != root]
            triples = [mask for mask in supports if len(mask) == 3]
            for mask in triples:
                assert sum(len(mask & other) == 2 for other in triples if other != mask) <= 1
            repeated = sum(len(mask & other) == 2 for mask, other in pairs(triples))
            slots = {tuple(sorted(edge)) for mask in triples for edge in pairs(mask)}
            assert len(slots) == 3 * len(triples) - repeated and 2 * repeated <= len(triples)
            assert len(triples) <= len(hood) * (len(hood) - 1) // 5
            counts['diamonds'] += repeated
    assert counts['short'] and counts['diamonds']
    print('PASS C22 local short-star packing', dict(counts))


def control_hole():
    profiles = list(read_profiles(Path('path.tsv')))
    for index in (2298, 2386, 2424, 2431):
        graph = fixed_graph(profiles[index])
        for root, other in [(0, 4), (4, 0)]:
            half = list(bits(graph[root] & 255 & ~(1 << other)))
            right = list(bits(graph[other] & 255 & ~(1 << root)))
            endpoints = [vertex for vertex in half if sum((graph[vertex] >> member) & 1 for member in right) == 1]
            assert len(endpoints) == 1
            start = endpoints[0]
            path = [start]
            while len(path) < 6:
                nxt, = [vertex for vertex in half + right if vertex not in path and graph[path[-1]] >> vertex & 1]
                path.append(nxt)
            assert (graph[path[0]] & graph[path[4]]).bit_count() == 3
    print('PASS directly traced eight oriented target holes, all high (conditional on four-profile cover)')


if __name__ == '__main__':
    check_stars()
    control_hole()
