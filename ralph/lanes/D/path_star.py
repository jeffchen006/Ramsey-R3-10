"""Unlabelled exact row extension of an eight-anchor P6 profile."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
import sys
import time

from path_growth import bits, fixed_graph, pairs, path_lengths, read_profiles
from path_overlap import Library, optimistic
from path_reroot import ROOT, core_instances, decode, neighbors, orientations, placements, profile_key


def extensions(graph, pivot, degree):
    cells = defaultdict(list)
    for vertex in range(8, len(graph)):
        if vertex != pivot and not graph[vertex] & graph[pivot]:
            cells[graph[vertex]].append(vertex)
    groups = sorted(cells.items(), key=lambda item: (-item[0].bit_count(), item[0]))
    totals = [(graph[pivot] & graph[anchor]).bit_count() for anchor in range(8)]
    def search(index, need, selection):
        if not need:
            if all(graph[pivot] >> anchor & 1 or total >= 1 for anchor, total in enumerate(totals)):
                yield selection
            return
        if index == len(groups) or sum(len(vertices) for _, vertices in groups[index:]) < need:
            return
        mask, vertices = groups[index]
        anchors = list(bits(mask))
        room = min([need, len(vertices)] + [3 - totals[anchor] for anchor in anchors])
        for count in range(room + 1):
            for anchor in anchors:
                totals[anchor] += count
            yield from search(index + 1, need - count, selection | sum(1 << vertex for vertex in vertices[:count]))
            for anchor in anchors:
                totals[anchor] -= count
    yield from search(0, degree - graph[pivot].bit_count(), 0)


def overlay(graph, pivot, add, degree, path_cap, library):
    work = list(graph)
    work[pivot] |= add
    for vertex in bits(add):
        work[vertex] |= 1 << pivot
    if any((left & right).bit_count() > 3 for left, right in pairs(work)):
        return 'cap'
    if path_lengths(work) > path_cap:
        return 'path'
    upper = optimistic(work, degree)
    for core in placements(work):
        if not library.supports(work, upper, core, extra=pivot):
            return 'overlap'
    return 'ok'


def calibration():
    samples = {}
    for line in (ROOT / 'gluing/val/r3_7_22.g6').read_text().splitlines():
        adj = neighbors(22, decode(line))
        if {len(row) for row in adj} != {6} or max(len(left & right) for left, right in pairs(adj)) > 3:
            continue
        for cycle, core in core_instances(adj):
            assert not cycle
            mask = lambda vertex: sum(1 << index for index, anchor in enumerate(core) if anchor in adj[vertex])
            outer = sorted(set(range(22)) - set(core), key=lambda vertex: (mask(vertex), vertex))
            order = core + outer
            samples.setdefault(profile_key(Counter(map(mask, outer))), [sum(1 << index for index, other in enumerate(order) if other in adj[vertex]) for vertex in order])
    lib = Library([dict(key) for key in samples])
    total = 0
    for key, planted in samples.items():
        graph = fixed_graph(dict(key))
        for pivot in range(8, len(graph)):
            want = planted[pivot] & ~255
            counts = Counter(graph[vertex] for vertex in bits(want))
            found = False
            for add in extensions(graph, pivot, 6):
                if Counter(graph[vertex] for vertex in bits(add)) == counts:
                    found = True
                    assert overlay(graph, pivot, add, 6, 8, lib) == 'ok'
                    break
            assert found
            total += 1
    print('PASS', total, 'planted star rows with normalized cell counts; every P6 compatible', flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--root', type=int)
    parser.add_argument('--library', nargs='*', type=int)
    args = parser.parse_args()
    if args.root is None:
        calibration()
        sys.exit()
    profiles = list(read_profiles(args.source))
    lib = Library([profiles[index] for index in args.library])
    graph = fixed_graph(profiles[args.root])
    pivots = {mask: graph.index(mask, 8) for mask in graph[8:]}
    ordered = sorted((sum(1 for _ in extensions(graph, pivot, 9)), mask, pivot) for mask, pivot in pivots.items())
    for size, mask, pivot in ordered:
        start = time.process_time()
        counts = Counter()
        for add in extensions(graph, pivot, 9):
            verdict = overlay(graph, pivot, add, 9, 6, lib)
            counts[verdict] += 1
            if verdict == 'ok':
                break
        print(args.root, mask, size, dict(counts), round(time.process_time() - start, 3), flush=True)
        if not counts['ok']:
            assert sum(counts.values()) == size
            print('EXHAUSTED', args.root, mask, flush=True)
            break
    else:
        print('OPEN', args.root, flush=True)
