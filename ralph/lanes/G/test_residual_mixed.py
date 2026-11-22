#!/usr/bin/env python3
"""Independent set-valued controls for the shared support projection."""

from argparse import ArgumentParser
from collections import Counter
from itertools import combinations, permutations, product
from pathlib import Path

from pysat.solvers import Cadical195

from check_root_cover import graph, vertices
from mixed_strip_completion import instance
from residual_mixed_joint import parse


def order_analogue(path):
    for line in path.read_text().splitlines():
        adj = [set(vertices(mask)) for mask in graph.parse_graph6(line)]
        cap, ramsey = {13: (4, 3), 35: (8, 18), 39: (9, 23)}[len(adj)]
        assert graph.triangle_free(graph.parse_graph6(line)) and graph.alpha(graph.parse_graph6(line)) == cap
        pairs = 0
        full_edges = sum(map(len, adj)) // 2
        for first, second in combinations(range(len(adj)), 2):
            if second in adj[first]:
                continue
            deleted = {first, second} | adj[first] | adj[second]
            kept = set(range(len(adj))) - deleted
            exclusive_a, exclusive_b = adj[first] - adj[second], adj[second] - adj[first]
            cross_edges = sum(len(adj[vertex] & exclusive_b) for vertex in exclusive_a)
            window_edges = sum(len(adj[vertex] & kept) for vertex in kept) // 2
            assert window_edges == full_edges - sum(len(adj[vertex]) for vertex in adj[first] | adj[second]) + cross_edges
            for vertex in kept:
                degree = len(adj[vertex] & kept)
                assert degree == len(adj[vertex]) - len(adj[vertex] & adj[first]) - len(adj[vertex] & adj[second]) + len(adj[vertex] & adj[first] & adj[second])
                assert len(kept) - ramsey <= degree <= cap - 2
            pairs += 1
        print('n-analogue', len(adj), pairs)


def side_placements(keep, side, pivot, own, other, holes):
    universe = Counter({frozenset((anchor,)): 4 for anchor in side})
    universe.update(frozenset(pair) for pair in combinations(side, 2) if frozenset(pair) not in holes)
    found = Counter(keep.values())
    assert not (found - universe)
    missing = (universe - found)
    intact = sorted((tuple(sorted(subset)) for subset in missing.elements() if pivot not in subset))
    assert len(intact) == len(other)
    additions = {vertex: frozenset(subset) for vertex, subset in zip(other, intact, strict=True)}
    variable = tuple(next(iter(subset - {pivot})) for subset in missing if pivot in subset and len(subset) == 2)
    assert len(own) == 4 + len(variable)
    for placement in permutations(own, len(variable)):
        doubles = dict(zip(placement, variable, strict=True))
        yield keep | additions | {vertex: frozenset((pivot, doubles[vertex])) if vertex in doubles
                                  else frozenset((pivot,)) for vertex in own}


def witness(row, joint):
    key, spec = parse(row)
    line, mask_a, mask_b, _, hole_first, hole_second, peer, _, *peer_right = spec
    adj = graph.parse_graph6(line)
    count = len(adj)
    first, second = tuple(vertices(mask_a)), tuple(vertices(mask_b))
    cross, = tuple((left, right) for left, right in product(first, second) if adj[left] >> right & 1)
    center, pivot = count + 2, count + 3
    side_a, side_b = (*first, center), (*second, pivot)
    keep = tuple(sorted(set(range(count)) - set(first) - set(second)))
    shared = count - (22 if peer_right else 23)
    common = tuple(range(count + 4, count + 4 + shared))
    only_a = tuple(range(count + 4 + shared, count + 10))
    only_b = tuple(range(count + 10, 40))
    outside = (*keep, *common, *only_a, *only_b)
    cut_a = set((*common, *only_a))
    holes_b = {frozenset((hole_first, hole_second)), frozenset((peer, peer_right[0] if peer_right else pivot))}
    kept_a = {vertex: frozenset(neighbor for neighbor in first if adj[vertex] >> neighbor & 1) for vertex in keep}
    kept_b = {vertex: frozenset(neighbor for neighbor in second if adj[vertex] >> neighbor & 1) for vertex in keep}
    candidates_a = []
    for leaf in set(first) - {cross[0]}:
        holes_a = {frozenset((cross[0], center)), frozenset((leaf, center))}
        candidates_a.extend(side_placements(kept_a, side_a, center, (*common, *only_a), only_b, holes_a))
    rows = Counter()
    for supports_b in side_placements(kept_b, side_b, pivot, (*common, *only_b), only_a, holes_b):
        rows['B'] += 1
        anchor_b = {anchor: {vertex for vertex in outside if anchor in supports_b[vertex]} for anchor in side_b}
        if any(not (cut_a & branch) for branch in anchor_b.values()):
            continue
        if any(cross[0] in candidates_a[0][vertex] for vertex in only_b if vertex in anchor_b[cross[1]]):
            continue
        rows['single B'] += 1
        if joint:
            good = False
            for branch in side_b:
                if branch == cross[1]:
                    continue
                size = len(anchor_b[branch]) + 1
                overlap = len(cut_a & anchor_b[branch])
                if not 1 <= overlap <= size - 5:
                    break
                remain = set(outside) - cut_a - anchor_b[branch]
                minimum = 4 if (size, overlap) == (8, 3) else max(0, 8 + len(remain) - 23)
                retained_a = [len({vertex for vertex in remain if anchor in candidates_a[0][vertex]}) + int(anchor == cross[0])
                              for anchor in first]
                retained_b = [len(anchor_b[anchor] & remain) + int(anchor == cross[1])
                              for anchor in side_b if anchor != branch]
                if not all(minimum <= value <= 7 for value in kept_degrees(retained_a, retained_b)):
                    break
            else:
                good = True
                rows['joint B'] += 1
            if not good:
                continue
        for supports_a in candidates_a:
            anchor_a = {anchor: {vertex for vertex in outside if anchor in supports_a[vertex]} for anchor in side_a}
            if any(not (anchor_a[anchor] & anchor_b[pivot]) for anchor in side_a):
                continue
            if joint and any(not (anchor_a[left] & anchor_b[right]) for left, right in product(side_a, side_b)
                             if (left, right) != cross):
                continue
            return key, rows, (supports_a, supports_b)
    return key, rows, None


def kept_degrees(first, second):
    assert len(first) == len(second) == 4
    return (*first, *second)


def check_plant(row, selected):
    key, spec = parse(row)
    problem, metadata = instance(*spec, residual=True, attachment='joint')
    sides, stars, pivots, exterior, _, __ = metadata
    assumptions = [problem.edgeof(anchor, vertex) * (1 if anchor in supports[vertex] else -1)
                   for supports, side in zip(selected, sides, strict=True) for vertex in exterior for anchor in side]
    with Cadical195(bootstrap_with=problem.formula.clauses) as solver:
        assert solver.solve(assumptions=assumptions)
    graph_order = len(graph.parse_graph6(spec[0]))
    skeleton = [set() for _ in range(40)]
    for vertex, neighbors in enumerate(graph.parse_graph6(spec[0])):
        skeleton[vertex].update(vertices(neighbors))
    for index, side in enumerate(sides):
        for vertex in (graph_order + 1 - index, *side):
            skeleton[graph_order + index].add(vertex)
            skeleton[vertex].add(graph_order + index)
        for vertex, anchors in selected[index].items():
            for anchor in anchors:
                skeleton[vertex].add(anchor)
                skeleton[anchor].add(vertex)
    assert all(not skeleton[vertex] & skeleton[other] for vertex in range(40) for other in skeleton[vertex])
    hand_window = set(range(40)) - set(pivots) - skeleton[pivots[0]] - skeleton[pivots[1]]
    assert hand_window == set(range(graph_order))
    assert stars[1] in skeleton[stars[0]]
    for expected, pivot in zip((7, 9 if len(spec) == 9 else 8), pivots, strict=True):
        assert len(skeleton[pivot]) == expected
    print('PLANTED', key, tuple(sorted((vertex, tuple(sorted(support))) for vertex, support in side.items()) for side in selected))


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('controls', type=Path)
    parser.add_argument('positive', type=Path)
    parser.add_argument('negative', type=Path)
    args = parser.parse_args()
    order_analogue(args.controls)
    positive = args.positive.read_text().splitlines()[0]
    negative, = args.negative.read_text().splitlines()
    key, rows, selected = witness(positive, joint=True)
    assert selected is not None
    print('oracle possible', key, dict(rows))
    check_plant(positive, selected)
    key, rows, selected = witness(negative, joint=False)
    assert selected is not None
    print('oracle single possible', key, dict(rows))
    key, rows, selected = witness(negative, joint=True)
    assert selected is None and rows['joint B'] == 0
    print('oracle joint incompatible', key, dict(rows))


if __name__ == '__main__':
    main()
